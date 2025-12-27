import os
import time
import requests
import tweepy
import random
import json
from datetime import datetime
from tweepy import OAuthHandler, API, Client

# Google GenAI - Güncel import
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
print("🔑 Horde key'leri test ediliyor...")

for key in HORDE_KEYS:
    try:
        response = requests.get(
            "https://stablehorde.net/api/v2/find_user",
            headers={"apikey": key, "Client-Agent": "AutonomousArtistBot"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("id"):
                HORDE_KEY = key
                print(f"✅ ÇALIŞAN KEY: {key[:8]}... (User: {data.get('username')})")
                break
    except:
        continue

if HORDE_KEY == "0000000000":
    print("⚠️ Horde key çalışmadı, anonim modda devam...")

# -----------------------------
# Güvenli Hashtag
# -----------------------------
def get_hashtag():
    tags = ["#AIArt", "#DigitalArt", "#Wallpaper", "#FantasyArt", "#AnimeArt", "#PhoneWallpaper"]
    return random.choice(tags)

# -----------------------------
# Fikir Üret
# -----------------------------
def get_idea():
    prompt_text = f"""
You are a creative mobile wallpaper artist. Create one unique, beautiful phone wallpaper idea.
No adult content. Inspired by anime, fantasy, mystery, superheroes.
Return exactly two lines:
PROMPT: <detailed English description>
CAPTION: <short poetic caption, max 100 chars, no hashtags>
"""
    # Groq öncelikli
    if GROQ_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": 1.3,
                    "max_tokens": 300
                },
                timeout=30
            )
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content']
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                p = next((l[7:].strip() for l in lines if l.startswith("PROMPT:")), None)
                c = next((l[8:].strip() for l in lines if l.startswith("CAPTION:")), None)
                if p and c:
                    return p, c
        except Exception as e:
            print(f"Groq hatası: {e}")

    # Gemini yedek
    if GEMINI_KEY and genai:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt_text)
            text = response.text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            p = next((l[7:].strip() for l in lines if l.startswith("PROMPT:")), None)
            c = next((l[8:].strip() for l in lines if l.startswith("CAPTION:")), None)
            if p and c:
                return p, c
        except Exception as e:
            print(f"Gemini hatası: {e}")

    # Fallback
    return (
        "Mysterious anime girl with glowing eyes under cherry blossoms at night",
        "Whispers in the moonlight"
    )

def final_prompt(text):
    return f"{text}, vertical phone wallpaper, 9:21 ratio, beautiful lighting, high detail, aesthetic"

# -----------------------------
# Resim Üret
# -----------------------------
def generate_image(prompt):
    payload = {
        "prompt": final_prompt(prompt),
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 7,
            "width": 640,
            "height": 1408,
            "steps": 30,
            "post_processing": ["RealESRGAN_x4plus"]
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "AutonomousArtistBot"}

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            print("Horde hatası:", r.json())
            return None
        task_id = r.json().get("id")
        if not task_id:
            return None

        print("🖼️ Resim sıraya alındı, bekleniyor... (max 15 dk)")
        for _ in range(45):  # 15 dakika max
            time.sleep(20)
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                return requests.get(img_url, timeout=60).content
        print("⏰ Zaman aşımı, resim gelmedi.")
        return None
    except Exception as e:
        print("Horde bağlantı hatası:", e)
        return None

# -----------------------------
# Tweet At
# -----------------------------
def tweet_image(img_bytes, caption):
    tag = get_hashtag()
    text = f"{caption} #Wallpaper #DigitalArt #AIArt #PhoneWallpaper {tag}"
    if len(text) > 280:
        text = text[:277] + "..."

    filename = "art.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    try:
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)

        client = Client(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        client.create_tweet(text=text, media_ids=[media.media_id])

        print("🎉 TWEET BAŞARIYLA ATILDI!")
        print(f"Metin: {text}")
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {str(e)}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# ANA ÇALIŞMA - SADECE 1 KEZ
# -----------------------------
print("🚀 Tek seferlik Autonomous Artist başlatılıyor...\n")

prompt, caption = get_idea()
print(f"🎨 Fikir: {prompt}")
print(f"💬 Caption: {caption}\n")

img = generate_image(prompt)

if img:
    print("📤 Tweet gönderiliyor...")
    if tweet_image(img, caption):
        print("\n✅ Her şey tamam! Bot başarıyla çalıştı.")
    else:
        print("\n⚠️ Tweet atılamadı ama resim üretildi.")
else:
    print("\n⚠️ Resim üretilemedi.")

print("\nBot bitti. GitHub Actions tamamlandı.")
