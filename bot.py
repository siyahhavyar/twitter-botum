import os
import requests
import time
import base64
import tweepy

# --------------------
# API KEYS
# --------------------
HORDE_API_KEY = "6FoHyt8ewpxxOO57QXZZFw"

TW_API_KEY = os.getenv("TW_API_KEY")
TW_API_SECRET = os.getenv("TW_API_SECRET")
TW_ACCESS_TOKEN = os.getenv("TW_ACCESS_TOKEN")
TW_ACCESS_SECRET = os.getenv("TW_ACCESS_SECRET")

# --------------------
# TWITTER LOGIN
# --------------------
def twitter_client():
    auth = tweepy.OAuth1UserHandler(
        TW_API_KEY,
        TW_API_SECRET,
        TW_ACCESS_TOKEN,
        TW_ACCESS_SECRET
    )
    return tweepy.API(auth)

# --------------------
# HORDE IMAGE GENERATOR
# --------------------
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

    # ---- SEND ASYNC REQUEST ----
    task = requests.post(
        "https://aihorde.net/api/v2/generate/async",
        json=payload,
        headers=headers
    ).json()

    if "id" not in task:
        print("HORDE ERROR:", task)
        return None

    task_id = task["id"]

    # ---- WAIT FOR GENERATION ----
    while True:
        status = requests.get(
            f"https://aihorde.net/api/v2/generate/status/{task_id}"
        ).json()

        if status.get("finished"):
            try:
                img_url = status["generations"][0]["img"]
                break
            except:
                print("GENERATION RESPONSE ERROR:", status)
                return None

        time.sleep(3)

    # --------------------
    # UPSCALE (optional)
    # --------------------
    upscale_payload = {
        "source_image": img_url,
        "source_processing": "upscale",
        "params": {"scale": 2}
    }

    upscale = requests.post(
        "https://aihorde.net/api/v2/generate/async",
        json=upscale_payload,
        headers=headers
    ).json()

    if "id" not in upscale:
        print("UPSCALE ERROR:", upscale)
        return img_url  # upscale başarısızsa orijinal resmi döndür

    upscale_id = upscale["id"]

    while True:
        up_status = requests.get(
            f"https://aihorde.net/api/v2/generate/status/{upscale_id}"
        ).json()

        if up_status.get("finished"):
            try:
                return up_status["generations"][0]["img"]
            except:
                print("UPSCALE STATUS ERROR:", up_status)
                return img_url

        time.sleep(3)


# --------------------
# DOWNLOAD IMAGE
# --------------------
def download_image(url, path="image.png"):
    img_data = requests.get(url).content
    with open(path, "wb") as f:
        f.write(img_data)
    return path


# --------------------
# POST TO TWITTER
# --------------------
def post_to_twitter():
    prompt = "4k ultra-detailed landscape, warm fantasy atmosphere"

    print("Görüntü üretiliyor...")
    img_url = generate_image(prompt)

    if img_url is None:
        print("GÖRSEL OLUŞTURULAMADI.")
        return

    print("Görüntü indiriliyor:", img_url)
    img_path = download_image(img_url)

    api = twitter_client()

    print("Twitter'a yükleniyor...")
    media = api.media_upload(img_path)

    print("Tweet atılıyor...")
    api.update_status(status=prompt, media_ids=[media.media_id])

    print("Tweet paylaşıldı!")


# --------------------
# RUN BOT
# --------------------
if __name__ == "__main__":
    post_to_twitter()
