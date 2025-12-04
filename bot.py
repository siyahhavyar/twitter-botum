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
# GEMINI: TEMA + PROMPT + CAPTION
# -----------------------------
def generate_ai_theme_and_prompt():
    """
    Bu fonksiyon tamamen yapay zekanın kendisinin bir tema yaratmasını sağlar.
    Tema, fantastik + minimal + karanlık + estetik olacak şekilde sınırlı yönlendirme alır.
    AI temayı, prompt'u ve kısa caption'ı birlikte üretir.
    """

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = """
    Create a unique artistic theme that mixes:
    - fantasy atmosphere
    - minimal and clean visual style
    - soft-dark or moody tones
    - abstract or symbolic elements (no explicit witches, heroes, characters)
    - elegant, aesthetic mood

    After deciding the theme, generate:
    PROMPT: a detailed AI image prompt describing that theme, including mood, lighting, color palette, and minimal fantasy symbolism.
    CAPTION: a very short poetic caption (max 7 words).

    Only return in this format:
    THEME: <the unique theme name>
    PROMPT: <image prompt>
    CAPTION: <caption>
    """

    text = model.generate_content(prompt).text

    # Parçalıyoruz
    parts = text.split("PROMPT:")

    theme = parts[0].replace("THEME:", "").strip()
    rest = parts[1].split("CAPTION:")

    img_prompt = rest[0].strip()
    caption = rest[1].strip()

    # Prompta ekstra stil eklentileri
    final_prompt = (
        img_prompt +
        ", ultra detailed, 4k, soft lighting, cinematic tone, minimal fantasy symbolism, muted colors, elegant aesthetic, sharp focus"
    )

    return theme, final_prompt, caption


# -----------------------------
# GEMINI: HASHTAG OLUŞTURUCU
# -----------------------------
def generate_hashtags(theme):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Based on the artistic theme "{theme}", generate 7 minimal, aesthetic, fantasy-inspired hashtags.
    Style: short, elegant, trending, abstract.
    No explanations, no numbering, only hashtags space-separated.
    """

    text = model.generate_content(prompt).text
    hashtags = text.strip().replace("\n", " ")
    return hashtags


# -----------------------------
# STABILITY AI: GÖRSEL ÜRETİMİ
# -----------------------------
def generate_image(prompt_text):

    print("Stability AI → 1024x1792 görsel oluşturuluyor...")

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
    theme, prompt, caption = generate_ai_theme_and_prompt()

    print("Theme:", theme)
    print("Prompt:", prompt)
    print("Caption:", caption)

    hashtags = generate_hashtags(theme)
    print("Hashtags:", hashtags)

    img = generate_image(prompt)

    if img:
        post_to_twitter(img, caption, hashtags)
    else:
        print("Görsel oluşturulamadı!")
