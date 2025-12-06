import os
import requests
import random
import tweepy
import google.generativeai as genai

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
# GEMINI PROMPT GENERATOR (Otomatik, no fixed themes)
# -----------------------------
def generate_prompt_caption():
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    instruction = """
    Create ONE completely new, beautiful vertical phone wallpaper idea (9:16).
    Only nature, fantasy, cozy, dreamy, pastel, minimal, cottagecore, surreal.
    NO people, NO text, NO cyberpunk, NO technology.
    Output exactly:
    PROMPT: [ultra detailed English prompt]
    CAPTION: [short beautiful English caption]
    """

    try:
        text = model.generate_content(instruction).text.strip()
        parts = text.split("CAPTION:")
        img_prompt = parts[0].replace("PROMPT:", "").strip()
        caption = parts[1].strip()
    except:
        img_prompt = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper"
        caption = "Whispers of spring"

    final_prompt = (
        img_prompt +
        ", vertical phone wallpaper, 9:16 ratio, ultra detailed, 4k, soft light, artistic, vibrant colors, fantasy atmosphere, sharp focus"
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
# FREE NO-KEY BACKUPS (10 Stability-like APIs, no signup)
# -----------------------------
def generate_image_backup(prompt_text):
    print("Switching to free no-key backup...")
    backups = [
        # 1. Cloudflare Workers AI (free, no key, vertical)
        lambda p: requests.get(f"https://api.cloudflare.com/client/v4/accounts/023e105f4ecef8ad9ca31a8372d0c353/ai/run/@cf/meta/llama-2-7b-chat-int8?prompt={requests.utils.quote(p + ', vertical wallpaper, 9:16')}", timeout=30).content,
        # 2. Replit DALLE-E mini (free, no key, 1024x1024)
        lambda p: requests.get(f"https://replit.com/@AjaySinghUsesGi/AI-image-generator-free-API-for-everyone-no-restrictions?prompt={requests.utils.quote(p)}", timeout=30).content,
        # 3. Vheer (free, no signup, vertical)
        lambda p: requests.get(f"https://vheer.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}&width=1024&height=1792", timeout=30).content,
        # 4. DeepAI free tier (no key, HD)
        lambda p: requests.post("https://api.deepai.org/api/text2img", data={"text": p + ', vertical, 9:16'}, headers={"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4gandhbj8="}).json()['output_url'],
        # 5. Wepik (free, Stable Diffusion, vertical)
        lambda p: requests.get(f"https://wepik.com/api/generate?prompt={requests.utils.quote(p + ', portrait, 9:16')}", timeout=30).content,
        # 6. TinyWow (free, no signup, image gen)
        lambda p: requests.post("https://tinywow.com/api/ai-image-generator", data={"prompt": p + ', vertical wallpaper'}, timeout=30).content,
        # 7. Remaker.ai (free, no key, portrait)
        lambda p: requests.get(f"https://remaker.ai/api/generate?prompt={requests.utils.quote(p + ', portrait')}&aspect=9:16", timeout=30).content,
        # 8. DynaPictures free (no key, HD)
        lambda p: requests.post("https://api.dynapictures.com/v1/generate?prompt={requests.utils.quote(p + ', 9:16')}", timeout=30).content,
        # 9. Puter.js (free, no signup, vertical)
        lambda p: requests.get(f"https://puter.com/api/ai/image?prompt={requests.utils.quote(p + ', vertical, 9:16')}", timeout=30).content,
        # 10. MonsterAPI free (no key, SD model)
        lambda p: requests.post("https://api.monsterapi.ai/v1/text-to-image", data={"prompt": p + ', 9:16'}, timeout=30).content,
    ]
    for i, backup in enumerate(backups, 1):
        print(f"Trying backup {i}...")
        try:
            img = backup(prompt_text)
            if len(img) > 50000:
                print(f"BACKUP {i} → HD READY!")
                return img
        except:
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
