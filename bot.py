import time
import requests
import tweepy
import random
import urllib.parse
import google.generativeai as genai
from datetime import datetime
from tweepy import OAuth1UserHandler, API, Client
import os  # <<< EKLENDİ: os.getenv için zorunlu

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
# 1. FİKİR ÜRETİCİ
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka sanatçı şapkasını taktı...", flush=True)
    
    past_topics = load_memory()
    past_topics_str = ", ".join(past_topics) if past_topics else "None"
    chaos_seed = random.randint(1, 999999999)
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    instruction_prompt = f"""
    Timestamp: {current_timestamp}
    Random Seed: {chaos_seed}

    ROLE: You are a VERSATILE Digital Artist with no fixed style.

    TASK: Create a phone wallpaper concept.
    RULE: YOU decide the art style freely (Anime, Minimalist, Pixel Art, Oil Painting, 3D, etc.).
    Avoid repeating past topics: [{past_topics_str}]

    Return exactly two lines:
    PROMPT: <detailed prompt with explicit art style>
    CAPTION: <short engaging tweet caption>
    """

    # PLAN A: GROQ (model adı güncellendi, daha stabillerden biri)
    if GROQ_KEY:
        try:
            print("🧠 Groq düşünüyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama3-70b-8192",  # <<< Daha güncel ve çalışan model
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.2
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                parts = content.split("CAPTION:")
                if len(parts) >= 2:
                    prompt_text = parts[0].replace("PROMPT:", "").strip()
                    caption_text = parts[1].strip()
                    save_to_memory(prompt_text[:50])
                    print("✅ Groq ile fikir bulundu!", flush=True)
                    return prompt_text, caption_text
        except Exception as e:
            print(f"Groq Hata: {e}", flush=True)

    # PLAN B: GEMINI
    if GEMINI_KEY:
        try:
            print("🧠 Gemini düşünüyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")  # <<< Daha güncel model
            response = model.generate_content(instruction_prompt, generation_config=genai.types.GenerationConfig(temperature=1.2))
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                prompt_text = parts[0].replace("PROMPT:", "").strip()
                caption_text = parts[1].strip()
                save_to_memory(prompt_text[:50])
                print("✅ Gemini ile fikir bulundu!", flush=True)
                return prompt_text, caption_text
        except Exception as e:
            print(f"Gemini Hata: {e}", flush=True)

    # Son çare
    return "A beautiful abstract phone wallpaper in vibrant colors", "Günlük duvar kağıdınız hazır! ✨ #AIArt"

def prepare_final_prompt(raw_prompt):
    return f"{raw_prompt}, vertical wallpaper, 9:21 aspect ratio, high quality"

# -----------------------------
# 2. AI HORDE
# -----------------------------
# (Bu kısım aynı, sadece küçük timeout artırımları ekleyebilirsin ama şimdilik dokunmadım)

# -----------------------------
# 3. TWITTER POST (ANA DÜZELTME BURADA)
# -----------------------------
def post_to_twitter(img_bytes, caption):
    filename = "wallpaper_mobile.png"
    try:
        with open(filename, "wb") as f:
            f.write(img_bytes)
        
        # <<< ANA DEĞİŞİKLİK: OAuth1 ile ayrı v1 API ve v2 Client oluştur >>>
        auth_v1 = OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        api_v1 = API(auth_v1, wait_on_rate_limit=True)  # wait_on_rate_limit ekledim, rate limit sorunu önler
        
        client_v2 = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True
        )

        print("📤 Medya yükleniyor (v1.1)...", flush=True)
        media = api_v1.media_upload(filename)
        print(f"✅ Medya yüklendi, ID: {media.media_id}", flush=True)

        print("🐦 Tweet atılıyor (v2)...", flush=True)
        client_v2.create_tweet(text=caption, media_ids=[media.media_id])
        print("🐦 TWEET BAŞARIYLA ATILDI!", flush=True)

    except Exception as e:
        print(f"❌ Twitter hatası: {e}", flush=True)
    finally:
        # Dosyayı temizle
        if os.path.exists(filename):
            os.remove(filename)
            print("🗑️ Geçici dosya silindi.", flush=True)

# -----------------------------
# ANA ÇALIŞTIRMA (örnek kullanım)
# -----------------------------
if __name__ == "__main__":
    prompt, caption = get_idea_ultimate()
    final_prompt = prepare_final_prompt(prompt)
    img_bytes = try_generate_image(final_prompt)  # Bu fonksiyonu kodunda zaten var
    if img_bytes:
        post_to_twitter(img_bytes, caption)
    else:
        print("Resim üretilemedi, tweet atılmadı.")
