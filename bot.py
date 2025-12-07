import os
import time
import requests
import tweepy
import random
import google.generativeai as genai
from datetime import datetime

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
HORDE_KEY     = os.getenv("HORDE_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

if not GEMINI_KEY:
    print("ERROR: GEMINI_KEY eksik!", flush=True)
    exit(1)

# -----------------------------
# 1. GEMINI (2.0 FLASH) - FİKİR BABASI
# -----------------------------
def get_idea_from_gemini():
    """
    Gemini 2.0 Flash modelini kullanır.
    Sadece 1 kez çalışır, bu yüzden kota doldurmaz.
    """
    genai.configure(api_key=GEMINI_KEY)
    
    generation_config = genai.types.GenerationConfig(
        temperature=1.1, # Yüksek yaratıcılık
        top_p=0.95,
        top_k=40,
    )
    
    # --- İSTEDİĞİN GİBİ 2.0 MODELİNE DÖNDÜK ---
    model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)

    while True:
        try:
            print("🧠 Gemini (2.0 Flash) yeni bir sanat eseri düşünüyor...", flush=True)
            
            # Zaman damgası ekleyerek her seferinde farklı hissetmesini sağlıyoruz
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            prompt = f"""
            Current Time: {current_time}
            Act as an avant-garde AI Art Curator. 
            You must create a concept that is COMPLETELY DIFFERENT from generic AI art.
            
            INSTRUCTIONS:
            1. Pick a very specific, random Art Style (e.g. Bauhaus, Ukiyo-e, Glitch Art, Renaissance, Synthwave, Minimalism).
            2. Pick a very specific, random Subject.
            3. Combine them. Be unpredictable.

            CRITICAL RULES:
            - NO HORROR, NO GORE, NO NSFW.
            - DO NOT use "photorealistic" unless it is photography style.
            - Format must be vertical phone wallpaper.

            Return exactly two lines:
            PROMPT: <Full english image prompt>
            CAPTION: <Tweet caption with 4-5 relevant hashtags>
            """
            
            text = model.generate_content(prompt).text
            parts = text.split("CAPTION:")
            
            if len(parts) < 2:
                print("⚠️ Format hatası, tekrar deneniyor...", flush=True)
                time.sleep(2)
                continue 

            img_prompt = parts[0].replace("PROMPT:", "").strip()
            caption = parts[1].strip()
            
            final_prompt = (
                f"{img_prompt}, "
                "vertical wallpaper, 9:21 aspect ratio, full screen coverage, "
                "8k resolution, high quality"
            )
            return final_prompt, caption

        except Exception as e:
            print(f"🛑 Gemini Hatası: {e}", flush=True)
            print("⏳ Kota dolmuş olabilir. 10 Dakika bekleyip tekrar deneyeceğim...", flush=True)
            time.sleep(600)


# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    # Her resim için benzersiz tohum
    unique_seed = random.randint(1, 1000000000)
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v8.0-Gemini2"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 640,                 
            "height": 1408,  # Güvenli İnce-Uzun Boyut             
            "steps": 30,                 
            "seed": unique_seed,
            "post_processing": ["RealESRGAN_x4plus"] 
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["Juggernaut XL", "AlbedoBase XL (SDXL)", "SDXL_beta"] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers, timeout=30)
        if req.status_code != 202:
            print(f"⚠️ Sunucu Hatası: {req.text}", flush=True)
            return None 
        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...", flush=True)
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}", flush=True)
        return None

    # Bekleme
    wait_time = 0
    max_wait = 2700 
    
    while wait_time < max_wait:
        time.sleep(20) 
        wait_time += 20
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url, timeout=30)
            status_data = check.json()
            
            if status_data['done']:
                generations = status_data['generations']
                if len(generations) > 0:
                    print("⬇️ Resim indiriliyor...", flush=True)
                    img_url = generations[0]['img']
                    return requests.get(img_url, timeout=60).content
                else:
                    print("⚠️ Horde boş yanıt döndü.", flush=True)
                    return None
            
            wait_t = status_data.get('wait_time', '?')
            queue = status_data.get('queue_position', '?')
            print(f"⏳ Geçen: {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn", flush=True)
        except Exception as e:
            time.sleep(5) 

    print("⚠️ Zaman aşımı.", flush=True)
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
            text=caption, 
            media_ids=[media.media_id]
        )
        print("🐦 TWEET BAŞARIYLA ATILDI!", flush=True)
        return True 
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}", flush=True)
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Bot Başlatılıyor... (Gemini 2.0 Flash Modu)", flush=True)
    
    # 1. ADIM: Sadece bir kere fikir al
    prompt, caption = get_idea_from_gemini()
    print("------------------------------------------------", flush=True)
    print("🎯 Hedeflenen Konu:", prompt[:100] + "...", flush=True)
    print("📝 Tweet:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    # 2. ADIM: O fikri çizdirene kadar dene
    while not basari:
        print(f"\n🔄 RESİM DENEMESİ: {deneme_sayisi}", flush=True)
        
        try:
            # Gemini'ye tekrar sormuyoruz, aynı promptu kullanıyoruz
            img = try_generate_image(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
                else:
                    print("⚠️ Resim var ama Tweet atılamadı.", flush=True)
            else:
                print("⚠️ Resim çizilemedi.", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 Sunucular yoğun, 2 dakika dinlenip AYNI prompt ile tekrar deniyorum...", flush=True)
            time.sleep(120) 
            deneme_sayisi += 1
