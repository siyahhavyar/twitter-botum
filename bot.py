import os
import time
import requests
import tweepy
import random
from datetime import datetime
from tweepy import OAuthHandler, API, Client

# Google GenAI
try:
    import google.genai as genai
except ImportError:
    genai = None

# KEYS
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

print("🔑 Key Durumu:")
print(f"Twitter: {'Var' if API_KEY and ACCESS_TOKEN else 'Eksik!'}")
print(f"Gemini: {'Var' if GEMINI_KEY else 'Yok'}")
print(f"Groq: {'Var' if GROQ_KEY else 'Yok'}")

# -----------------------------
# HORDE KEYS - EN YÜKSEK KUDOS'LU SEÇ
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

HORDE_KEY = None
max_kudos = 0
print("🔍 Horde key'leri kontrol ediliyor...")

for key in HORDE_KEYS:
    try:
        info = requests.get("https://stablehorde.net/api/v2/find_user", headers={"apikey": key}, timeout=15).json()
        kudos = info.get("kudos", 0)
        username = info.get("username", "Bilinmeyen")
        print(f"   {key[:8]}... → {username} → {kudos} kudos")
        if kudos > max_kudos:
            max_kudos = kudos
            HORDE_KEY = key
    except:
        pass

if not HORDE_KEY:
    print("❌ Hiçbir key çalışmadı.")
    exit()

print(f"✅ Seçilen key: {HORDE_KEY[:8]}... ({max_kudos} kudos)")

if max_kudos < 30:
    print("⚠️ Kudos düşük (30+ önerilir), ama düşük maliyetli ayarlarla deniyoruz...")

# -----------------------------
# Hashtag
# -----------------------------
def get_hashtag():
    return random.choice(["#AIArt", "#DigitalArt", "#Wallpaper", "#FantasyArt", "#AnimeArt", "#PhoneWallpaper"])

# -----------------------------
# Fikir Üret
# -----------------------------
def get_idea():
    prompt_text = """
Creative mobile wallpaper artist.
One unique vertical phone wallpaper idea (anime, fantasy, mystery).
No adult.
Return exactly two lines:
PROMPT: <detailed English description>
CAPTION: <short poetic caption, max 100 chars>
"""
    if GROQ_KEY:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt_text}], "temperature": 1.3},
                timeout=30)
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content']
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                p = next((l[7:].strip() for l in lines if l.startswith("PROMPT:")), None)
                c = next((l[8:].strip() for l in lines if l.startswith("CAPTION:")), None)
                if p and c: return p, c
        except: pass

    return "Glowing anime character in mystical forest under stars", "Eternal Dream"

def final_prompt(p):
    return f"{p}, vertical phone wallpaper, highly detailed, beautiful lighting, masterpiece"

# -----------------------------
# Resim Üret - DÜŞÜK MALİYETLİ AYARLAR
# -----------------------------
def generate_image(prompt):
    payload = {
        "prompt": final_prompt(prompt),
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 7,
            "width": 512,      # Düşük çözünürlük
            "height": 1024,    # Dikey wallpaper için yeterli
            "steps": 20,       # Az step
            # post_processing kaldırıldı (maliyet düşsün)
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "AutonomousArtistBot"}

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=60)
        data = r.json()
        if not data.get("id"):
            print("❌ Horde reddetti:", data)
            return None

        task_id = data["id"]
        print(f"🖼️ Görev başladı (maliyet düşük, {task_id})")

        for _ in range(45):  # 15 dk max
            time.sleep(20)
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                print("✅ Resim hazır!")
                return requests.get(img_url, timeout=60).content

        print("⏰ Zaman aşımı")
        return None
    except Exception as e:
        print("❌ Hata:", e)
        return None

# -----------------------------
# Tweet At
# -----------------------------
def tweet_image(img_bytes, caption):
    text = f"{caption} #AIArt #Wallpaper #DigitalArt {get_hashtag()}"
    filename = "wallpaper.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    try:
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)
        client = Client(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        client.create_tweet(text=text, media_ids=[media.media_id])
        print("🎉 TWEET ATILDI!")
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# ANA
# -----------------------------
print("\n🚀 Bot başlıyor (düşük maliyet modu)...\n")

prompt, caption = get_idea()
print(f"🎨 Prompt: {prompt}")
print(f"💬 Caption: {caption}\n")

img = generate_image(prompt)

if img and tweet_image(img, caption):
    print("\n✅ Başarılı! Tweet atıldı.")
else:
    print("\n⚠️ Hala sorun var.")

print("\nBitti.")
