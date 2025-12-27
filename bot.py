import os
import time
import requests
import tweepy
import random
import json
from datetime import datetime
from tweepy import OAuthHandler, API, Client

# Google GenAI için DOĞRU ve GÜNCEL import (uyarı kalktı)
try:
    import google.genai as genai
except ImportError:
    genai = None

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# Key kontrolü (log'da görünsün)
print("🔑 Key Durumu:")
print(f"Twitter API Key: {'Var' if API_KEY else 'YOK'}")
print(f"Twitter Access Token: {'Var' if ACCESS_TOKEN else 'YOK'}")
print(f"Gemini Key: {'Var' if GEMINI_KEY else 'YOK'}")
print(f"Groq Key: {'Var' if GROQ_KEY else 'YOK'}")

# -----------------------------
# HORDE KEYS
# -----------------------------
HORDE_KEYS = [
    "cQ9Kty7vhFWfD8nddDOq7Q",
    "ceIr0GFCjybUk_3ItTju0w",
    "_UZ8x88JEw4_zkIVI1GkpQ",
    "8PbI2lLTICOUMLE4gKzb0w",
    "SwxAZZWFvruz8ugHkFJV5w",
    "AEFG4kHNWHKPCWvZlEjVUg",
    "Q-zqB1m-7kjc5pywX52uKg"
]

HORDE_KEY = "0000000000"
print("🔑 Horde key'leri test ediliyor...", flush=True)

for key in HORDE_KEYS:
    try:
        test_url = "https://stablehorde.net/api/v2/find_user"
        headers = {"apikey": key, "Client-Agent": "AutonomousArtistBot"}
        response = requests.get(test_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("id") and data.get("id") != 0:
                HORDE_KEY = key
                print(f"✅ ÇALIŞAN KEY BULUNDU: {key[:8]}... (User: {data.get('username')})", flush=True)
                break
    except Exception as e:
        print(f"❌ Key testi hatası: {key[:8]}... → {str(e)}")
        continue

if HORDE_KEY == "0000000000":
    print("⚠️ Hiçbir key doğrulanamadı, anonim modda devam ediliyor...", flush=True)

# -----------------------------
# Güvenli Hashtag (trend API sorunlu olduğu için)
# -----------------------------
SAFE_HASHTAGS = ["#AIArt", "#DigitalArt", "#Wallpaper", "#FantasyArt", "#AnimeArt", "#MobileWallpaper", "#Art", "#Illustration"]

def get_current_trending_hashtag():
    return random.choice(SAFE_HASHTAGS)

# -----------------------------
# Memory (geçmiş paylaşımlar) - Güvenli
# -----------------------------
MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)
    except:
        pass

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_memory(item):
    try:
        memory = load_memory()
        memory.append(item)
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)
    except Exception as e:
        print(f"⚠️ Memory kaydedilemedi: {e}")

def is_duplicate(prompt):
    try:
        memory = load_memory()
        return prompt in memory
    except:
        return False

# -----------------------------
# 1. Fikir Üretici
# -----------------------------
def get_idea_ultimate():
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    instruction_prompt = f"""
You are an imaginative mobile wallpaper artist.
Today's date: {current_timestamp}
You have complete creative freedom. Create unique, original phone wallpapers.
Draw inspiration from popular culture, anime, fantasy, superheroes, supernatural, and mysterious characters.
Exclude adult (18+) content.
Return exactly two lines:
PROMPT: <English description of your creative wallpaper idea, including composition, colors, lighting, mood, references if any.>
CAPTION: <Short poetic tweet caption (max 140 chars), no hashtags.>
"""
    # Groq
    if GROQ_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.4,
                "top_p": 0.95,
                "max_tokens": 500
            }
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content']
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                prompt_line = next((l for l in lines if l.startswith("PROMPT:")), None)
                caption_line = next((l for l in lines if l.startswith("CAPTION:")), None)
                if prompt_line and caption_line:
                    return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"⚠️ Groq hatası: {e}")

    # Gemini
    if GEMINI_KEY and genai:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                instruction_prompt,
                generation_config=genai.types.GenerationConfig(temperature=1.3, top_p=0.95, max_output_tokens=500)
            )
            text = response.text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            prompt_line = next((l for l in lines if l.startswith("PROMPT:")), None)
            caption_line = next((l for l in lines if l.startswith("CAPTION:")), None)
            if prompt_line and caption_line:
                return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"⚠️ Gemini hatası: {e}")

    # Fallback
    fallback_prompts = [
        "A mysterious anime character under a glowing moon",
        "A superhero silhouette in soft pastel clouds",
        "Fantasy forest with floating lanterns",
        "Mystical creature in a foggy night scene",
        "Ethereal character in a vibrant aurora sky"
    ]
    fallback_captions = ["mystery unfolds", "dreams take flight", "beyond the shadows", "magic whispers", "enchanting night"]
    return random.choice(fallback_prompts), random.choice(fallback_captions)

