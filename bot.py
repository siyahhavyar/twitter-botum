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
STABILITY_KEY = os.getenv("STABILITY_KEY")
GEMINI_KEY    = os.getenv("GEMINI_KEY")

if not STABILITY_KEY:
    print("ERROR: STABILITY_KEY eksik!")
    exit(1)

if not GEMINI_KEY:
    print("ERROR: GEMINI_KEY eksik!")
    exit(1)


# -----------------------------
# GEMINI: PROMPT + CAPTION
# -----------------------------
def generate_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
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

    return final_prompt, caption, theme


# -----------------------------
# GEMINI: HASHTAG OLUŞTURUCU
# -----------------------------
def generate_hashtags(theme):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Based on the theme "{theme}", create 5 short, aesthetic, relevant, trending hashtags.
    Only return the hashtags, space-separated, no explanation.
    """

    text = model.generate_content(prompt).text
    hashtags = text.strip().replace("\n", " ")
    return hashtags


# -----------------------------
# STABILITY AI: GÖRSEL ÜRETİMİ
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
        "aspect_ratio": "9:16",
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
def post_to_twitter(img_bytes, caption, hashtags):
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

    tweet_text = f"{caption}\n\n{hashtags}"

    client.create_tweet(
        text=tweet_text,
        media_ids=[media.media_id]
    )

    print("TWEET BAŞARILI!")
    os.remove(filename)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    prompt, caption, theme = generate_prompt_caption()

    print("Prompt:", prompt)
    print("Caption:", caption)
    print("Theme:", theme)

    hashtags = generate_hashtags(theme)
    print("Hashtags:", hashtags)

    img = generate_image(prompt)

    if img:
        post_to_twitter(img, caption, hashtags)
    else:
        print("Görsel oluşturulamadı!")
