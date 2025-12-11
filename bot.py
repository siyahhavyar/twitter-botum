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

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# 1. FİKİR ÜRETİCİ (MODERN VE EĞLENCELİ KARIŞIM)
# -----------------------------
def get_idea_ultimate():
    
    styles_map = {
        "Cinematic": "Cinematic Movie Shot (Netflix style, 8k, dramatic lighting, highly detailed, photorealistic)",
        "Superhero": "Comic Book / Superhero Art (Marvel/DC style, dynamic pose, action scene, vibrant colors)",
        "Cyberpunk": "Cyberpunk City (Neon lights, rain, high tech, futuristic cars, night time)",
        "StreetStyle": "Modern Street Photography (Fashion, urban life, coffee shops, rainy window, candid shot)",
        "Fantasy": "Epic Fantasy (Lord of the Rings style, magic, warriors, mythical creatures, grand landscapes)",
        "RetroWave": "Retro 80s Synthwave (Purple sunsets, sports cars, palm trees, nostalgic vibe)",
        "SciFi": "Futuristic Sci-Fi (Spaceships, astronauts, alien planets, high-tech labs)",
    }
    
    keys = list(styles_map.keys())
    chosen_key = random.choice(keys)
    forced_style = styles_map[chosen_key]
    
    print(f"🎨 ZAR ATILDI, GELEN TARZ: {chosen_key.upper()}", flush=True)

    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    Act as a creative Art Director.
    STYLE TO USE: {forced_style}
    
    CRITICAL RULES:
    1. ❌ DO NOT GENERATE SIMPLE GEOMETRIC SHAPES OR PLAIN CIRCLES. ❌
    2. Make it COMPLEX, DETAILED, and MODERN.
    3. Focus on: Characters, Action, Scenery, Emotion, or Technology.
    
    Return exactly two lines:
    PROMPT: <Highly detailed English image prompt>
    CAPTION: <Cool, engaging caption with hashtags>
    """

    # --- PLAN A: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini düşünüyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.3, top_p=0.99)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception: pass

    # --- PLAN B: GROQ ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq düşünüyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.0
            }
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception: pass

    # --- PLAN C: POLLINATIONS ---
    try:
        encoded = urllib.parse.quote(f"Create a wallpaper prompt about: {forced_style}. Return PROMPT: ... CAPTION: ...")
        response = requests.get(f"https://text.pollinations.ai/{encoded}?seed={random.randint(1,9999)}", timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except Exception: pass

    return f"Epic wallpaper in style {forced_style}", "#AIArt #Wallpaper"


def prepare_final_prompt(raw_prompt):
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, highly detailed, 8k resolution, "
        "intricate details, trending on artstation, unreal engine 5 render, cinematic lighting"
    )

# -----------------------------
# 2. AI HORDE (AKILLI VİTES KÜÇÜLTME MODU)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    # --- 1. DENEME: YÜKSEK KALİTE (LÜKS MOD) ---
    print("💎 Mod 1: Yüksek Kalite deneniyor...", flush=True)
    
    # Eğer key yoksa Anonim (0000000000) kullan
    current_key = HORDE_KEY if HORDE_KEY else "0000000000"
    
    headers = {"apikey": current_key, "Client-Agent": "MyTwitterBot:v3.0"}
    
    payload_high = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7,               
            "width": 640,    
            "height": 1408,               
            "steps": 30,
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"] # Bu özellik bazen "Kudos" hatası verdirir
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"] 
    }

    # İsteği gönder
    try:
        req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
        
        # --- HATA YAKALAMA (Kudos Hatası mı?) ---
        if req.status_code != 202:
            error_msg = req.text
            print(f"⚠️ Yüksek Kalite Reddedildi: {error_msg}", flush=True)
            
            # Eğer hata "KudosUpfront" veya "Too much demand" ise PLANA B'ye geç
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Sunucular yoğun! Standart Kaliteye (Ekonomi Modu) geçiliyor...", flush=True)
                
                # --- 2. DENEME: STANDART KALİTE (EKONOMİ MODU) ---
                # Ayarları düşürüyoruz ki sunucu kabul etsin
                payload_high["params"]["post_processing"] = [] # Upscale'i kapat (En çok bu yorar)
                payload_high["params"]["steps"] = 25 # Adımı biraz azalt
                
                # Tekrar dene
                req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
                if req.status_code != 202:
                    print(f"❌ Ekonomi Modu da reddedildi: {req.text}", flush=True)
                    return None
            else:
                return None

        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...", flush=True)
        
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}", flush=True)
        return None

    # Bekleme Döngüsü
    wait_time = 0
    max_wait = 1800 # 30 dakika bekleme limiti
    
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
                    print("⚠️ Resim çizildi ama boş geldi.", flush=True)
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
    print("🚀 Bot Başlatılıyor... (Akıllı Vites Modu)", flush=True)
    
    prompt, caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Seçilen Konu:", prompt[:100] + "...", flush=True)
    print("📝 Tweet:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n🔄 RESİM ÇİZİM DENEMESİ: {deneme_sayisi}", flush=True)
        
        try:
            img = try_generate_image(prompt)
            
            if img:
                if post_to_twitter(img, caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
                else:
                    print("⚠️ Resim var ama Tweet atılamadı.", flush=True)
            else:
                print("⚠️ Resim çizilemedi. (Tüm modlar denendi)", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 Çok yoğunluk var, 5 dakika dinlenip tekrar deniyorum...", flush=True)
            time.sleep(300) 
            deneme_sayisi += 1
            
