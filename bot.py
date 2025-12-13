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

# Hafıza Dosyası Adı
MEMORY_FILE = "bot_memory.txt"

# Anonim Mod Kontrolü
if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Horde Key yok, Anonim mod (Yavaş olabilir).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# YARDIMCI FONKSİYONLAR: HAFIZA SİSTEMİ
# -----------------------------
def load_memory():
    """Geçmişte çizilen son 20 konuyu yükler."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines[-20:] # Sadece son 20 tanesini hatırlasa yeter, fazlası kafasını karıştırır

def save_to_memory(topic):
    """Yeni çizilen konuyu hafızaya kaydeder."""
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(topic + "\n")

# -----------------------------
# 1. FİKİR ÜRETİCİ (KAOS VE HAFIZA MODU)
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka hafızasını kontrol ediyor ve Kaos Motorunu çalıştırıyor...", flush=True)
    
    # 1. HAFIZAYI YÜKLE
    past_topics = load_memory()
    past_topics_str = ", ".join(past_topics) if past_topics else "None (First run)"
    
    # 2. KAOS MOTORU (Rastgelelik Tohumları)
    # Bu listeler yapay zekayı zorla farklı yönlere iter.
    materials = ["Glass", "Liquid Gold", "Smoke", "Neon Lasers", "Origami Paper", "Marble", "Rusty Metal", "Clouds", "Candy", "Ice"]
    subjects = ["Samurai", "Astronaut", "Giant Cat", "Floating Island", "Ancient Temple", "Cybernetic Plant", "Melting Clock", "Ghost Ship", "Robot Dragon", "Chess Piece"]
    styles = ["Ukiyo-e", "Cyberpunk", "Renaissance", "Vaporwave", "Bauhaus", "Gothic", "Abstract Expressionism", "Low Poly", "Surrealism", "Pop Art"]
    emotions = ["Melancholic", "Energetic", "Mysterious", "Terrifying", "Peaceful", "Chaotic", "Lonely", "Majestic"]
    
    # Rastgele bir kombinasyon seç
    random_combo = f"{random.choice(emotions)} {random.choice(materials)} {random.choice(subjects)} in {random.choice(styles)} style"
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # --- GELİŞTİRİLMİŞ PROMPT ---
    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    
    ROLE: You are an avant-garde AI Art Curator with infinite imagination.
    
    MEMORY CHECK (DO NOT DRAW THESE):
    The following topics were already drawn recently. DO NOT REPEAT THEM:
    [{past_topics_str}]
    
    INSPIRATION SEED (Use this as a starting point, but evolve it):
    "{random_combo}"
    
    YOUR TASK:
    Create a highly detailed, unique, and mind-blowing phone wallpaper prompt based on the seed above, but make it unique.
    
    RULES:
    1. AVOID common AI clichés (like just a generic sunset or standard cyberpunk city).
    2. Focus on unique lighting, texture, and composition.
    3. The output must be visually striking for a smartphone wallpaper.
    
    Return exactly two lines:
    PROMPT: <The detailed English image prompt>
    CAPTION: <A short, artistic tweet caption including hashtags>
    """

    # --- PLAN A: GROQ ---
    if GROQ_KEY:
        try:
            print(f"🧠 Groq düşünüyor... (İlham: {random_combo})", flush=True)
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
                    prompt_text = parts[0].replace("PROMPT:", "").strip()
                    caption_text = parts[1].strip()
                    
                    # Konuyu hafızaya kaydet (Özet olarak)
                    save_to_memory(random_combo) 
                    
                    print("✅ Groq benzersiz bir fikir buldu!", flush=True)
                    return prompt_text, caption_text
        except Exception as e: print(f"Groq Hata: {e}")

    # --- PLAN B: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Gemini düşünüyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.0)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                prompt_text = parts[0].replace("PROMPT:", "").strip()
                caption_text = parts[1].strip()
                save_to_memory(random_combo)
                return prompt_text, caption_text
        except Exception: pass

    # --- PLAN C: POLLINATIONS ---
    try:
        encoded = urllib.parse.quote(f"Imagine a unique wallpaper: {random_combo}. Return PROMPT: ... CAPTION: ...")
        response = requests.get(f"https://text.pollinations.ai/{encoded}?seed={random.randint(1,9999)}", timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except Exception: pass

    return f"Masterpiece wallpaper of {random_combo}, 8k", "#Art"


def prepare_final_prompt(raw_prompt):
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, 8k resolution, "
        "masterpiece, highly detailed, sharp focus, vibrant colors"
    )

# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    current_key = HORDE_KEY if HORDE_KEY else "0000000000"
    headers = {"apikey": current_key, "Client-Agent": "MyTwitterBot:v6.0-ChaosMode"}
    
    #  
    # Bu diyagram, istemcinin sunucuya nasıl istek gönderdiğini ve worker'ların (işçilerin) 
    # görseli nasıl işleyip geri döndürdüğünü gösterir.
    
    print("💎 Mod: Yüksek Kalite deneniyor...", flush=True)
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
        
        if req.status_code != 202:
            error_msg = req.text
            print(f"⚠️ Yüksek Kalite Reddedildi: {error_msg[:100]}...", flush=True)
            
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Sunucular dolu! Ekonomi Moduna geçiliyor...", flush=True)
                payload_high["params"]["post_processing"] = [] 
                payload_high["params"]["steps"] = 20 
                
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

    # Bekleme Döngüsü
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
    print("🚀 Bot Başlatılıyor... (KAOS + HAFIZA MODU)", flush=True)
    
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
    
