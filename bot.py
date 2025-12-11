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
    
    # --- YENİ VE CANLI TARZ LİSTESİ ---
    styles_map = {
        "Cinematic": "Cinematic Movie Shot (Netflix style, 8k, dramatic lighting, highly detailed, photorealistic)",
        "Superhero": "Comic Book / Superhero Art (Marvel/DC style, dynamic pose, action scene, vibrant colors)",
        "Cyberpunk": "Cyberpunk City (Neon lights, rain, high tech, futuristic cars, night time)",
        "StreetStyle": "Modern Street Photography (Fashion, urban life, coffee shops, rainy window, candid shot)",
        "Fantasy": "Epic Fantasy (Lord of the Rings style, magic, warriors, mythical creatures, grand landscapes)",
        "RetroWave": "Retro 80s Synthwave (Purple sunsets, sports cars, palm trees, nostalgic vibe)",
        "Horror": "Dark Mystery / Thriller (Stranger Things vibe, misty forest, abandoned places, suspense)",
        "PopArt": "Modern Pop Art (Colorful, collage, energetic, trendy, street art)",
        "SciFi": "Futuristic Sci-Fi (Spaceships, astronauts, alien planets, high-tech labs)",
        "Luxury": "Luxury & High Tech (Expensive cars, modern architecture, gold & black, sleek design)"
    }
    
    # --- SEÇİM SİSTEMİ (ARTIK EŞİT ŞANS) ---
    # Artık Minimalizm baskısı YOK. Her tarza eşit şans veriyoruz.
    keys = list(styles_map.keys())
    chosen_key = random.choice(keys)
    forced_style = styles_map[chosen_key]
    
    print(f"🎨 ZAR ATILDI, GELEN TARZ: {chosen_key.upper()}", flush=True)

    # Ortak Talimat (DAİRE YASAĞI GETİRİLDİ)
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    Act as a creative Art Director for a modern Instagram/Twitter page.
    
    YOUR MISSION: Create a visually stunning, ATTENTION-GRABBING wallpaper concept.
    👉 STYLE TO USE: {forced_style}
    
    CRITICAL RULES:
    1. ❌ DO NOT GENERATE SIMPLE GEOMETRIC SHAPES OR PLAIN CIRCLES. ❌
    2. Make it COMPLEX, DETAILED, and MODERN.
    3. Focus on: Characters, Action, Scenery, Emotion, or Technology.
    4. NO NSFW.
    
    Return exactly two lines:
    PROMPT: <Highly detailed English image prompt>
    CAPTION: <Cool, engaging caption with hashtags>
    """

    # --- PLAN A: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini düşünüyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.3, top_p=0.99) # Yaratıcılık artırıldı
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            
            if len(parts) >= 2:
                print("✅ Gemini Başarılı!", flush=True)
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception as e:
            print(f"⚠️ Gemini Hatası: {e}", flush=True)

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
                    print("✅ Groq Başarılı!", flush=True)
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    # --- PLAN C: POLLINATIONS (Yedek) ---
    try:
        print("🧠 Plan C: Pollinations deneniyor...", flush=True)
        simple_instruction = f"Create a detailed wallpaper prompt about: {forced_style}. Return PROMPT: ... CAPTION: ..."
        encoded = urllib.parse.quote(simple_instruction)
        response = requests.get(f"https://text.pollinations.ai/{encoded}?seed={random.randint(1,9999)}", timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except Exception:
        pass

    return f"Epic wallpaper in style {forced_style}", "#AIArt #Wallpaper"


def prepare_final_prompt(raw_prompt):
    # Sıkıcı daireleri engellemek için promptu zenginleştiriyoruz
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, highly detailed, 8k resolution, "
        "intricate details, trending on artstation, unreal engine 5 render, cinematic lighting"
    )

# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    print(f"ℹ️ Prompt: {final_prompt[:60]}...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v2.0-ActionPack"
    }
    
    payload = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7,               # Detayları artırmak için 7 yaptık
            "width": 640,    
            "height": 1408,               
            "steps": 35,                  # Daha kaliteli olsun diye 35 adım
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"] 
        },
        "nsfw": False,
        "censor_nsfw": True,
        # SDXL modelleri daha modern ve sinematik çizer
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL", "DreamShaper XL"] 
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
    print("🚀 Bot Başlatılıyor... (Hedef: Full Görsellik ve Aksiyon)", flush=True)
    
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
                print("⚠️ Resim çizilemedi.", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 Sunucular yoğun, 3 dakika dinlenip AYNI fikirle tekrar deniyorum...", flush=True)
            time.sleep(180) 
            deneme_sayisi += 1
            
