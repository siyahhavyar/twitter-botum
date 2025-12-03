import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# GEREKLİ KEYLER
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"

# Eksik kontrol
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_completely_random_wallpaper():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    instruction = """
    You are a creative phone wallpaper artist.
    Come up with ONE completely original, beautiful, aesthetic wallpaper idea.
    
    Allowed styles (only these):
    - nature, forest, mountains, ocean, sunset, flowers, animals
    - fantasy forest, magical creatures, fairy tale, enchanted
    - minimal, pastel, cozy, soft colors, dreamy
    - vintage, retro, polaroid, old film
    - abstract watercolor, ink art, soft shapes
    - surreal landscapes, floating islands, clouds
    - cottagecore, garden, books, coffee, candles

    STRICTLY FORBIDDEN:
    - cyberpunk, neon, technology, robot, city, sci-fi, futuristic, digital art, glitch

    Must be vertical phone wallpaper (9:16).
    Output ONLY in English.
    Format exactly:
    PROMPT: [ultra detailed English prompt] ||| CAPTION: [short beautiful English caption]
    """
    
    try:
        resp = model.generate_content(instruction).text.strip()
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, 8k, soft natural lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        # Güvenli yedek
        prompt = "soft pastel cherry blossom forest with glowing fireflies at twilight, vertical phone wallpaper, 9:16, ultra detailed, 8k"
        caption = "Whispers of spring"
    
    return prompt, caption

# PERCHANCE – 1080x1920 DİKEY
def perchance_image(prompt):
    print("Perchance ile dikey wallpaper üretiliyor (tamamen özgün)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1080x1920&quality=high&seed={random.randint(1,999999)}&model=flux"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://perchance.org/ai-text-to-image-generator",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        if r.status_code == 200 and len(r.content) > 80000:
            print("PERCHANCE → DİKEY WALLPAPER HAZIR!")
            return r.content
    except Exception as e:
        print(f"Perchance hatası: {e}")
    return None

# HORDE – YEDEK
def horde_image(prompt):
    print("Horde ile dikey wallpaper üretiliyor (yedek)...")
    try:
        r = requests.post(
            "https://stablehorde.net/api/v2/generate/async",
            headers={"apikey": HORDE_API_KEY},
            json={"prompt": prompt, "params": {"width": 768, "height": 1344, "steps": 25, "n": 1}},
            timeout=30
        )
        if r.status_code != 202: return None
        job_id = r.json()["id"]
        for _ in range(180):
            time.sleep(6)
            check = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}").json()
            if check.get("done"):
                img_url = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}").json()["generations"][0]["img"]
                return requests.get(img_url).content
    except: pass
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "wallpaper.jpg"
    open(fn, "wb").write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=caption + " #Wallpaper #Aesthetic #Nature #Art", media_ids=[media.media_id])
    print("TWEET GÖNDERİLDİ!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nTAMAMEN OTOMATİK WALLPAPER BOTU ÇALIŞIYOR (YAPAY ZEKA KENDİ DÜŞÜNÜYOR!)\n")
    
    prompt, caption = get_completely_random_wallpaper()
    print(f"Bu seferki fikir → {caption}")
    print(f"Prompt: {prompt[:120]}...\n")
    
    img = perchance_image(prompt) or horde_image(prompt)
    if not img:
        print("Bugün şanssız günümüz, yarın tekrar dene :)")
        exit(1)
    
    tweet(img, caption)
