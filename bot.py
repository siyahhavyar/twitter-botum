import os
import time
import requests
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
HORDE_KEY     = os.getenv("HORDE_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.")
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)")

if not GEMINI_KEY:
    print("ERROR: GEMINI_KEY eksik!")
    exit(1)

# -----------------------------
# 1. GEMINI PROMPT GENERATOR (İNATÇI VE ÖZGÜR MOD)
# -----------------------------
def generate_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    
    generation_config = genai.types.GenerationConfig(
        temperature=1.0, top_p=0.99, top_k=40,
    )
    model = genai.GenerativeModel("gemini-2.0-flash", generation_config=generation_config)

    # --- SADECE GEMINI VAR, YEDEK YOK ---
    # Bu döngü Gemini cevap verene kadar kırılmaz.
    while True:
        try:
            print("Gemini'ye yeni bir fikir soruluyor...")
            
            prompt = """
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
            
            text = model.generate_content(prompt).text
            parts = text.split("CAPTION:")
            
            if len(parts) < 2:
                # Format bozuksa tekrar dene
                print("Gemini formatı tutturamadı, tekrar soruluyor...")
                time.sleep(5)
                continue 

            img_prompt = parts[0].replace("PROMPT:", "").strip()
            caption = parts[1].strip()
            
            final_prompt = (
                f"{img_prompt}, "
                "vertical wallpaper, 9:19 aspect ratio, full screen coverage, "
                "8k resolution, high quality"
            )
            return final_prompt, caption

        except Exception as e:
            # HATA YAKALAMA (429 Quota Exceeded vb.)
            print(f"⚠️ Gemini Hatası: {e}")
            print("⏳ Kota dolmuş olabilir. 10 Dakika dinlenip TEKRAR GEMINI'YE soracağım. Yedek yok.")
            time.sleep(600) # 10 Dakika bekle ve döngünün başına dön (Tekrar dene)


# -----------------------------
# 2. AI HORDE (GENİŞLETİLMİŞ FULL EKRAN MODU)
# -----------------------------
def generate_image_horde(prompt_text):
    print("AI Horde → Wallpaper isteği gönderiliyor...")
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v4.3-Patient"
    }
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 704,    # Genişletilmiş (Yanlarda siyah boşluk kalmasın diye)             
            "height": 1536,  # Full Ekran Yüksekliği             
            "steps": 30,                 
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

    # Bekleme (60 Dk)
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
            text=caption + " #AIArt #Wallpaper",
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
# MAIN (SONSUZ DÖNGÜ - UZUN MOLA)
# -----------------------------
if __name__ == "__main__":
    print("Bot Başlatılıyor... Sadece Gemini + Sabır Modu.")
    
    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n=== DENEME {deneme_sayisi} BAŞLIYOR ===")
        
        try:
            # Burası Gemini cevap verene kadar çıkmaz
            prompt, caption = generate_prompt_caption()
            print("Onaylanan Prompt:", prompt[:100] + "...") 
            
            img = generate_image_horde(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 İşlem tamam.")
                else:
                    print("⚠️ Tweet hatası.")
            else:
                print("⚠️ Resim hatası.")
                
        except Exception as e:
            print(f"⚠️ Beklenmeyen genel hata: {e}")
        
        if not basari:
            # Gemini'yi ve sistemi yormamak için hata durumunda 15 DAKİKA BEKLE
            print("⏳ Hata oluştu. Kotayı korumak için 15 DAKİKA bekleyip tekrar deneyeceğim...")
            time.sleep(900) # 900 saniye = 15 Dakika
            deneme_sayisi += 1
