import os
import requests
import random
import google.generativeai as genai
import tweepy
from bs4 import BeautifulSoup
import cloudscraper
import base64
import time

# ENV
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY")

required_vars = ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","HORDE_API_KEY"]
for v in required_vars:
    if not os.getenv(v):
        print(f"Missing ENV variable: {v}")
        exit(1)

# NON-PUNK THEMES ONLY
THEMES = [
    "Misty Waterfall Valley",
    "Golden Sunset Beach",
    "Frozen Aurora Lake",
    "Silent Autumn Forest",
    "Ancient Marble Temple",
    "Celestial Cloud Kingdom",
    "Blue Crystal Mountains",
    "Sacred Sakura Garden",
    "Starry Dream Meadow",
    "Shimmering Ice Cavern",
]

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    theme = random.choice(THEMES)

    q = f"""
Create:
PROMPT = highly detailed, photorealistic wallpaper for theme: {theme}
CAPTION = poetic, short (max 8 words)
Format strictly:
PROMPT: ...
|||
CAPTION: ...
"""

    resp = model.generate_content(q).text.strip()

    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip()
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "beautiful mountain landscape, ultra detailed"
        caption = "Nature's silence"

    prompt += ", ultra detailed, 1024x1792, 8k, natural colors, no punk style, no cyber elements"
    return prompt, caption


# PERCHANCE
def perchance_image(prompt):
    print("Generating free 1024x1792 HD image with Perchance...")
    encoded = requests.utils.quote(prompt)
    url = (
        f"https://perchance.org/ai-text-to-image-generator?"
        f"prompt={encoded}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux"
    )

    scraper = cloudscraper.create_scraper()
    try:
        r = scraper.get(url, timeout=60)
        print("Perchance status:", r.status_code)

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            img_tag = soup.find("img", {"id": "generated-image"}) or \
                      soup.find("img", src=lambda s: s and ("generated" in s or "data:image" in s))

            if img_tag:
                img_url = img_tag["src"]

                if img_url.startswith("data:image"):
                    img = base64.b64decode(img_url.split(",",1)[1])
                    return img

                if not img_url.startswith("http"):
                    img_url = "https://perchance.org" + img_url

                raw = scraper.get(img_url, timeout=60).content
                if len(raw) > 50000:
                    print("Perchance HD READY!")
                    return raw
    except Exception as e:
        print("Perchance exception:", e)

    return None


# HORDE BACKUP
def horde_image(prompt):
    print("Generating HD with AI Horde...")

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
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        print("Horde create status:", r.status_code)

        if r.status_code != 202:
            print(r.text[:300])
            return None

        job_id = r.json()["id"]
        print("Job:", job_id)

        for i in range(200):
            chk = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}", timeout=30).json()
            print(f"Check {i+1}: queue={chk['queue_position']} wait={chk['wait_time']}")

            if chk["done"]:
                status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}", timeout=30).json()
                img_url = status["generations"][0]["img"]
                raw = requests.get(img_url, timeout=60).content

                if len(raw) > 50000:
                    print("HORDE HD READY!")
                    return raw

            time.sleep(6)

    except Exception as e:
        print("Horde exception:", e)

    return None


def tweet(img_bytes, caption):
    fn = "wallpaper.jpg"
    with open(fn, "wb") as f:
        f.write(img_bytes)

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    media = api.media_upload(fn)

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    client.create_tweet(
        text=caption + " #AIArt #Wallpaper #4K",
        media_ids=[media.media_id]
    )

    print("Tweet posted!")
    os.remove(fn)


# MAIN
if __name__ == "__main__":
    print("\nNON-PUNK HD TWITTER BOT RUNNING!\n")

    prompt, caption = get_prompt_caption()
    print("Prompt:", prompt[:150], "...")
    print("Caption:", caption)

    img = perchance_image(prompt)
    if not img:
        img = horde_image(prompt)

    if not img:
        print("Image error! Tweet cancelled.")
        exit(1)

    tweet(img, caption)
