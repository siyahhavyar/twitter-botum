import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# ONLY THESE ARE NEEDED (Horde key optional)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"  # Put your real key in secrets

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

# PERCHANCE – FREE HD (403 fix: More headers, browser mimic)
def perchance_image(prompt):
    print("Generating free 1024x1024 HD image with Perchance (no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1024x1024&quality=high&seed={random.randint(1,100000)}&model=flux"
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
    } # Wide header set, Cloudflare 403 bypass
    try:
        r = requests.get(url, headers=headers, timeout=60)
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

# HORDE – Backup (With real key, increased timeout)
def horde_image(prompt):
    print("Generating free 1024x1024 HD image with AI Horde...")
    url = "https://stablehorde.net/api/v2/generate/async"
    headers = {"apikey": HORDE_API_KEY}
    payload = {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
            "seed_variation": 1,
            "height": 1024,
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
                print(f"Status check {i+1}: {check_json['wait_time']} sec left, queue: {check_json['queue_position']}")
                if check_json["done"]:
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}", timeout=30)
                    if status.status_code == 200:
                        generations = status.json()["generations"]
                        if generations:
                            img_url = generations[0]["img"]
                            img = requests.get(img_url, timeout=60).content
                            if len(img) > 50000:
                                print("1024x1024 HD IMAGE READY!")
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

# MAIN
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
