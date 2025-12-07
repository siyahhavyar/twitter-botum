import os
import time
import requests
import tweepy
import random

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
HORDE_KEY     = os.getenv("HORDE_API_KEY")

# Gemini Key kontrolünü kaldırdım, artık gerek yok.

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.")
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)")


# -----------------------------
# 1. POLLINATIONS TEXT GENERATOR (BEDAVA BEYİN)
# -----------------------------
def get_idea_from_ai():
    """
    Gemini yerine Pollinations AI Text servisini kullanır.
    API Key istemez, tamamen ücretsizdir.
    """
    while True:
        try:
            print("🧠 Yapay Zeka (Pollinations) fikir düşünüyor...")
            
            # Yapay Zekaya gönderilecek talimat
            instruction = """
            Act as an unpredictable AI Art Curator. Invent a unique phone wallpaper concept.
            
            INSTRUCTIONS:
            1. Select a RANDOM Art Style (e.g. Minimalism, Ukiyo-e, Cyberpunk, Oil Painting, Sketch, Abstract, Pop Art, etc.).
            2. Select a RANDOM Subject.
            3. Combine them into a detailed image prompt.

            CRITICAL RULES:
            - NO HORROR, NO GORE, NO NSFW.
            - DO NOT use the word "photorealistic" or "unreal engine" unless the style is photography.
            - The composition must be vertical but WIDE ENOUGH to fill screen edges.

            Return exactly two lines:
            PROMPT: <The full english prompt>
            CAPTION: <A short, engaging tweet caption>
            """
            
            # Pollinations'a istek at (GET isteği, model otomatik seçilir)
            # URL encoded prompt gönderiyoruz
            response = requests.get(f"https://text.pollinations.ai/{instruction}")
            
            if response.status_code != 200:
                print("⚠️ AI Bağlantı hatası, tekrar deneniyor...")
                time.sleep(2)
                continue
                
            text = response.text
            parts = text.split("CAPTION:")
            
            if len(parts) < 2:
                # Bazen AI formatı tutturamazsa basitçe tekrar soralım
                print("⚠️ Format hatası, tekrar soruluyor...")
                time.sleep(2)
                continue 

            img_prompt = parts[0].replace("PROMPT:", "").strip()
            caption = parts[1].strip()
            
            # Senin istediğin Ultra Uzun format komutları
            final_prompt = (
                f"{img_prompt}, "
                "vertical wallpaper, 9:21 aspect ratio, full screen coverage, "
                "8k resolution, high quality"
            )
            return final_prompt, caption

        except Exception as e:
            print(f"🛑 AI Hatası: {e}")
            print("⏳ 1 Dakika bekleyip tekrar deneyeceğim...")
            time.sleep(60)


# -----------------------------
# 2. AI HORDE (KALİTELİ RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    print("🎨 AI Horde → Resim çiziliyor (Kalite: Juggernaut XL)...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v6.0-NoGemini"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 704,    # Senin beğendiğin genişletilmiş ayar             
            "height": 1536,  # Ultra uzun boy             
            "steps": 30,                 
            "post_processing": ["RealESRGAN_x4plus"] 
        },
        "nsfw": False,
        "censor_nsfw": True,
        # Kalite için en iyi modeller
        "models": ["Juggernaut XL", "AlbedoBase XL (SDXL)", "SDXL_beta"] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers)
        if req.status_code != 202:
            print(f"⚠️ Sunucu Hatası: {req.text}")
            return None 
        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...")
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}")
        return None

    # Bekleme (45 Dk limit)
    wait_time = 0
    max_wait = 2700 
    
    while wait_time < max_wait:
        time.sleep(20) 
        wait_time += 20
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url)
            status_data = check.json()
            
            if status_data['done']:
                generations = status_data['generations']
                if len(generations) > 0:
                    print("⬇️ Resim indiriliyor...")
                    img_url = generations[0]['img']
                    return requests.get(img_url).content
                else:
                    print("⚠️ Horde boş yanıt döndü.")
                    return None
            
            wait_t = status_data.get('wait_time', '?')
            queue = status_data.get('queue_position', '?')
            print(f"⏳ Geçen: {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn")
        except Exception as e:
            time.sleep(5) 

    print("⚠️ Zaman aşımı.")
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
            text=caption + " #AIArt #Wallpaper",
            media_ids=[media.media_id]
        )
        print("🐦 TWEET BAŞARIYLA ATILDI!")
        return True 
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Bot Başlatılıyor... (Gemini YOK, Pollinations VAR)")
    
    # 1. ADIM: Bedava beyinden fikir al
    prompt, caption = get_idea_from_ai()
    print("------------------------------------------------")
    print("🎯 Hedeflenen Konu:", prompt[:100] + "...")
    print("------------------------------------------------")

    basari = False
    deneme_sayisi = 1
    
    # 2. ADIM: O fikri çizdirene kadar dene
    while not basari:
        print(f"\n🔄 RESİM DENEMESİ: {deneme_sayisi}")
        
        try:
            # Aynı promptu kullanıyoruz
            img = try_generate_image(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.")
                else:
                    print("⚠️ Resim var ama Tweet atılamadı.")
            else:
                print("⚠️ Resim çizilemedi.")
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}")
        
        if not basari:
            print("💤 Sunucular yoğun, 2 dakika dinlenip AYNI prompt ile tekrar deniyorum...")
            time.sleep(120) 
            deneme_sayisi += 1
