import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy

# Tüm keyler GitHub Secrets'ten alınacak
GEMINI_API_KEY      = os.getenv("GEMINI_KEY")
CONSUMER_KEY        = os.getenv("API_KEY")
CONSUMER_SECRET     = os.getenv("API_SECRET")
ACCESS_TOKEN        = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET       = os.getenv("ACCESS_SECRET")
PIXELCUT_API_KEY    = os.getenv("PIXELCUT_API_KEY")

# Eksik key kontrolü
required = ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","PIXELCUT_API_KEY"]
missing = [x for x in required if not os.getenv(x)]
if missing:
    print(f"EKSİK KEYLER: {', '.join(missing)}")
    exit(1)

# ────────────────────────── GEMİNİ ──────────────────────────
def get_creative_content():
    print("Gemini düşünüyor...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        themes = ["Cyberpunk Tokyo","Cherry Blossom Forest","Interstellar Nebula","Crystal Cave","Floating Islands","Neon Arcade","Golden Desert","Underwater Ruins","Steampunk Airships","Aurora Iceland"]
        theme = random.choice(themes)
        resp = model.generate_content(f"Ultra detaylı Flux Realism prompt + kısa tweet caption. Tema: {theme}. Format: PROMPT: [...] ||| CAPTION: [...]").text.strip()
        prompt, caption = resp.split("|||")
        prompt = prompt.replace("PROMPT:", "").strip() + ", 8k, ultra sharp, masterpiece"
        caption = caption.replace("CAPTION:", "").strip()
        print(f"Tema: {theme}")
        return prompt, caption
    except Exception as e:
        print("Gemini fallback:", e)
        return "cyberpunk neon city night rain, ultra detailed, 8k", "Neon dreams 🌃✨ #AIArt"

# ────────────────────────── POLLİNATİONS ──────────────────────────
def download_base_image(prompt):
    print("Pollinations resim üretiyor...")
    url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?model=flux-realism&width=768&height=1344&nologo=true&enhance=true&seed={random.randint(1,999999)}"
    r = requests.get(url, timeout=90)
    return r.content if r.status_code == 200 and len(r.content) > 50000 else None

# ────────────────────────── PIXELCUT 4K ──────────────────────────
def pixelcut_upscale(img_bytes):
    print("Pixelcut 4x upscale yapıyor...")
    try:
        resp = requests.post(
            "https://api.pixelcut.ai/v1/image-upscaler/upscale",
            json={"image": base64.b64encode(img_bytes).decode(), "scale": 4},
            headers={"Authorization": f"Bearer {PIXELCUT_API_KEY}"},
            timeout=120
        )
        if resp.status_code == 200:
            url = resp.json().get("result_url")
            if url:
                return requests.get(url, timeout=60).content
    except: pass
    return None

# ────────────────────────── TWEET ──────────────────────────
def tweet_image(img_bytes, caption):
    fn = "wallpaper.jpg"
    open(fn, "wb").write(img_bytes)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=caption + " #AIArt #4K #Wallpaper", media_ids=[media.media_id])
    print("TWEET ATILDI!")
    os.remove(fn)

# ────────────────────────── ANA ──────────────────────────
if __name__ == "__main__":
    print("\n4K WALLPAPER BOT ÇALIŞIYOR\n")
    prompt, caption = get_creative_content()
    base = download_base_image(prompt)
    if not base: exit("Resim üretilemedi!")
    final = pixelcut_upscale(base) or base
    tweet_image(final, caption)
