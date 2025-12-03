import os
import requests
import random
import google.generativeai as genai
import tweepy

# KEYS
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

# PERCHANCE – PRIMARY (Enhanced 403 fix)
def perchance_image(prompt):
    print("Generating with Perchance (primary, free)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1080x1920&quality=high&seed={random.randint(1,999999)}&model=flux"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://perchance.org/ai-text-to-image-generator",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 80000:
                print("PERCHANCE → VERTICAL HD READY!")
                return img
        else:
            print(f"Perchance error: {r.text[:200]}")
    except Exception as e:
        print(f"Perchance exception: {e}")
    return None

# DEZGO – BACKUP (Web endpoint scraping for image)
def dezgo_image(prompt):
    print("Switching to Dezgo backup (free)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://dezgo.com/?prompt={encoded}&aspect=portrait&width=1080&height=1920&model=flux"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://dezgo.com/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"Dezgo status: {r.status_code}")
        # Scrape for image URL (from HTML)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')
            img_tag = soup.find('img', {'class': 'generated-image'})
            if img_tag:
                img_url = img_tag['src']
                img = requests.get(img_url, timeout=60).content
                if len(img) > 80000:
                    print("DEZGO → VERTICAL HD READY!")
                    return img
        else:
            print(f"Dezgo error: {r.text[:200]}")
    except Exception as e:
        print(f"Dezgo exception: {e}")
    return None

# VHEER – 3. YEDEK (No signup, portrait support)
def vheer_image(prompt):
    print("Switching to Vheer backup (free, no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://vheer.com/api/generate?prompt={encoded}&format=portrait&width=1080&height=1920"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "image/*",
        "Referer": "https://vheer.com/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"Vheer status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 80000:
            print("VHEER → VERTICAL HD READY!")
            return r.content
    except Exception as e:
        print(f"Vheer exception: {e}")
    return None

# FLATAI – 4. YEDEK (Free/no login, vertical)
def flatai_image(prompt):
    print("Switching to Flatai backup (free, portrait)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://flatai.org/api/image?prompt={encoded}&aspect=portrait&width=1080&height=1920"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/*",
        "Referer": "https://flatai.org/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"Flatai status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 80000:
            print("FLATAI → VERTICAL HD READY!")
            return r.content
    except Exception as e:
        print(f"Flatai exception: {e}")
    return None

# WRITECREAM – 5. YEDEK (100% free, no login)
def writecream_image(prompt):
    print("Switching to Writecream backup (free, no login)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://www.writecream.com/api/ai-image-generator?prompt={encoded}&aspect=portrait&width=1080&height=1920"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "image/*",
        "Referer": "https://www.writecream.com/ai-image-generator-free-no-sign-up/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"Writecream status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 80000:
            print("WRITECREAM → VERTICAL HD READY!")
            return r.content
    except Exception as e:
        print(f"Writecream exception: {e}")
    return None

# RAPHAELAI – 6. YEDEK (Unlimited, no signup)
def raphaelai_image(prompt):
    print("Switching to RaphaelAI backup (unlimited, free)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://raphaelai.org/api/generate?prompt={encoded}&aspect=portrait&width=1080&height=1920"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/*",
        "Referer": "https://raphaelai.org/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=90)
        print(f"RaphaelAI status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 80000:
            print("RAPHAELAI → VERTICAL HD READY!")
            return r.content
    except Exception as e:
        print(f"RaphaelAI exception: {e}")
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
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=caption + " #Wallpaper #Aesthetic #Nature #Art", media_ids=[media.media_id])
    print("TWEET SUCCESSFULLY POSTED!")
    os.remove(fn)

# MAIN
if __name__ == "__main__":
    print("\nPERCHANCE + 5 FREE BACKUPS VERTICAL BOT RUNNING!\n")
    
    prompt, caption = get_completely_random_wallpaper()
    print(f"Idea: {caption}")
    print(f"Prompt: {prompt[:120]}...\n")
    
    img = perchance_image(prompt)
    if not img:
        img = dezgo_image(prompt)
    if not img:
        img = vheer_image(prompt)
    if not img:
        img = flatai_image(prompt)
    if not img:
        img = writecream_image(prompt)
    if not img:
        img = raphaelai_image(prompt)
    if not img:
        print("Image generation failed today, try again tomorrow :)")
        exit(1)
    
    tweet(img, caption)
