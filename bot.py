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
    print("UYARI: Key yok, Anonim mod. (Öncelik düşük)")
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
        "Hyper-Realistic Cyberpunk City",
        "Majestic Fantasy Landscape",
        "Cinematic Sci-Fi Space Station",
        "Mystical Ancient Ruins",
        "Vaporwave Sunset Highway",
        "Dark Gothic Castle",
        "Neon Noir Detective Street",
        "Post-Apocalyptic Nature Takeover"
    ]

    theme = random.choice(themes)

    prompt = f"""
    Write a highly detailed image prompt for an AI based on: {theme}.
    Focus on lighting, texture, and realism.
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
        
        # Kalite artırıcı eklemeler
        final_prompt = (
            f"{img_prompt}, "
            "masterpiece, best quality, ultra-detailed, 8k resolution, "
            "sharp focus, ray tracing, unreal engine 5, cinematic lighting, "
            "photorealistic, intricate details, clean lines"
        )
        return final_prompt, caption
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        # Hata durumunda basit prompt döndür
        return f"High quality {theme}", f"{theme} #AI"


# -----------------------------
# 2. AI HORDE (HD & UZUN BEKLEMELİ)
# -----------------------------
def generate_image_horde(prompt_text):
    print("AI Horde → HD Görsel isteği gönderiliyor...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v2.1-Persistent"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 832,                 
            "height": 1216,               
            "steps": 35,                  
            "post_processing": ["RealESRGAN_x4plus"] # Upscaling (Kalite)
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

    # --- DEĞİŞİKLİK: BEKLEME SÜRESİ UZATILDI ---
    wait_time = 0
    max_wait = 3600 # 60 Dakika (Sıra 75'teyken kesilmesin diye)
    
    while wait_time < max_wait:
        time.sleep(20) # 20 saniyede bir kontrol
        wait_time += 20
        
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url)
            status_data = check.json()
            
            if status_data['done']:
                print("İşlem tamamlandı! HD Resim indiriliyor...")
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
            # Ufak bağlantı kopmalarında döngüyü kırma, devam et
            print(f"Kontrol hatası (önemsiz): {e}")
            time.sleep(5) 

    print("Bu deneme için zaman aşımı (60 dk) doldu.")
    return None


# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
    filename = "wallpaper_hd.png"
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
            text=caption + " #AIArt #4K #Wallpaper",
            media_ids=[media.media_id]
        )
        print("✅ TWEET BAŞARIYLA ATILDI!")
        return True # Başarılı olduğunu bildir
        
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        return False # Başarısız
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN (İNATÇI MOD / RETRY LOOP)
# -----------------------------
if __name__ == "__main__":
    print("Bot Başlatılıyor... Paylaşım yapılana kadar durmayacak.")
    
    basari = False
    deneme_sayisi = 1
    
    # Sonsuz döngü (Başarılı olana kadar)
    while not basari:
        print(f"\n=== DENEME {deneme_sayisi} BAŞLIYOR ===")
        
        try:
            # 1. Prompt Oluştur
            prompt, caption = generate_prompt_caption()
            print("Prompt:", prompt)
            
            # 2. Resim Oluştur (Horde)
            img = generate_image_horde(prompt)
            
            if img:
                # 3. Tweet At
                if post_to_twitter(img, caption):
                    basari = True # Döngüden çıkış bileti
                    print("🎉 İşlem başarıyla tamamlandı. Bot kapanıyor.")
                else:
                    print("⚠️ Resim oluştu ama Twitter'a atılamadı. Tekrar deneniyor...")
            else:
                print("⚠️ Resim oluşturulamadı (Zaman aşımı veya Hata). Tekrar deneniyor...")
                
        except Exception as e:
            print(f"⚠️ Beklenmeyen genel hata: {e}")
        
        if not basari:
            print("⏳ 1 Dakika dinlenip tekrar deniyoruz...")
            time.sleep(60) # Sunucuları spamlamamak için 1 dk mola
            deneme_sayisi += 1
            
