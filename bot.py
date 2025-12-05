import os
import requests
import random
import google.generativeai as genai
import tweepy

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
# GEMINI PROMPT GENERATOR (KENDİ FİKİR BULUYOR)
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
        p = parts[0].replace("PROMPT:", "").strip()
        c = parts[1].strip()
    except:
        p = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper"
        c = "Whispers of spring"

    final_prompt = (
        p +
        ", vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, 8k, soft lighting, cinematic atmosphere"
    )

    return final_prompt, c


# -----------------------------
# STABILITY AI IMAGE GENERATOR
# -----------------------------
def generate_image(prompt_text):
    print("Stability AI → 1024x1792 HD görsel oluşturuluyor...")

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "authorization": f"Bearer {STABILITY_KEY}",
        "accept": "image/*"
    }

    data = {
        "model": "stable-image-core",
        "prompt": prompt_text,
        "aspect_ratio": "9:16",        # DİKEY
        "output_format": "png"
    }

    response = requests.post(url, headers=headers, files={"none": ''}, data=data)

    if response.status_code != 200:
        print("STABILITY ERROR:", response.text[:500])
        return None

    return response.content


# -----------------------------
# TWITTER POST
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
        text=caption + " #Wallpaper #AIArt #4K #Aesthetic",
        media_ids=[media.media_id]
    )

    print("TWEET BAŞARILI!")
    os.remove(filename)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    prompt, caption = generate_prompt_caption()
    print("Prompt:", prompt)
    print("Caption:", caption)

    img = generate_image(prompt)

    if img:
        post_to_twitter(img, caption)
    else:
        print("Görsel oluşturulamadı!")
