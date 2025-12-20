import os
import time
import requests
import tweepy
import random
import urllib.parse
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
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# Anonim Mod Kontrolü
if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Horde Key yok, Anonim mod (Yavaş olabilir).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# 1. FİKİR ÜRETİCİ (SAF SANATÇI MODU)
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka sanatçı koltuğuna oturuyor ve düşünüyor...", flush=True)
    
    # Zamana göre benzersizlik katıyoruz
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # --- İŞTE BURASI DEĞİŞTİ: HİÇBİR KONU/ÖRNEK YOK ---
    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    
    Act as a Visionary Digital Artist and Trendsetter.
    
    I am giving you a BLANK CANVAS.
    I am NOT giving you a topic.
    I am NOT giving you a style.
    
    YOUR TASK:
    Close your virtual eyes and imagine a Masterpiece Phone Wallpaper.
    Think: "What visual concept would make people stop scrolling and say WOW?"
    
    It can be ANYTHING:
    - Something abstract and emotional?
    - A scene from a movie that doesn't exist?
    - A futuristic invention?
    - A wild mixture of nature and technology?
    - A bizarre dream?
    
    RULES:
    1. Be 100% Original. Do not use clichés.
    2. Make it VISUALLY STUNNING.
    3. Decide the subject, the lighting, the colors, and the mood YOURSELF.
    
    Return exactly two lines:
    PROMPT: <The detailed English description of your vision>
    CAPTION: <A short, artistic tweet caption for this wallpaper>
    """

    # --- PLAN A: GROQ (En Yaratıcısı) ---
    if GROQ_KEY:
        try:
            print("🧠 Groq hayal kuruyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.0 # Yüksek yaratıcılık
            }
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    print("✅ Groq bir fikir buldu!", flush=True)
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception: pass

    # --- PLAN B: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Gemini hayal kuruyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.0)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception: pass

    # --- PLAN C: POLLINATIONS (Yedek) ---
    try:
        encoded = urllib.parse.quote("Imagine a unique, artistic wallpaper. Return PROMPT: ... CAPTION: ...")
        response = requests.get(f"https://text.pollinations.ai/{encoded}?seed={random.randint(1,9999)}", timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except Exception: pass

    return "A masterpiece artistic wallpaper, 8k", "#Art"


def prepare_final_prompt(raw_prompt):
    # Sadece teknik kalite komutları ekliyoruz, STİL eklemiyoruz.
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, 8k resolution, "
        "masterpiece, highly detailed, sharp focus"
    )

# -----------------------------
# 2. AI HORDE (KESİNTİSİZ - PUAN HATASI ÖNLEYİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    current_key = HORDE_KEY if HORDE_KEY else "0000000000"
    headers = {"apikey": current_key, "Client-Agent": "MyTwitterBot:v5.0"}
    
    # --- 1. DENEME: KALİTELİ MOD ---
    print("💎 Mod 1: Yüksek Kalite deneniyor...", flush=True)
    payload_high = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7,               
            "width": 640,    
            "height": 1408,               
            "steps": 30,
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"]
        },
        "nsfw": False, "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"] 
    }

    try:
        req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
        
        # Hata yakalama
        if req.status_code != 202:
            error_msg = req.text
            print(f"⚠️ Yüksek Kalite Reddedildi: {error_msg[:100]}...", flush=True)
            
            # Sunucu "Puan yetersiz" veya "Yoğunum" derse:
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Sunucular dolu! Standart Kaliteye (Ekonomi Modu) geçiliyor...", flush=True)
                payload_high["params"]["post_processing"] = [] # Upscale kapat
                payload_high["params"]["steps"] = 20 # Adımı düşür
                
                req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
                if req.status_code != 202:
                    print(f"❌ Ekonomi Modu da reddedildi.", flush=True)
                    return None
            else:
                return None

        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...", flush=True)
        
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}", flush=True)
        return None

    # Bekleme
    wait_time = 0
    max_wait = 1800 
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
                    return None
            
            wait_t = status_data.get('wait_time', '?')
            queue = status_data.get('queue_position', '?')
            print(f"⏳ Geçen: {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn", flush=True)
        except Exception:
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
        
        client.create_tweet(text=caption, media_ids=[media.media_id])
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
    print("🚀 Bot Başlatılıyor... (SAF SANATÇI MODU)", flush=True)
    
    # Fikir al
    prompt, caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Yapay Zekanın Bulduğu Konu:", prompt[:100] + "...", flush=True)
    print("📝 Tweet:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n🔄 DENEME: {deneme_sayisi}", flush=True)
        
        try:
            img = try_generate_image(prompt)
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
                else:
                    print("⚠️ Resim var ama Tweet atılamadı.", flush=True)
            else:
                print("⚠️ Resim çizilemedi (Sunucu hatası).", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 Sunucular dolu, 3 dakika bekleyip tekrar deniyorum...", flush=True)
            time.sleep(180) 
            deneme_sayisi += 1
    
