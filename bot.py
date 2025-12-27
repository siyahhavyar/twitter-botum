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
# 8 HORDE KEY - KUDOS KONTROLÜYLE SEÇİM
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
print("🔍 Horde key'leri kontrol ediliyor (kudos miktarı bakılıyor)...")

for key in HORDE_KEYS:
    try:
        # Kullanıcı bilgisi ve kudos miktarı
        info = requests.get(
            "https://stablehorde.net/api/v2/find_user",
            headers={"apikey": key, "Client-Agent": "AutonomousArtistBot"},
            timeout=15
        ).json()

        if info.get("kudos") is not None:
            kudos = info.get("kudos", 0)
            username = info.get("username", "Bilinmeyen")
            print(f"   {key[:8]}... → {username} → {kudos} kudos")

            if kudos >= 50:  # 44 maliyetli prompt için güvenli sınır
                HORDE_KEY = key
                print(f"✅ YETERLİ KUDOS BULUNDU: {key[:8]}... ({kudos} kudos)")
                break
    except Exception as e:
        print(f"   {key[:8]}... → Test hatası: {e}")

if not HORDE_KEY:
    print("❌ Hiçbir key'de yeterli kudos yok (en az 50 lazım).")
    print("   Çözüm: Yeni bir Horde hesabı açıp key al[](https://stablehorde.net/register)")
    print("   Veya mevcut hesaba kudos kazan (görev yaparak).")
    exit()  # Bot burada dursun, boşuna çalışmasın

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
You are a creative mobile wallpaper artist.
Create one unique, beautiful vertical phone wallpaper idea.
Inspiration: anime, fantasy, mystery, superheroes.
No adult content.
Return exactly two lines:
PROMPT: <detailed English description>
CAPTION: <short poetic caption, max 100 chars, no hashtags>
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

    if GEMINI_KEY and genai:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt_text)
            lines = [l.strip() for l in response.text.split('\n') if l.strip()]
            p = next((l[7:].strip() for l in lines if l.startswith("PROMPT:")), None)
            c = next((l[8:].strip() for l in lines if l.startswith("CAPTION:")), None)
            if p and c: return p, c
        except: pass

    return "A lone warrior standing on a cliff under a starry sky with aurora lights", "Eternal Vigil"

def final_prompt(p):
    return f"{p}, vertical phone wallpaper, 9:21 aspect ratio, masterpiece, highly detailed, cinematic lighting"

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
            "steps": 28,
            "post_processing": ["RealESRGAN_x4plus"]
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "AutonomousArtistBot"}

    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=60)
        data = r.json()

        if "message" in data:
            print(f"❌ Horde reddetti: {data['message']}")
            return None

        task_id = data.get("id")
        if not task_id:
            print("❌ Task ID alınamadı:", data)
            return None

        print(f"🖼️ Görev başladı (ID: {task_id}), resim bekleniyor...")
        
        for _ in range(60):  # 20 dakika max
            time.sleep(20)
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}").json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                print("✅ Resim tamamlandı!")
                return requests.get(img_url, timeout=60).content
            if status.get("faulted"):
                print("❌ Görev başarısız oldu.")
                return None

        print("⏰ Zaman aşımı (20 dk geçti)")
        return None
    except Exception as e:
        print("❌ Bağlantı hatası:", e)
        return None

# -----------------------------
# Tweet At
# -----------------------------
def tweet_image(img_bytes, caption):
    text = f"{caption} #AIArt #Wallpaper #DigitalArt #FantasyArt {get_hashtag()}"
    if len(text) > 280:
        text = text[:277] + "..."

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
        print("🎉 TWEET BAŞARIYLA ATILDI!")
        print(f"📝 {text}")
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {str(e)}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# ANA ÇALIŞMA
# -----------------------------
print("\n🚀 Autonomous Artist başlıyor...\n")

prompt, caption = get_idea()
print(f"🎨 Prompt: {prompt}")
print(f"💬 Caption: {caption}\n")

img = generate_image(prompt)

if img and tweet_image(img, caption):
    print("\n✅ Bot başarıyla tamamladı! Tweet atıldı.")
else:
    print("\n⚠️ Bir aşamada hata oldu.")

print("\nGitHub Actions bitti.")
