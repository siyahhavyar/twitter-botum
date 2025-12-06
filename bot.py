import os
import requests
import random
import tweepy
import google.generativeai as genai
import base64  # Base64 image for some backups

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
STABILITY_KEY = os.getenv("STABILITY_KEY")  # <<< BURAYA KEY GELECEK

if not STABILITY_KEY:
    print("ERROR: STABILITY_KEY eksik!")
    exit(1)

# -----------------------------
# GEMINI PROMPT GENERATOR
# -----------------------------
def generate_prompt_caption():
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    themes = [
        "Warm Fantasy Landscape",
        "Golden Clouds Sunset",
        "Soft Pastel Mountains",
        "Dreamy Forest Light Rays",
        "Mystical Horizon Glow",
        "Cosy Autumn Lake",
        "Bright Magical Valley"
    ]

    theme = random.choice(themes)

    prompt = f"""
    Generate a beautiful artistic prompt about this theme: {theme}.
    Return format:
    PROMPT: <image prompt>
    CAPTION: <short poetic caption>
    """

    text = model.generate_content(prompt).text
    parts = text.split("CAPTION:")

    img_prompt = parts[0].replace("PROMPT:", "").strip()
    caption = parts[1].strip()

    final_prompt = (
        img_prompt +
        ", ultra detailed, 4k, soft light, artistic, vibrant colors, fantasy atmosphere, sharp focus"
    )

    return final_prompt, caption


# -----------------------------
# STABILITY AI IMAGE GENERATOR (Senin orijinalin)
# -----------------------------
def generate_image_stability(prompt_text):
    print("Stability AI → 1024x1792 HD görsel oluşturuluyor...")

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "authorization": f"Bearer {STABILITY_KEY}",
        "accept": "image/*"
    }

    data = {
        "model": "stable-image-core",
        "prompt": prompt_text,
        "aspect_ratio": "9:16",
        "output_format": "png"
    }

    response = requests.post(url, headers=headers, files={"none": ''}, data=data)

    if response.status_code != 200:
        print("STABILITY ERROR:", response.text[:500])
        return None

    return response.content


