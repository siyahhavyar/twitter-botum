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

HORDE_KEY = os.getenv("HORDE_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.")
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)")

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
        "Hyper-Realistic Cyberpunk City Vertical",
        "Majestic Fantasy Landscape Vertical",
        "Cinematic Sci-Fi Space Station Portrait",
        "Mystical Ancient Ruins Tall",
        "Vaporwave Sunset Highway Phone Wallpaper",
        "Dark Gothic Castle Vertical",
        "Neon Noir Detective Street Tall"
    ]

    theme = random.choice(themes)

    prompt = f"""
    Write a highly detailed image prompt for an AI based on: {theme}.
    IMPORTANT: The image will be a vertical phone wallpaper.
    Focus on vertical composition, tall structures, and depth.
    Return exactly two lines:
    PROMPT: <english detailed description>
    CAPTION: <short tweet caption>
    """
    
    try:
        text = model.generate_content(prompt).text
        parts = text.split("CAPTION:")
        
        if len(parts) < 2:
            return f"{theme}, 8k, masterpiece", f"{theme} #AIArt"

        img_prompt = parts[0].replace("PROMPT:", "").strip()
        caption = parts[1].strip()
        
        # Dikey kompozisyonu güçlendiren kelimeler ekledim
        final_prompt = (
            f"{img_prompt}, "
            "vertical aspect ratio, tall composition, looking up, "
            "masterpiece, best quality, ultra-detailed, 8k resolution, "
            "sharp focus, ray tracing, unreal engine 5, cinematic lighting, "
            "photorealistic, intricate details, clean lines"
        )
        return final_prompt, caption
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return f"High quality {theme}", f"{theme} #AI"


# -----------------------------
# 2. AI HORDE (9:16 TELEFON MODU)
# -----------------------------
def generate_image_horde(prompt_text):
    print("AI Horde → 9:16 Wallpaper isteği gönderiliyor...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v2.2-PhoneWait"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            # --- DEĞİŞİKLİK BURADA ---
            # Eski: 832x1216 (Biraz genişti)
            # Yeni: 768x1344 (Tam İnce Uzun Telefon Formatı)
            "width": 768,                 
            "height": 1344,               
            "steps": 35,                  
            "post_processing": ["RealESRGAN_x4plus"] 
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["Juggernaut XL", "AlbedoBase XL (SDXL)", "SDXL_beta"] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers)
        
        if req.status_code != 202:
            print(f"Horde Sunucu Hatası: {req.text}")
            return None
            
        task_id = req.json()['id']
        print(f"Görev ID: {task_id}. Sırada bekleniyor...")
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return None

    # Bekleme (60 Dk - İnatçı Mod)
    wait_time = 0
    max_wait = 3600 
    
    while wait_time < max_wait:
        time.sleep(20) 
        wait_time += 20
        
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url)
            status_data = check.json()
            
            if status_data['done']:
                print("İşlem tamamlandı! Wallpaper indiriliyor...")
                generations = status_data['generations']
                if len(generations) > 0:
                    img_url = generations[0]['img']
                    return requests.get(img_url).content
                else:
                    print("Horde boş yanıt döndü.")
                    return None
            
            wait_t = status_data.get('wait_time', '?')
            queue = status_data.get('queue_position', '?')
            print(f"Geçen: {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn")
            
        except Exception as e:
            print(f"Kontrol hatası: {e}")
            time.sleep(5) 

    print("Zaman aşımı (60 dk).")
    return None


# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
    filename = "wallpaper_mobile.png"
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
            text=caption + " #AIArt #PhoneWallpaper #4K",
            media_ids=[media.media_id]
        )
        print("✅ TWEET BAŞARIYLA ATILDI!")
        return True 
        
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN (SONSUZ DÖNGÜ)
# -----------------------------
if __name__ == "__main__":
    print("Bot Başlatılıyor... Telefon formatında resim üretilecek.")
    
    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n=== DENEME {deneme_sayisi} BAŞLIYOR ===")
        
        try:
            prompt, caption = generate_prompt_caption()
            print("Prompt:", prompt)
            
            img = generate_image_horde(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 İşlem tamam. Bot dinlenmeye geçiyor.")
                else:
                    print("⚠️ Tweet hatası. Tekrar deneniyor...")
            else:
                print("⚠️ Resim hatası. Tekrar deneniyor...")
                
        except Exception as e:
            print(f"⚠️ Beklenmeyen hata: {e}")
        
        if not basari:
            print("⏳ 1 Dakika mola...")
            time.sleep(60)
            deneme_sayisi += 1
