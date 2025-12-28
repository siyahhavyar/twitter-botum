import os
import time
import requests
import tweepy
import random
from datetime import datetime
from tweepy import OAuth1UserHandler, API, Client

# KEYS
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

print("🔑 Key Durumu:")
print(f"Twitter: {'Var' if API_KEY and ACCESS_TOKEN else 'Eksik!'}")
print(f"Groq: {'Var' if GROQ_KEY else 'Yok'}")

if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_SECRET):
    print("❌ Twitter key'leri eksik!")
    exit()

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
    except Exception as e:
        print(f"   {key[:8]}... → Hata: {e}")

if not HORDE_KEY:
    print("❌ Hiçbir Horde key çalışmadı.")
    exit()

print(f"✅ Seçilen key: {HORDE_KEY[:8]}... ({max_kudos} kudos)")

# -----------------------------
# Hashtag'ler
# -----------------------------
def get_hashtag():
    return random.choice(["#AIArt", "#DigitalArt", "#Wallpaper", "#FantasyArt", "#AnimeArt", "#PhoneWallpaper", "#AIGenerated"])

def get_etsy_hashtag():
    return random.choice(["#Etsy", "#EtsySeller", "#EtsyFinds", "#DigitalDownload", "#EtsyArt"])

# -----------------------------
# Fikir Üret
# -----------------------------
def get_idea():
    prompt_text = """
Creative mobile wallpaper artist.
One unique vertical phone wallpaper idea (anime, fantasy, mystery, dark aesthetic).
No adult or NSFW.
Return exactly two lines:
PROMPT: <detailed English description>
CAPTION: <short poetic caption, max 80 chars>
"""
    if GROQ_KEY:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": 1.2,
                    "max_tokens": 300
                },
                timeout=45)
            if r.status_code == 200:
                content = r.json()['choices'][0]['message']['content'].strip()
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                p = next((l.partition("PROMPT:")[2].strip() for l in lines if "PROMPT:" in l), None)
                c = next((l.partition("CAPTION:")[2].strip() for l in lines if "CAPTION:" in l), None)
                if p and c:
                    return p, c
        except Exception as e:
            print(f"Groq hatası: {e}")

    # Fallback
    return "Mysterious anime silhouette under blood moon in ancient dark forest", "Shadows Whisper"

def final_prompt(p):
    return f"{p}, vertical phone wallpaper 9:19 ratio, highly detailed, intricate, beautiful dark lighting, masterpiece, best quality"

# -----------------------------
# Resim Üret
# -----------------------------
def generate_image(prompt):
    payload = {
        "prompt": final_prompt(prompt),
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 7,
            "width": 512,
            "height": 1024,
            "steps": 20,
            "karras": True
        },
        "nsfw": False,
        "censor_nsfw": True,
        "trusted_workers": False,
        "slow_workers": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "SiyahHavyarBot:1.0"}

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=60)
        data = r.json()
        if not data.get("id"):
            print("❌ Horde reddetti:", data)
            return None

        task_id = data["id"]
        print(f"🖼️ Görev başladı: {task_id}")

        for _ in range(60):
            time.sleep(20)
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", headers=headers).json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                print("✅ Resim hazır!")
                return requests.get(img_url, timeout=60).content

        print("⏰ Zaman aşımı")
        return None
    except Exception as e:
        print("❌ Horde hatası:", e)
        return None

# -----------------------------
# Tweet At + Etsy Tanıtımı
# -----------------------------
def tweet_image(img_bytes, caption):
    # Etsy promosyon varyasyonları (rastgele seçilsin, spam olmasın)
    promo_options = [
        "🖤 Get this as instant digital download on my Etsy!",
        "✨ Available now on Etsy – instant download!",
        "🌙 Download this wallpaper instantly from my Etsy shop!",
        "🔗 High-res version on Etsy – link below!",
        "💎 Grab the full quality version on Etsy!"
    ]
    promo_text = random.choice(promo_options)
    
    text = f"{caption}\n\n{promo_text}\n👉 https://www.etsy.com/shop/SiyahHavyarArt\n\n{get_hashtag()} {get_hashtag()} {get_etsy_hashtag()} #AIArt #Wallpaper #DigitalArt"
    
    filename = "siyahhavyar_wallpaper.png"
    
    try:
        with open(filename, "wb") as f:
            f.write(img_bytes)

        # v1.1 media upload
        auth_v1 = OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        api_v1 = API(auth_v1)
        media = api_v1.media_upload(filename)
        
        # v2 tweet
        client = Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
        client.create_tweet(text=text, media_ids=[media.media_id_string])
        
        print("🎉 TWEET ATILDI! Etsy linkli ✨")
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
print("\n🚀 Siyah Havyar Art Bot başlıyor... (Etsy promosyonlu)\n")

prompt, caption = get_idea()
print(f"🎨 Prompt: {prompt}")
print(f"💬 Caption: {caption}\n")

img = generate_image(prompt)

if img and tweet_image(img, caption):
    print("\n✅ Başarı! Etsy linkli tweet atıldı.")
else:
    print("\n⚠️ Bir sorun oldu, kontrol et.")

print("\nBitti. Siyah Havyar büyüyor! 🖤")