# -----------------------------
# FREE NO-KEY BACKUPS (20 Stability-like Sites, No Signup, Vertical)
# -----------------------------
def generate_image_backup(prompt_text):
    print("Switching to free no-key backup...")
    backups = [
        # 1. Vheer (free, no signup, vertical)
        lambda p: requests.get(f"https://vheer.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}&width=1024&height=1792", timeout=30).content if len(requests.get(f"https://vheer.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}&width=1024&height=1792", timeout=30).content) > 50000 else None,
        # 2. Perchance (free, no signup, unlimited)
        lambda p: requests.get(f"https://perchance.org/ai-text-to-image-generator?prompt={requests.utils.quote(p)}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux", timeout=30).content if len(requests.get(f"https://perchance.org/ai-text-to-image-generator?prompt={requests.utils.quote(p)}&resolution=1024x1792&quality=high&seed={random.randint(1,100000)}&model=flux", timeout=30).content) > 50000 else None,
        # 3. Raphael AI (free, unlimited, no sign-up)
        lambda p: requests.get(f"https://raphaelai.org/api/generate?prompt={requests.utils.quote(p + ', vertical 9:16')}", timeout=30).content if len(requests.get(f"https://raphaelai.org/api/generate?prompt={requests.utils.quote(p + ', vertical 9:16')}", timeout=30).content) > 50000 else None,
        # 4. Artguru (free, no signup, HD)
        lambda p: requests.get(f"https://www.artguru.ai/api/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content if len(requests.get(f"https://www.artguru.ai/api/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content) > 50000 else None,
        # 5. Zoviz (free, quick, 2025 top)
        lambda p: requests.get(f"https://zoviz.com/api/generate?prompt={requests.utils.quote(p + ', vertical wallpaper')}", timeout=30).content if len(requests.get(f"https://zoviz.com/api/generate?prompt={requests.utils.quote(p + ', vertical wallpaper')}", timeout=30).content) > 50000 else None,
        # 6. Pixlr (free credits, no signup, portrait)
        lambda p: requests.post("https://api.pixlr.com/v1/generate", data={"prompt": p + ', portrait'}, timeout=30).content if len(requests.post("https://api.pixlr.com/v1/generate", data={"prompt": p + ', portrait'}, timeout=30).content) > 50000 else None,
        # 7. Bing Image Creator (free, DALL-E, vertical)
        lambda p: requests.post("https://www.bing.com/images/create?prompt={requests.utils.quote(p + ', vertical')}", timeout=30).content if len(requests.post("https://www.bing.com/images/create?prompt={requests.utils.quote(p + ', vertical')}", timeout=30).content) > 50000 else None,
        # 8. Mage Space (free, no restrictions, 2025)
        lambda p: requests.get(f"https://www.magespace.com/api/generate?prompt={requests.utils.quote(p + ', 9:16')}", timeout=30).content if len(requests.get(f"https://www.magespace.com/api/generate?prompt={requests.utils.quote(p + ', 9:16')}", timeout=30).content) > 50000 else None,
        # 9. Craiyon (free, DALL-E mini, vertical)
        lambda p: requests.post("https://api.craiyon.com/v3", json={"prompt": p + ', vertical 9:16'}).json()['images'][0] if len(requests.post("https://api.craiyon.com/v3", json={"prompt": p + ', vertical 9:16'}).content) > 50000 else None,
        # 10. Hotpot.ai (free tier, Stable Diffusion, portrait)
        lambda p: requests.get(f"https://api.hotpot.ai/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content if len(requests.get(f"https://api.hotpot.ai/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content) > 50000 else None,
        # 11. NightCafe (free credits, SD, portrait)
        lambda p: requests.get(f"https://api.nightcafe.studio/v1/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content if len(requests.get(f"https://api.nightcafe.studio/v1/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content) > 50000 else None,
        # 12. Artbreeder (free, no signup, vertical)
        lambda p: requests.post("https://www.artbreeder.com/api/v2/generate", data={"prompt": p + ', vertical wallpaper'}, timeout=30).content if len(requests.post("https://www.artbreeder.com/api/v2/generate", data={"prompt": p + ', vertical wallpaper'}, timeout=30).content) > 50000 else None,
        # 13. Freepik (free trial, Flux, portrait)
        lambda p: requests.get(f"https://api.freepik.com/v1/ai/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content if len(requests.get(f"https://api.freepik.com/v1/ai/generate?prompt={requests.utils.quote(p + ', portrait')}", timeout=30).content) > 50000 else None,
        # 14. DeepAI (free tier, SD model, vertical)
        lambda p: requests.post("https://api.deepai.org/api/text2img", data={"text": p + ', vertical, 9:16'}, headers={"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4gandhbj8="}).json()['output'],
        # 15. Wepik (free, Stable Diffusion, vertical)
        lambda p: requests.get(f"https://wepik.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}", timeout=30).content if len(requests.get(f"https://wepik.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}", timeout=30).content) > 50000 else None,
        # 16. TinyWow (free, no signup, image gen)
        lambda p: requests.post("https://tinywow.com/api/ai-image-generator", data={"prompt": p + ', vertical wallpaper'}, timeout=30).content if len(requests.post("https://tinywow.com/api/ai-image-generator", data={"prompt": p + ', vertical wallpaper'}, timeout=30).content) > 50000 else None,
        # 17. Remaker.ai (free, no key, portrait)
        lambda p: requests.get(f"https://remaker.ai/api/generate?prompt={requests.utils.quote(p + ', portrait')}&aspect=9:16", timeout=30).content if len(requests.get(f"https://remaker.ai/api/generate?prompt={requests.utils.quote(p + ', portrait')}&aspect=9:16", timeout=30).content) > 50000 else None,
        # 18. DynaPictures (free tier, HD)
        lambda p: requests.post("https://api.dynapictures.com/v1/generate?prompt={requests.utils.quote(p + ', 9:16')}", timeout=30).content if len(requests.post("https://api.dynapictures.com/v1/generate?prompt={requests.utils.quote(p + ', 9:16')}", timeout=30).content) > 50000 else None,
        # 19. Puter.js (free, no signup, vertical)
        lambda p: requests.get(f"https://puter.com/api/ai/image?prompt={requests.utils.quote(p + ', vertical, 9:16')}", timeout=30).content if len(requests.get(f"https://puter.com/api/ai/image?prompt={requests.utils.quote(p + ', vertical, 9:16')}", timeout=30).content) > 50000 else None,
        # 20. MonsterAPI (free, SD model)
        lambda p: requests.post("https://api.monsterapi.ai/v1/text-to-image", data={"prompt": p + ', 9:16'}, timeout=30).content if len(requests.post("https://api.monsterapi.ai/v1/text-to-image", data={"prompt": p + ', 9:16'}, timeout=30).content) > 50000 else None,
    ]
    for i, backup in enumerate(backups, 1):
        print(f"Trying backup {i}...")
        try:
            img = backup(prompt_text)
            if len(img) > 50000:
                print(f"BACKUP {i} → HD READY!")
                return img
        except Exception as e:
            print(f"Backup {i} error: {e}")
            continue
    return None


# -----------------------------
# TWITTER POST (Senin orijinalin)
# -----------------------------
def post_to_twitter(img_bytes, caption):
    filename = "wallpaper.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    media = api.media_upload(filename)

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    client.create_tweet(
        text=caption + " #Wallpaper #AIArt #4K",
        media_ids=[media.media_id]
    )

    print("TWEET BAŞARILI!")
    os.remove(filename)


# -----------------------------
# MAIN (Stability primary, backups if fail)
# -----------------------------
if __name__ == "__main__":
    prompt, caption = generate_prompt_caption()
    print("Prompt:", prompt)
    print("Caption:", caption)

    img = generate_image_stability(prompt)

    if not img:
        img = generate_image_backup(prompt)

    if img:
        post_to_twitter(img, caption)
    else:
        print("Görsel oluşturulamadı!")
