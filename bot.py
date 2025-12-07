import os
import time
import requests
import tweepy
import random
import google.generativeai as genai
from datetime import datetime
from tweepy import OAuthHandler, API, Client

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
    print("ERROR: GEMINI_KEY eksik! GitHub Secrets'ı kontrol et.", flush=True)
    exit(1)

# -----------------------------
# 1. GEMINI (1.5 FLASH STANDART) - SANAT YÖNETMENİ
# -----------------------------
def get_idea_from_gemini():
    """
    Gemini 1.5 Flash standart modelini kullanır.
    En kararlı çalışan versiyondur.
    """
    genai.configure(api_key=GEMINI_KEY)
    
    # Yaratıcılık ayarları
    generation_config = genai.types.GenerationConfig(
        temperature=1.1,
        top_p=0.95,
        top_k=40,
    )
    
    # --- DÜZELTME BURADA: İsim "gemini-1.5-flash" olarak sabitlendi ---
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

    while True:
        try:
            print("🧠 Gemini (1.5 Flash) benzersiz bir eser düşünüyor...", flush=True)
            
            # Her saniye değişen zaman damgası
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            
            prompt = f"""
            Timestamp: {current_timestamp}
            Act as an avant-garde AI Art Curator with limitless imagination. 
            Your task is to invent a unique vertical phone wallpaper concept that feels like real art, not generic AI generation.

            INSTRUCTIONS:
            1. Combine a specific Art Style (e.g., Bauhaus, Ukiyo-e, Glitch Art, Brutalism, Ethereal, Macro Photography, Sketch) with a unique Subject.
            2. Be unpredictable. Do not repeat recent concepts.

            CRITICAL RULES:
            - NO HORROR, NO GORE, NO NSFW.
            - DO NOT use "photorealistic" unless the chosen style is specifically photography.
            - COMPOSITION: Must be a vertical, tall phone wallpaper fit.

            Return exactly two lines:
            PROMPT: <The full detailed english prompt for the image generator>
            CAPTION: <An engaging short tweet caption related to the image + 4-5 relevant hashtags>
            """
            
            text = model.generate_content(prompt).text
            parts = text.split("CAPTION:")
            
            if len(parts) < 2:
                print("⚠️ Format hatası, anlık bir sorun, tekrar soruluyor...", flush=True)
                time.sleep(3)
                continue 

            img_prompt = parts[0].replace("PROMPT:", "").strip()
            caption = parts[1].strip()
            
            # Horde için güvenli boyut ve kalite komutları
            final_prompt = (
                f"{img_prompt}, "
                "vertical wallpaper, 9:21 aspect ratio, tall composition, "
                "8k resolution, high quality, highly detailed"
            )
            return final_prompt, caption

        except Exception as e:
            print(f"🛑 Gemini Hatası: {e}", flush=True)
            print("⏳ Hata alındı. 5 Dakika dinlenip tekrar deneyeceğim...", flush=True)
            time.sleep(300) # 5 dakika bekle


# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    # Her çizim için benzersiz bir matematiksel tohum (seed)
    unique_seed = random.randint(1, 9999999999)
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v10.1-GeminiStable"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 640,    # Güvenli, ince-uzun boyut
            "height": 1408,               
            "steps": 30,                 
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"] # HD Kalite
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

    # Bekleme (45 Dk limit)
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
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)
        client = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        # Gemini'nin ürettiği akıllı etiketli metin
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
    print("🚀 Bot Başlatılıyor... (Gemini 1.5 Flash - Sabit Sürüm)", flush=True)
    
    # 1. ADIM: Fikri SADECE BİR KERE al
    prompt, caption = get_idea_from_gemini()
    print("------------------------------------------------", flush=True)
    print("🎯 Gemini'nin Sanat Fikri:", prompt[:100] + "...", flush=True)
    print("📝 Tweet Metni:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    # 2. ADIM: O fikri çizdirene kadar dene
    while not basari:
        print(f"\n🔄 RESİM ÇİZİM DENEMESİ: {deneme_sayisi}", flush=True)
        
        try:
            # Aynı promptu kullanıyoruz
            img = try_generate_image(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
                else:
                    print("⚠️ Resim var ama Tweet atılamadı (Twitter sorunu).", flush=True)
            else:
                print("⚠️ Resim çizilemedi (Sunucu yoğunluğu veya hata).", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 Sunucular yoğun, 3 dakika dinlenip AYNI fikirle tekrar deniyorum...", flush=True)
            time.sleep(180) # 3 dakika bekle
            deneme_sayisi += 1
            
