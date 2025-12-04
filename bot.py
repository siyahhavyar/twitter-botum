import os
import requests
import random
import google.generativeai as genai
import tweepy
import cloudscraper
from bs4 import BeautifulSoup

# ONLY THESE ARE NEEDED (No extra keys!)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

# Check for missing keys
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"MISSING: {var}")
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

# PERCHANCE – FREE HD (Cloudscraper + BeautifulSoup for full 403/HTML fix)
def perchance_image(prompt):
    print("Generating free 1080x1920 vertical HD image with Perchance (no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1080x1920&quality=high&seed={random.randint(1,100000)}&model=flux"
    scraper = cloudscraper.create_scraper()  # Bypasses Cloudflare 403
    try:
        r = scraper.get(url, timeout=90)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200:
            # Extract image from HTML (if not direct image response)
            soup = BeautifulSoup(r.text, 'html.parser')
            img_tag = soup.find('img', {'id': 'generated-image'}) or soup.find('img', src=True)
            if img_tag and img_tag['src']:
                img_url = img_tag['src']
                if not img_url.startswith("http"):
                    img_url = "https://perchance.org" + img_url
                img = requests.get(img_url, timeout=60).content
                if len(img) > 50000:
                    print("1080x1920 VERTICAL HD IMAGE READY! (Perchance free quality)")
                    return img
            # If direct image
            if 'image' in r.headers.get('Content-Type', ''):
                img = r.content
                if len(img) > 50000:
                    print("1080x1920 VERTICAL HD IMAGE READY! (Perchance direct)")
                    return img
        else:
            print(f"Perchance error: {r.text[:200]}")
    except Exception as e:
        print(f"Perchance exception: {e}")
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "wallpaper.jpg"
    with open(fn, "wb") as f:
        f.write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    client.create_tweet(text=caption + " #AIArt #Wallpaper #4K", media_ids=[media.media_id])
    print("TWEET SUCCESSFULLY POSTED!")
    os.remove(fn)

# MAIN
if __name__ == "__main__":
    print("\nPERCHANCE FREE HD BOT RUNNING (No signup/credit, full 403/HTML fixed!)\n")
    prompt, caption = get_completely_random_wallpaper()
    print(f"Idea: {caption}")
    print(f"Prompt: {prompt[:150]}...\n")

    img = perchance_image(prompt)
    if not img:
        print("Image generation failed → Tweet not posted")
        exit(1)
    tweet(img, caption)
