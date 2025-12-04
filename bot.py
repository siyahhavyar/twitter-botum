import os
import requests
import random
import google.generativeai as genai
import tweepy
from bs4 import BeautifulSoup  # HTML scraping for image URL
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
    themes = ["Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Steampunk City","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Theme: {theme} → ultra detailed photorealistic prompt + short caption. Format: PROMPT: [...] ||| CAPTION: [...]").text.strip()
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, high resolution 1024x1792, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "beautiful mountain landscape, ultra detailed, high resolution 1024x1792, 8k"
        caption = "Mountain serenity"
    return prompt, caption

# PERCHANCE – FREE HD (Cloudflare 403 bypass with cloudscraper + scrape image from HTML)
def perchance_image(prompt):
    print("Generating free 1024x1792 HD image with Perchance (no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux"
    scraper = cloudscraper.create_scraper()  # Bypass Cloudflare 403
    try:
        r = scraper.get(url, timeout=60)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            img_tag = soup.find('img', {'id': 'generated-image'}) or soup.find('img', src=lambda s: s and 'generated' in s or 'data:image' in s)
            if img_tag:
                img_url = img_tag['src']
                if 'data:image' in img_url:
                    # Base64 image
                    _, data = img_url.split(",", 1)
                    img = base64.b64decode(data)
                else:
                    if not img_url.startswith("http"):
                        img_url = "https://perchance.org" + img_url
                    img_r = scraper.get(img_url, timeout=60)
                    img = img_r.content
                if len(img) > 50000:
                    print("1024x1792 HD IMAGE READY! (Perchance free quality)")
                    return img
        else:
            print(f"Perchance error: {r.text[:200]}")
    except Exception as e:
        print(f"Perchance exception: {e}")
    return None

# HORDE – Backup (Real key, increased timeout)
def horde_image(prompt):
    print("Generating free 1024x1792 HD image with AI Horde...")
    url = "https://stablehorde.net/api/v2/generate/async"
    headers = {"apikey": HORDE_API_KEY}
    payload = {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
            "seed_variation": 1,
            "height": 1792,
            "width": 1024,
            "karras": True,
            "steps": 20,
            "n": 1
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["SDXL 1.0"]
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Horde create status: {r.status_code}")
        if r.status_code != 202:
            print(f"Horde create error: {r.text[:300]}")
            return None
        job_id = r.json()["id"]
        print(f"Job ID: {job_id} - Generation started...")
        for i in range(200):  # Max 20 min (6 sec interval, for long queues)
            check = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}", timeout=30)
            if check.status_code == 200:
                check_json = check.json()
                print(f"Status check {i+1}: {check_json['wait_time']} sn kalan, kuyruk: {check_json['queue_position']}")
                if check_json["done"]:
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}", timeout=30)
                    if status.status_code == 200:
                        generations = status.json()["generations"]
                        if generations:
                            img_url = generations[0]["img"]
                            img = requests.get(img_url, timeout=60).content
                            if len(img) > 50000:
                                print("1024x1792 HD IMAGE READY!")
                                return img
            time.sleep(6)
        print("AI Horde timeout.")
        return None
    except Exception as e:
        print(f"AI Horde exception: {e}")
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

# ANA
if __name__ == "__main__":
    print("\nPERCHANCE + HORDE FREE HD BOT RUNNING!\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = perchance_image(prompt)
    if not img:
        img = horde_image(prompt)
    if not img:
        print("Image generation failed → Tweet not posted")
        exit(1)
    tweet(img, caption)
