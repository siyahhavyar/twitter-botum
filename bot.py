import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# REQUIRED KEYS
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"

for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

# 🔥 AI generates its OWN theme, prompt and caption (English)
def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # AI chooses everything automatically
    cmd = (
        "Generate an ultra-detailed photorealistic wallpaper theme yourself. "
        "Return in this format ONLY: "
        "PROMPT: [...] ||| CAPTION: [...] "
        "Prompt must describe a portrait (vertical) wallpaper that fits 1024x1792. "
        "Caption must be SHORT, aesthetic, and in English."
    )

    resp = model.generate_content(cmd).text.strip()

    try:
        p, c = resp.split("|||")

        prompt = (
            p.replace("PROMPT:", "").strip() +
            ", vertical composition, portrait ratio 1024x1792, ultra detailed, sharp focus, 8k masterpiece, cinematic lighting"
        )

        caption = c.replace("CAPTION:", "").strip()

    except:
        prompt = "majestic fantasy landscape, portrait orientation, 1024x1792, sharp, ultra detailed, 8k"
        caption = "Timeless beauty"

    return prompt, caption

# PERCHANCE – portrait mode
def perchance_image(prompt):
    print("Perchance: 1024x1792 portrait wallpaper üretiliyor...")
    encoded = requests.utils.quote(prompt)

    url = (
        f"https://perchance.org/ai-text-to-image-generator?"
        f"prompt={encoded}&resolution=1024x1792&quality=high&"
        f"seed={random.randint(1,100000)}&model=flux"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://perchance.org/ai-text-to-image-generator"
    }

    try:
        r = requests.get(url, headers=headers, timeout=60)
        print(f"Perchance status: {r.status_code}")

        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            img = r.content
            if len(img) > 50000:
                print("PORTRAIT 1024x1792 HD image hazır!")
                return img
        else:
            print("Perchance error:", r.text[:200])
    except Exception as e:
        print("Perchance exception:", e)

    return None

# HORDE – backup
def horde_image(prompt):
    print("AI Horde: portrait wallpaper üretiliyor...")

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
        if r.status_code != 202:
            print("Horde error:", r.text[:300])
            return None

        job_id = r.json()["id"]
        print("Horde job:", job_id)

        for i in range(200):
            check = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}", timeout=30)

            if check.status_code == 200:
                chk = check.json()
                print(f"Queue: {chk['queue_position']} | Wait: {chk['wait_time']}")

                if chk["done"]:
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}", timeout=30)

                    if status.status_code == 200:
                        gens = status.json()["generations"]
                        if gens:
                            img_url = gens[0]["img"]
                            img = requests.get(img_url, timeout=60).content

                            if len(img) > 50000:
                                print("HORDE portrait image hazır!")
                                return img

            time.sleep(6)

    except Exception as e:
        print("Horde exception:", e)

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

    client.create_tweet(
        text=caption + " #AIArt #Wallpaper #4K #Portrait",
        media_ids=[media.media_id]
    )

    print("Tweet gönderildi!")
    os.remove(fn)


# MAIN
if __name__ == "__main__":
    print("\nPortrait Wallpaper BOT ÇALIŞIYOR!\n")

    prompt, caption = get_prompt_caption()

    print("AI prompt:", prompt[:180], "…")
    print("AI caption:", caption)

    img = perchance_image(prompt)
    if not img:
        img = horde_image(prompt)

    if not img:
        print("Görsel üretilemedi → Tweet iptal")
        exit(1)

    tweet(img, caption)
