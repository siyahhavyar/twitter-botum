import os
import requests
import random
import time
import google.generativeai as genai
import tweepy
import cloudscraper  # Cloudflare 403 bypass için ekledik

# SADECE BUNLAR LAZIM (Horde key opsiyonel)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"  # Gerçek key'ini secrets'e koy

# Eksik kontrol
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    themes = ["Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Steampunk City","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → ultra detaylı photorealistic prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text.strip()
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, high resolution 1024x1024, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "beautiful mountain landscape, ultra detailed, high resolution 1024x1024, 8k"
        caption = "Mountain serenity"
    return prompt, caption

# PERCHANCE – ÜCRETSİZ HD (403 fix: Cloudscraper ile bypass)
def perchance_image(prompt):
    print("Perchance ile ücretsiz 1024x1024 HD resim üretiliyor (no signup)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1024x1024&quality=high&seed={random.randint(1,100000)}&model=flux"
    scraper = cloudscraper.create_scraper()  # Cloudflare 403 bypass
    try:
        r = scraper.get(url, timeout=60)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("1024x1024 HD RESİM HAZIR! (Perchance free kalite)")
                return img
        else:
            print(f"Perchance error: {r.text[:200]}")
    except Exception as e:
        print(f"Perchance exception: {e}")
    return None

# HORDE – Yedek (Gerçek key ile, timeout artırıldı)
def horde_image(prompt):
    print("AI Horde ile ücretsiz 1024x1024 HD resim üretiliyor...")
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
        print(f"Job ID: {job_id} - Üretim başladı...")
        for i in range(200):  # Max 20 dk (6 sn aralık, uzun kuyruk için)
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
                                print("1024x1024 HD RESİM HAZIR!")
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
    print("TWEET BAŞARIYLA ATILDI!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nPERCHANCE + HORDE ÜCRETSİZ HD BOT ÇALIŞIYOR!\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = perchance_image(prompt)
    if not img:
        img = horde_image(prompt)
    if not img:
        print("Resim üretilemedi → Tweet atılmadı")
        exit(1)
    tweet(img, caption)
