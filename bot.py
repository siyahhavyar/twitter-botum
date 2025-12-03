import os
import requests
import random
import google.generativeai as genai
import tweepy

# GEREKLİ KEYLER
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

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
        prompt = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper, 9:16, ultra detailed, 8k"
        caption = "Whispers of spring"
    
    return prompt, caption

# BASEDLABS – %100 ÜCRETSİZ HD (No signup/key, 1024x1792 dikey!)
def basedlabs_image(prompt):
    print("BasedLabs ile 1024x1792 dikey wallpaper üretiliyor (ücretsiz, no key)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://basedlabs.ai/api/generate?prompt={encoded}&aspect=9:16&width=1024&height=1792&model=flux&quality=high"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/*",
        "Referer": "https://basedlabs.ai/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"BasedLabs status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("BASEDLABS → DİKEY HD WALLPAPER HAZIR!")
                return img
        else:
            print(f"BasedLabs error: {r.text[:200]}")
    except Exception as e:
        print(f"BasedLabs exception: {e}")
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
    print("\nBASEDLABS %100 ÜCRETSİZ WALLPAPER BOTU ÇALIŞIYOR!\n")
    
    prompt, caption = get_completely_random_wallpaper()
    print(f"Fikir: {caption}")
    print(f"Prompt: {prompt[:120]}...\n")
    
    img = basedlabs_image(prompt)
    if not img:
        print("Bugün bir hata oldu, yarın tekrar dene :)")
        exit(1)
    
    tweet(img, caption)
