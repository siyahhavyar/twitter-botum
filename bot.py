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

# SİZİN TANIMLADIĞINIZ İSİM: HORDE_API_KEY
HORDE_KEY = os.getenv("HORDE_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: HORDE_API_KEY bulunamadı! Anonim mod (Yavaş) devreye giriyor.")
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Kullanıcı API Key algılandı! ({HORDE_KEY[:4]}***)")

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
            return f"{theme}, cinematic lighting, 8k", f"{theme} #AIArt"

        img_prompt = parts[0].replace("PROMPT:", "").strip()
        caption = parts[1].strip()
        
        final_prompt = f"{img_prompt}, masterpiece, best quality, ultra detailed, 8k, cinematic lighting"
        return final_prompt, caption
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return f"A beautiful {theme}", f"{theme} #AI"


# -----------------------------
# 2. AI HORDE (GARANTİCİ MOD - ÇOKLU MODEL)
# -----------------------------
def generate_image_horde(prompt_text):
    print("AI Horde → İstek gönderiliyor (Üyelik Modu)...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v1.0"
    }
    
    # --- MODEL GÜNCELLEMESİ ---
    # Tek bir modele bağlı kalmak yerine, en iyi 3 modeli listeledik.
    # Sistem ilkini bulamazsa otomatik olarak ikincisini dener.
    # 1. Juggernaut XL: Çok popüler ve gerçekçi SDXL modeli
    # 2. AlbedoBase XL: Harika renkler ve detaylar
    # 3. SDXL_beta: Standart Stability AI modeli
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_euler",
            "cfg_scale": 7,
            "width": 576,    
            "height": 1024,  
            "steps": 30,
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": [
            "Juggernaut XL", 
            "AlbedoBase XL (SDXL)", 
            "SDXL_beta"
        ] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers)
        
        # Eğer yine sunucu hatası alırsak loglayalım
        if req.status_code != 202:
            print(f"Horde Sunucu Hatası: {req.text}")
            return None
            
        task_id = req.json()['id']
        print(f"Görev ID: {task_id}. İşleniyor...")
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return None

    # Bekleme
    wait_time = 0
    max_wait = 600 # 10 Dakika
    
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
                    print("Horde resim üretmedi.")
                    return None
            
            # Kuyruk bilgisi
            queue_pos = status_data.get('queue_position', '?')
            wait_t = status_data.get('wait_time', '?')
            print(f"Süre: {wait_time}sn | Sıra: {queue_pos} | Tahmini: {wait_t}sn")
            
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
            text=caption + " #AIArt #SDXL #Wallpaper",
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
