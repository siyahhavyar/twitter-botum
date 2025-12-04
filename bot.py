import os
import requests
import tweepy
import random
import time

# -----------------------------------------
# SABİT AYARLAR
# -----------------------------------------

HORDE_API_KEY = "6FoHyt8ewpxxOO57QXZZFw"   # API KEY doğrudan kodda
PERCHANCE_URL = "https://your-model.perchance.org/api"   # kendi perchance api url'inle değiştir
TWITTER_API_KEY = "TWITTER_API_KEY"
TWITTER_API_SECRET = "TWITTER_API_SECRET"
TWITTER_ACCESS_TOKEN = "TWITTER_ACCESS_TOKEN"
TWITTER_ACCESS_SECRET = "TWITTER_ACCESS_SECRET"

# -----------------------------------------
# TWITTER BAĞLANTISI
# -----------------------------------------

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter = tweepy.API(auth)

# -----------------------------------------
# PROMPT HAVUZU (CYBERPUNK/STEAMPUNK YOK)
# -----------------------------------------

PROMPTS = [
    "hyper-realistic portrait photography, soft lighting, beautiful depth",
    "4k ultra-detailed landscape, warm fantasy atmosphere",
    "cinematic shot, natural lighting, beautiful composition",
    "studio-quality photo, detailed textures, soft colors",
    "nature scenery, ultra high detail, photo-realistic",
    "dreamy environment, magical realism, extremely detailed"
]

# -----------------------------------------
# PERCHANCE AI İÇERİK ÜRETİMİ
# -----------------------------------------

def generate_text():
    try:
        r = requests.get(PERCHANCE_URL, timeout=15)
        if r.status_code == 200:
            return r.text.strip()
        return "Harika bir gün! Yeni bir görsel daha hazırladım."
    except:
        return "Bugün sanat yaratma günü! İşte yeni bir görsel."

# -----------------------------------------
# HORDE İLE GÖRSEL ÜRETİMİ + UPSCALE
# -----------------------------------------

def generate_image(prompt):
    headers = {"apikey": HORDE_API_KEY}

    payload = {
        "prompt": prompt,
        "models": ["Stable Diffusion XL"],
        "params": {
            "sampler_name": "k_euler",
            "denoising_strength": 0.7,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "steps": 30
        }
    }

    task = requests.post("https://aihorde.net/api/v2/generate/async", json=payload, headers=headers).json()
    task_id = task["id"]

    while True:
        status = requests.get(f"https://aihorde.net/api/v2/generate/status/{task_id}").json()
        if status.get("finished"):
            img_url = status["generations"][0]["img"]
            break
        time.sleep(3)

    # HD UPSCALE
    upscale_payload = {
        "source_image": img_url,
        "source_processing": "upscale",
        "params": {"scale": 2}
    }

    upscale = requests.post("https://aihorde.net/api/v2/generate/async", json=upscale_payload, headers=headers).json()
    upscale_id = upscale["id"]

    while True:
        up_status = requests.get(f"https://aihorde.net/api/v2/generate/status/{upscale_id}").json()
        if up_status.get("finished"):
            return up_status["generations"][0]["img"]
        time.sleep(3)

# -----------------------------------------
# TWITTER POST
# -----------------------------------------

def post_to_twitter():
    text = generate_text()
    prompt = random.choice(PROMPTS)

    print("Prompt:", prompt)

    img_url = generate_image(prompt)
    img_data = requests.get(img_url).content

    with open("image.png", "wb") as f:
        f.write(img_data)

    twitter.update_status_with_media(status=text, filename="image.png")
    print("Gönderildi!")

# -----------------------------------------
# ÇALIŞTIR
# -----------------------------------------

if __name__ == "__main__":
    post_to_twitter()
