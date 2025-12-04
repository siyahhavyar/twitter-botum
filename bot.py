import os
import requests
import random
import google.generativeai as genai
import tweepy
import cloudscraper  # Cloudflare bypass

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

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    resp = model.generate_content(
        "Generate a random beautiful landscape or fantasy theme. Then create an ultra detailed photorealistic English prompt for it, and a short English tweet caption. "
        "Format: THEME: [...] ||| PROMPT: [...] ||| CAPTION: [...]"
    ).text.strip()
    try:
        parts = resp.split("|||")
        theme = parts[0].replace("THEME:", "").strip()
        prompt = parts[1].replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, high resolution 1024x1024, 8k masterpiece, cinematic lighting"
        caption = parts[2].replace("CAPTION:", "").strip()
    except:
        theme = "Beautiful mountain landscape"
        prompt = "beautiful mountain landscape, ultra detailed, high resolution 1024x1024, 8k"
        caption = "Mountain serenity"
    print(f"Generated Theme: {theme}")
    return prompt, caption

# PERCHANCE – FREE HD (403 fix: Cloudscraper for bypass)
def perchance_image(prompt):
    print("Generating free 1024x1024 HD image with Perchance (no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1024x1024&quality=high&seed={random.randint(1,100000)}&model=flux"
    scraper = cloudscraper.create_scraper()  # Cloudflare 403 bypass
    try:
        r = scraper.get(url, timeout=60)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("1024x1024 HD IMAGE READY! (Perchance free quality)")
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
    print("\nPERCHANCE FREE HD BOT RUNNING (No signup/credit, 403 fixed with cloudscraper!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = perchance_image(prompt)
    if not img:
        print("Image generation failed → Tweet not posted")
        exit(1)
    tweet(img, caption)
