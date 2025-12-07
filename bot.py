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
GROQ_KEY      = os.getenv("GROQ_API_KEY") # YENİ OYUNCU

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# 1. FİKİR ÜRETİCİ (MUHTEŞEM ÜÇLÜ: GEMINI -> GROQ -> POLLINATIONS)
# -----------------------------
def get_idea_ultimate():
    """
    Sırasıyla Gemini, Groq ve Pollinations'ı dener.
    Asla fikir bulmadan dönmez.
    """
    
    # --- PLAN A: GEMINI (1.5 Flash) ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini (1.5 Flash) deneniyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            
            # Yaratıcılık ayarları
            config = genai.types.GenerationConfig(temperature=1.1, top_p=0.95, top_k=40)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config=config)
            
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = f"""
            Timestamp: {current_timestamp}
            Act as an avant-garde AI Art Curator. Invent a unique vertical phone wallpaper concept.
            Rules: NO Horror, NO Gore, NO NSFW.
            Return exactly two lines:
            PROMPT: <Full english image prompt>
            CAPTION: <Tweet caption with 4-5 hashtags>
            """
            
            response = model.generate_content(prompt)
            parts = response.text.split("CAPTION:")
            
            if len(parts) >= 2:
                print("✅ Gemini Başarılı!", flush=True)
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
                
        except Exception as e:
            print(f"⚠️ Gemini Hatası: {e}", flush=True)
            print("🔄 Gemini yanıt vermedi, Plan B (Groq)'a geçiliyor...", flush=True)

    # --- PLAN B: GROQ (LLAMA 3) ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq (Llama 3) deneniyor...", flush=True)
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt_text = f"""
            Timestamp: {current_timestamp}
            Act as an AI Art Curator. Invent a unique vertical phone wallpaper concept.
            Rules: NO Horror, NO Gore, NO NSFW.
            Return exactly two lines:
            PROMPT: <Full english image prompt>
            CAPTION: <Tweet caption with hashtags>
            """
            
            data = {
                "model": "llama3-70b-8192", 
                "messages": [{"role": "user", "content": prompt_text}],
                "temperature": 1.0
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                parts = content.split("CAPTION:")
                if len(parts) >= 2:
                    print("✅ Groq Başarılı!", flush=True)
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
            else:
                print(f"⚠️ Groq Hatası: {response.text}", flush=True)
                
        except Exception as e:
            print(f"⚠️ Groq Bağlantı Hatası: {e}", flush=True)
            print("🔄 Groq yanıt vermedi, Plan C (Pollinations)'a geçiliyor...", flush=True)
    else:
        print("ℹ️ Groq Key tanımlı değil, atlanıyor.", flush=True)

    # --- PLAN C: POLLINATIONS (YEDEK) ---
    try:
        print("🧠 Plan C: Pollinations AI (Bedava) düşünülüyor...", flush=True)
        seed = random.randint(1, 999999)
        instruction = (
            f"Act as an AI Art Curator. Seed: {seed}. "
            "Invent a unique vertical phone wallpaper concept. "
            "Rules: NO Horror, NO Gore, NO NSFW. "
            "Return exactly two lines: PROMPT: ... and CAPTION: ..."
        )
        encoded = urllib.parse.quote(instruction)
        url = f"https://text.pollinations.ai/{instruction}?seed={seed}"
        
        response = requests.get(url, timeout=30)
        parts = response.text.split("CAPTION:")
        
        if len(parts) >= 2:
            print("✅ Pollinations Başarılı!", flush=True)
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
            
    except Exception as e:
        print(f"🛑 Pollinations Hatası: {e}", flush=True)

    # Hiçbiri çalışmazsa (İmkansız ama)
    print("❌ Tüm sistemler çöktü. Varsayılan dönülüyor.", flush=True)
    return "Abstract minimalist wallpaper, 8k", "#AIArt"


def prepare_final_prompt(raw_prompt):
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, full screen coverage, "
        "8k resolution, high quality, highly detailed"
    )

# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = random.randint(1, 9999999999)
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v12.0-Ultimate"
    }
    
    payload = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 640,    # Güvenli İnce-Uzun Boyut
            "height": 1408,               
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
    print("🚀 Bot Başlatılıyor... (Gemini -> Groq -> Pollinations)", flush=True)
    
    # 1. ADIM: Fikir Al (3 Kademeli Sistem)
    prompt, caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Seçilen Konu:", prompt[:100] + "...", flush=True)
    print("📝 Tweet:", caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    # 2. ADIM: Çizdir
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
