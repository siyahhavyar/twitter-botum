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

MEMORY_FILE = "bot_memory.txt"

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Horde Key yok, Anonim mod (Yavaş olabilir).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# HAFIZA SİSTEMİ
# -----------------------------
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines[-20:]

def save_to_memory(topic):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(topic + "\n")

# -----------------------------
# 1. FİKİR ÜRETİCİ (TAMAMEN ÖZGÜR MOD)
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka sanatçı şapkasını taktı, tarzını kendi seçiyor...", flush=True)
    
    past_topics = load_memory()
    past_topics_str = ", ".join(past_topics) if past_topics else "None"
    
    # Rastgelelik tohumu (Sadece beyni tetiklemek için, yönlendirmek için değil)
    chaos_seed = random.randint(1, 999999999)
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # --- BURASI DEĞİŞTİ: ZORLAMA YOK ---
    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    Random Seed: {chaos_seed}
    
    ROLE: You are a VERSATILE Digital Artist with no fixed style.
    
    YOUR TASK:
    Create a phone wallpaper concept.
    
    THE MOST IMPORTANT RULE:
    YOU decide the art style. Do NOT always make it "cinematic" or "realistic".
    
    Vary your style wildly every time. For example:
    - Sometimes choose: Anime / Manga style
    - Sometimes choose: Simple Flat Vector Art (Minimalist)
    - Sometimes choose: Retro Pixel Art
    - Sometimes choose: Classic Oil Painting
    - Sometimes choose: 3D Render
    - Sometimes choose: Comic Book / Pop Art
    - Sometimes choose: Black and White Sketch
    - Sometimes choose: Abstract shapes
    
    MEMORY CHECK (Do not draw these again):
    [{past_topics_str}]
    
    Think like a human artist. "What do I feel like drawing today?"
    
    Return exactly two lines:
    PROMPT: <The detailed image prompt. MUST INCLUDE THE ART STYLE explicitly>
    CAPTION: <A short tweet caption>
    """

    # --- PLAN A: GROQ ---
    if GROQ_KEY:
        try:
            print(f"🧠 Groq düşünüyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.1 # Yaratıcılığı ve rastgeleliği artırdık
            }
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    prompt_text = parts[0].replace("PROMPT:", "").strip()
                    caption_text = parts[1].strip()
                    save_to_memory(prompt_text[:50]) 
                    print("✅ Fikir bulundu!", flush=True)
                    return prompt_text, caption_text
        except Exception as e: print(f"Groq Hata: {e}")

    # --- PLAN B: GEMINI ---
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.1)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                prompt_text = parts[0].replace("PROMPT:", "").strip()
                caption_text = parts[1].strip()
                save_to_memory(prompt_text[:50])
                return prompt_text, caption_text
        except Exception: pass

    # --- PLAN C: POLLINATIONS ---
    try:
        encoded = urllib.parse.quote(f"Imagine a random art style wallpaper. Return PROMPT: ... CAPTION: ...")
        response = requests.get(f"https://text.pollinations.ai/{encoded}?seed={random.randint(1,9999)}", timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except Exception: pass

    return "A surprise artistic wallpaper", "#Art"


def prepare_final_prompt(raw_prompt):
    # --- BURASI DEĞİŞTİ: STİL DAYATMASI YOK ---
    # Eski kodda burada "cinematic, 8k, masterpiece" gibi zorlamalar vardı.
    # Şimdi sadece teknik formatı (boyutunu) ayarlıyoruz. Stili yapay zeka belirledi.
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, high quality"
    )

# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    # Promptu son kez hazırla
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    current_key = HORDE_KEY if HORDE_KEY else "0000000000"
    headers = {"apikey": current_key, "Client-Agent": "MyTwitterBot:v7.0-FreeSpirit"}
    
    print("💎 Mod: Standart istek gönderiliyor...", flush=True)
    payload = {
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
        req = requests.post(generate_url, json=payload, headers=headers, timeout=30)
        
        if req.status_code != 202:
            error_msg = req.text
            print(f"⚠️ Hata: {error_msg[:100]}...", flush=True)
            
            # Eğer sunucu doluysa ayarları düşürüp tekrar dene
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Ekonomi Moduna geçiliyor...", flush=True)
                payload["params"]["post_processing"] = [] 
                payload["params"]["steps"] = 20 
                req = requests.post(generate_url, json=payload, headers=headers, timeout=30)
                if req.status_code != 202:
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
    print("🚀 Bot Başlatılıyor... (ÖZGÜR RUH MODU - SİNEMATİK ZORLAMASI YOK)", flush=True)
    
    # Fikir al
    prompt, caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Yapay Zekanın Hayal Ettiği:", prompt[:100] + "...", flush=True)
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