def prepare_final_prompt(prompt):
    return f"{prompt}, vertical phone wallpaper, 9:21 aspect ratio, soft lighting, subtle colors, clean design, negative space"

# -----------------------------
# 2. AI HORDE GENERATION
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    unique_seed = str(random.randint(1, 9999999999))
    payload = {
        "prompt": final_prompt,
        "params": {"sampler_name":"k_dpmpp_2m","cfg_scale":7,"width":640,"height":1408,"steps":30,"seed":unique_seed,"post_processing":["RealESRGAN_x4plus"]},
        "nsfw": False, "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "AutonomousArtistBot"}

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            print("⚠️ Horde async hatası:", r.json())
            return None
        task_id = r.json().get("id")
        if not task_id:
            print("⚠️ Task ID alınamadı:", r.json())
            return None
    except Exception as e:
        print("⚠️ Horde istek hatası:", e)
        return None

    wait_time = 0
    while wait_time < 1800:
        time.sleep(20)
        wait_time += 20
        try:
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                return requests.get(img_url, timeout=60).content
        except Exception as e:
            print("⚠️ Status kontrol hatası:", e)
    print("⚠️ Horde zaman aşımı (30 dk)")
    return None

# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
    trending_tag = get_current_trending_hashtag()
    hashtags = "#Wallpaper #DigitalArt #PhoneWallpaper #FantasyArt #Anime"
    final_caption = f"{caption} {hashtags} {trending_tag}"
    if len(final_caption) > 280:
        final_caption = final_caption[:277] + "..."

    filename = "wallpaper.png"
    try:
        with open(filename, "wb") as f:
            f.write(img_bytes)

        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth, wait_on_rate_limit=True)
        
        media = api.media_upload(filename)
        
        client = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        
        client.create_tweet(text=final_caption, media_ids=[media.media_id])
        print("🐦 TWEET BAŞARIYLA ATILDI!")
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {str(e)}")
        return False
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

# -----------------------------
# MAIN LOOP - TEST MODU (60 saniye bekleme)
# -----------------------------
if __name__ == "__main__":
    print("🚀 Autonomous Artist Bot başlatıldı - TEST MODU (60 sn bekleme)")
    
    # İlk çalıştırmada duplicate kontrolünü atla (hemen paylaşsın)
    first_run = True
    
    while True:
        try:
            prompt, caption = get_idea_ultimate()
            print(f"🎨 Yeni fikir: {prompt[:80]}...")

            # İlk çalıştırmada duplicate olsa bile paylaş
            if is_duplicate(prompt) and not first_run:
                print("⚠️ Bu prompt daha önce kullanıldı, yenisi üretiliyor...")
                time.sleep(10)
                continue

            print("🖼️ Resim üretiliyor (AI Horde ile)...")
            img = try_generate_image(prompt)

            if img:
                print("📤 Tweet atılıyor...")
                if post_to_twitter(img, caption):
                    save_memory(prompt)
                    print("✅ Paylaşım başarılı!")
                else:
                    print("⚠️ Tweet atılamadı.")
            else:
                print("⚠️ Resim üretilemedi.")

            first_run = False

        except Exception as e:
            print(f"🔥 Genel hata: {str(e)}")

        print("⏳ Bir sonraki paylaşım için 60 saniye bekleniyor... (Test modu)")
        print("   Gerçek kullanımda bunu 7200 yap: time.sleep(7200)\n")
        
        time.sleep(60)  # TEST İÇİN 60 SANİYE
        
        # Gerçek kullanımda şu satırı aç:
        # time.sleep(7200)  # 2 saat
