import os
import time
import requests
import tweepy
import random

try:
    import google.genai as genai
except ImportError:
    genai = None

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
GROQ_KEY      = os.getenv("GROQ_API_KEY")

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
        r = requests.get(
            "https://stablehorde.net/api/v2/find_user",
            headers={"apikey": key, "Client-Agent": "MyTwitterBot:v6.0"},
            timeout=10
        )
        if r.status_code == 200 and r.json().get("id"):
            HORDE_KEY = key
            print(f"✅ Aktif Horde Key: {key[:8]}...", flush=True)
            break
    except:
        continue

# -----------------------------
# TREND HASHTAG
# -----------------------------

def get_current_trending_hashtag():
    try:
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        trends = api.get_place_trends(1)
        tags = [t["name"] for t in trends[0]["trends"] if t["name"].startswith("#")]
        return random.choice(tags[:5]) if tags else "#Art"
    except:
        return "#Art"

# -----------------------------
# IDEA GENERATOR (AI KENDİ DÜŞÜNÜR)
# -----------------------------

def get_idea_ultimate():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    instruction_prompt = f"""
You are a creative AI artist specializing in minimal, atmospheric mobile wallpapers.

STYLE:
- Minimal composition
- Anime-inspired aesthetics
- Fantasy, supernatural, mysterious themes
- Witches, sorcerers, masked figures, superheroes (original only)
- Dark fantasy, ethereal, cinematic lighting
- Calm but powerful mood
- Clean background, strong negative space

AVOID COMPLETELY:
- Geometry
- Abstract shapes
- Tech UI
- Flat vector style
- Crowded scenes

RULES:
- NO NSFW
- NO nudity
- NO sexual content
- NO violence or gore
- No real people
- No copyrighted characters by name

You decide what to create today.
Design for vertical phone wallpaper (9:21).

Output EXACTLY two lines:

PROMPT: <Detailed English image description including character, mood, lighting, colors, atmosphere>
CAPTION: <Short, poetic, mysterious English caption. Max 140 chars. No hashtags>
"""

    # GROQ
    if GROQ_KEY:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": instruction_prompt}],
                    "temperature": 1.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            text = r.json()["choices"][0]["message"]["content"]
        except:
            text = ""
    else:
        text = ""

    if not text and GEMINI_KEY and genai:
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            text = model.generate_content(instruction_prompt).text
        except:
            text = ""

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    p = next(l for l in lines if l.startswith("PROMPT:"))[7:]
    c = next(l for l in lines if l.startswith("CAPTION:"))[8:]
    return p.strip(), c.strip()

def prepare_prompt(p):
    return f"{p}, minimal, vertical wallpaper, 9:21, cinematic lighting, high quality"

# -----------------------------
# IMAGE GENERATION
# -----------------------------

def generate_image(prompt):
    payload = {
        "prompt": prepare_prompt(prompt),
        "params": {"width": 640, "height": 1408, "steps": 25},
        "nsfw": False,
        "models": ["Juggernaut XL"]
    }

    r = requests.post(
        "https://stablehorde.net/api/v2/generate/async",
        headers={"apikey": HORDE_KEY},
        json=payload
    )

    task = r.json()["id"]

    while True:
        time.sleep(20)
        s = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task}").json()
        if s["done"] and s["generations"]:
            return requests.get(s["generations"][0]["img"]).content

# -----------------------------
# POST TO TWITTER
# -----------------------------

def post(img, caption):
    tag = get_current_trending_hashtag()
    text = f"{caption} #MinimalArt #AnimeArt #FantasyArt {tag}"

    with open("img.png", "wb") as f:
        f.write(img)

    auth = OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = API(auth)
    media = api.media_upload("img.png")

    client = Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    client.create_tweet(text=text[:280], media_ids=[media.media_id])
    os.remove("img.png")

# -----------------------------
# MAIN LOOP (2 SAATTE 1)
# -----------------------------

if __name__ == "__main__":
    print("🚀 Bot başladı – 2 saatte bir paylaşım", flush=True)

    while True:
        try:
            prompt, caption = get_idea_ultimate()
            img = generate_image(prompt)
            post(img, caption)
            print("✅ Paylaşıldı. 2 saat bekleniyor...", flush=True)
        except Exception as e:
            print(f"⚠️ Hata: {e}", flush=True)

        time.sleep(7200)  # 2 SAAT
