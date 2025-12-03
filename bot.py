import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# SADECE BUNLAR LAZIM (Horde key opsiyonel)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"  

# Eksik kontrol
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

# ---------------------------------------------------
# 1) *** İngilizce Prompt + İngilizce Caption ***
# ---------------------------------------------------
def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    themes = [
        "Cyberpunk City", "Crystal Forest", "Galactic Storm", 
        "Mystic Waterfall", "Moonlight Desert", "Neon Jungle",
        "Steam City", "Floating Islands"
    ]

    theme = random.choice(themes)

    resp = model.generate_content(
        f"Theme: {theme} → Create: PROMPT: ultra detailed portrait wallpaper prompt "
        f"||| CAPTION: short poetic English caption with 2 hashtags"
    ).text.strip()

    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip()

        # *** PORTRAIT EKLENDİ ***
        prompt += ", ultra detailed, portrait 1024x1792, 8k, sharp focus, cinematic lighting"

        caption = c.replace("CAPTION:", "").strip()

    except:
        prompt = "majestic mountain portrait wallpaper, ultra detailed, portrait 1024x1792, 8k"
        caption = "Mountain serenity #Wallpaper #AIArt"

    return prompt, caption

# ---------------------------------------------------
# PERCHANCE – Portrait 1024x1792 Output
# ---------------------------------------------------
def perchance_image(prompt):
    print("Perchance ile ücretsiz PORTRE 1024x1792 HD resim üretiliyor...")

    encoded = requests.utils.quote(prompt)

    # *** PORTRE ÇÖZÜNÜRLÜĞÜ EKLENDİ ***
    url = (
        f"https://perchance.org/ai-text-to-image-generator?"
        f"prompt={encoded}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://perchance.org/ai-text-to-image-generator"
    }

    try:
        r = requests.get(url, headers=headers, timeout=60)
        print(f"Perchance status: {r.status_code}")

        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("PORTRAIT 1024x1792 HD RESİM HAZIR!")
                return img

    except Exception as e:
        print(f"Perchance exception: {e}")

    return None

# ---------------------------------------------------
# HORDE – Portrait (Yedek)
# ---------------------------------------------------
def horde_image(prompt):
    print("AI Horde ile portrait 1024x1792 HD resim üretiliyor...")

    url = "https://stablehorde.net/api/v2/generate/async"
    headers = {"apikey": HORDE_API_KEY}

    payload = {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
            "height": 1792,   # *** PORTRE ***
            "width": 1024,    # *** PORTRE ***
            "steps": 20,
            "n": 1
        },
        "nsfw": False,
        "models": ["SDXL 1.0"]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code != 202:
            print("Horde create error:", r.text[:300])
            return None

        job_id = r.json()["id"]

        for i in range(200):
            check = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}")
            if check.status_code == 200:
                data = check.json()
                if data["done"]:
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}")
                    if status.status_code == 200:
                        gen = status.json()["generations"]
                        if gen:
                            img = requests.get(gen[0]["img"]).content
                            if len(img) > 50000:
                                print("PORTRAIT 1024x1792 HD RESİM HAZIR!")
                                return img
            time.sleep(6)
    except Exception as e:
        print("AI Horde exception:", e)

    return None

# ---------------------------------------------------
# Tweet At
# ---------------------------------------------------
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

    client.create_tweet(text=caption, media_ids=[media.media_id])
    print("TWEET BAŞARIYLA ATILDI!")

    os.remove(fn)

# ---------------------------------------------------
# Çalıştır
# ---------------------------------------------------
if __name__ == "__main__":
    print("\nPORTRAIT HD TWITTER BOT ÇALIŞIYOR!\n")

    prompt, caption = get_prompt_caption()
    print("Prompt:", prompt)
    print("Caption:", caption)

    img = perchance_image(prompt)
    if not img:
        img = horde_image(prompt)
    if not img:
        print("Resim üretilemedi → Tweet gönderilmedi.")
        exit(1)

    tweet(img, caption)
