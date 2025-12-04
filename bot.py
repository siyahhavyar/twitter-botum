import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# SADECE BUNLAR LAZIM (No Horde, only Perchance)
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

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Yapay zeka kendi seçsin (no fixed themes)
    instruction = """
    You are a creative wallpaper designer.
    Come up with a random beautiful theme (nature, fantasy, minimal, cozy, etc.).
    STRICTLY FORBIDDEN: cyberpunk, technology, city, sci-fi, digital art.
    Then create an ultra detailed photorealistic English prompt for a vertical phone wallpaper (9:16 ratio).
    Add a short English caption.
    Format: PROMPT: [...] ||| CAPTION: [...]
    """
    
    resp = model.generate_content(instruction).text.strip()
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", vertical phone wallpaper, 9:16 ratio, ultra detailed, sharp focus, high resolution, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "beautiful mountain landscape, vertical phone wallpaper, 9:16 ratio, ultra detailed, 8k"
        caption = "Mountain serenity"
    return prompt, caption

# PERCHANCE – ÜCRETSİZ HD (Portrait 1024x1792, header bypass)
def perchance_image(prompt):
    print("Perchance ile ücretsiz 1024x1792 PORTRAIT resim üretiliyor...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://perchance.org/ai-text-to-image-generator",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    } 
    try:
        r = requests.get(url, headers=headers, timeout=60)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("1024x1792 PORTRAIT RESİM HAZIR! (Perchance free kalite)")
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
    print("TWEET BAŞARIYLA ATILDI!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nPERCHANCE ÜCRETSİZ PORTRAIT BOT ÇALIŞIYOR (Yapay Zeka Kendi Seçiyor!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")
    
    img = perchance_image(prompt)
    if not img:
        print("Resim üretilemedi → Tweet atılmadı")
        exit(1)
    tweet(img, caption)
