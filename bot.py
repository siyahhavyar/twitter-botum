import os
import time
import requests
import random
import tweepy
import google.generativeai as genai

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")

# Horde Key
HORDE_KEY = os.getenv("HORDE_KEY")
if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("Bilgi: Anonim mod (0000000000) kullanılıyor.")
    HORDE_KEY = "0000000000"

if not GEMINI_KEY:
    print("ERROR: GEMINI_KEY eksik!")
    exit(1)

# -----------------------------
# 1. GEMINI PROMPT GENERATOR
# -----------------------------
def generate_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    themes = [
        "Cyberpunk City Rain",
        "Ethereal Forest Magic",
        "Space Colony on Mars",
        "Underwater Ancient Ruins",
        "Vaporwave Sunset Road",
        "Gothic Vampire Castle",
        "Futuristic Neon Street"
    ]

    theme = random.choice(themes)

    prompt = f"""
    Write a prompt for an AI image generator based on this theme: {theme}.
    Return exactly two lines:
    PROMPT: <english detailed description>
    CAPTION: <short tweet caption>
    """
    
    try:
        text = model.generate_content(prompt).text
        parts = text.split("CAPTION:")
        
        if len(parts) < 2:
            return f"{theme}, cinematic lighting, realistic", f"{theme} #AIArt"

        img_prompt = parts[0].replace("PROMPT:", "").strip()
        caption = parts[1].strip()
        
        # Gerçekçilik ve kalite için eklemeler
        final_prompt = f"{img_prompt}, (photorealistic:1.4), raw photo, dslr, soft lighting, high quality, 8k, masterpiece"
        
        return final_prompt, caption
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return f"A beautiful {theme}", f"{theme} #AI"


# -----------------------------
# 2. AI HORDE (CORRECTED RESOLUTION)
# -----------------------------
def generate_image_horde(prompt_text):
    print("AI Horde → İstek gönderiliyor...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v1.0"
    }
    
    # --- MATEMATİKSEL DÜZELTME ---
    # Kurallar: 
    # 1. Sayılar 64'ün katı olmalı (Örn: 448/64 = 7 tam sayı)
    # 2. Toplam piksel anonim limiti (331.776) geçmemeli.
    # 448 x 704 = 315.392 piksel (Limitin altında ve kurallara uygun)
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7,
            "width": 448,   
            "height": 704,  
            "steps": 25,
        },
        "nsfw": False,
        "censor_nsfw": True,
        # ICBINP daha gerçekçi sonuç verir, yedek olarak stable_diffusion ekledik
        "models": ["ICBINP", "stable_diffusion"] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers)
        
        if req.status_code != 202:
            print(f"Horde Hata: {req.text}")
            return None
            
        task_id = req.json()['id']
        print(f"Görev ID: {task_id}. Bekleniyor...")
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return None

    # Bekleme
    wait_time = 0
    max_wait = 300
    
    while wait_time < max_wait:
        time.sleep(10)
        wait_time += 10
        
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url)
            status_data = check.json()
            
            if status_data['done']:
                print("İşlem tamamlandı! Resim iniyor...")
                generations = status_data['generations']
                if len(generations) > 0:
                    img_url = generations[0]['img']
                    return requests.get(img_url).content
                else:
                    print("Horde resim üretmedi (Liste boş).")
                    return None
            
            print(f"Süre: {wait_time}sn | Durum: {status_data.get('wait_time', 'Sıra bekleniyor')}sn...")
        except Exception as e:
            time.sleep(5) 

    print("Zaman aşımı.")
    return None


# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
    filename = "wallpaper.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    try:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )

        client.create_tweet(
            text=caption + " #AIArt #Wallpaper #Dreamy",
            media_ids=[media.media_id]
        )
        print("TWEET BAŞARILI!")
        
    except Exception as e:
        print(f"Twitter Hatası: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    prompt, caption = generate_prompt_caption()
    print("Prompt:", prompt)
    
    img = generate_image_horde(prompt)
    
    if img:
        post_to_twitter(img, caption)
    else:
        print("Resim oluşturulamadı.")
