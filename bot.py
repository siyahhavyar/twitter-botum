import os
import time
import requests
import tweepy
import random
import urllib.parse 

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
HORDE_KEY     = os.getenv("HORDE_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)", flush=True)


# -----------------------------
# 1. POLLINATIONS (FİKİR VE ETİKET BABASI)
# -----------------------------
def get_idea_from_ai():
    while True:
        try:
            print("🧠 Yapay Zeka (Pollinations) fikir ve etiket düşünüyor...", flush=True)
            
            # YENİ TALİMAT: "Caption" kısmına etiketleri de eklemesini söyledik.
            instruction = (
                "Act as an AI Art Curator. Invent a unique vertical phone wallpaper concept. "
                "Randomly select an Art Style and a Subject. Combine them into a detailed image prompt. "
                "Rules: NO Horror, NO Gore, NO NSFW. "
                "Return exactly two lines: "
                "PROMPT: (the full english prompt) "
                "CAPTION: (a short tweet caption INCLUDING 4-5 relevant hashtags based on the style and subject, e.g. #Cyberpunk #City)"
            )
            
            encoded_instruction = urllib.parse.quote(instruction)
            
            response = requests.get(f"https://text.pollinations.ai/{encoded_instruction}", timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️ AI Bağlantı hatası ({response.status_code}), tekrar deneniyor...", flush=True)
                time.sleep(5)
                continue
                
            text = response.text
            parts = text.split("CAPTION:")
            
            if len(parts) < 2:
                print("⚠️ Format hatası, tekrar soruluyor...", flush=True)
                time.sleep(2)
                continue 

            img_prompt = parts[0].replace("PROMPT:", "").strip()
            caption = parts[1].strip() # Artık etiketler bu caption'ın içinde!
            
            final_prompt = (
                f"{img_prompt}, "
                "vertical wallpaper, 9:21 aspect ratio, full screen coverage, "
                "8k resolution, high quality"
            )
            return final_prompt, caption

        except Exception as e:
            print(f"🛑 AI Hatası: {e}", flush=True)
            print("⏳ 1 Dakika bekleyip tekrar deneyeceğim...", flush=True)
            time.sleep(60)


# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    print("🎨 AI Horde → Resim çiziliyor (Kalite: Juggernaut XL)...", flush=True)
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v6.3-SmartTags"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 640,                 
            "height": 1408,  # Güvenli ince-uzun boyut             
            "steps": 30,                 
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
        
        # --- DEĞİŞİKLİK BURADA ---
        # Artık sabit "#AIArt #Wallpaper" etiketlerini kaldırdık.
        # "caption" değişkeni zaten yapay zekanın ürettiği etiketleri içeriyor.
        client.create_tweet(
            text=caption, 
            media_ids=[media.media_id]
        )
        print("🐦 TWEET BAŞARIYLA ATILDI! (Etiketler dahil)", flush=True)
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
    print("🚀 Bot Başlatılıyor... (Akıllı Etiket Modu)", flush=True)
    
    # 1. ADIM: Bedava beyinden fikir VE etiket al
    prompt, caption = get_idea_from_ai()
    print("------------------------------------------------", flush=True)
    print("🎯 Hedeflenen Konu:", prompt[:100] + "...", flush=True)
    print("📝 Hazırlanan Tweet:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    # 2. ADIM: O fikri çizdirene kadar dene
    while not basari:
        print(f"\n🔄 RESİM DENEMESİ: {deneme_sayisi}", flush=True)
        
        try:
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
