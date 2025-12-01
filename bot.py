import tweepy
import os
import json
from google import genai

# --- API Keys ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- Gemini Client ---
client = genai.Client(api_key=GEMINI_KEY)
TEXT_MODEL = "gemini-1.5-flash"
IMAGE_MODEL = "gemini-1.5-flash"

# -------------------------------------------------------
# 1) Gemini – JSON Fikir Üretme
# -------------------------------------------------------
def get_artistic_idea():
    print("🧠 Gemini JSON üretiyor...")

    prompt = """
    You are an AI that outputs STRICT JSON with no codeblocks, no markdown, no explanation.

    Return exactly:

    {
      "caption": "short english caption with 2 hashtags",
      "image_prompt": "highly detailed professional vertical wallpaper prompt, include: vertical wallpaper, 8k resolution, masterpiece, cinematic lighting, sharp focus"
    }
    """

    try:
        result = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )

        text = result.text.strip()
        text = text.replace("```json", "").replace("```", "")
        text = text.replace("`", "")

        data = json.loads(text)
        print("✅ Üretilen Caption:", data["caption"])
        return data

    except Exception as e:
        print("⚠️ JSON üretim hatası:", e)
        return {
            "caption": "Cosmic Dream ✨ #Wallpaper",
            "image_prompt": "A glowing cosmic nebula, vertical wallpaper, 8k resolution, masterpiece, cinematic lighting"
        }

# -------------------------------------------------------
# 2) Gemini – Görsel Üretme
# -------------------------------------------------------
def generate_image(prompt):
    print("🎨 Gemini görsel oluşturuyor...")

    try:
        result = client.models.generate_image(
            model=IMAGE_MODEL,
            prompt=prompt
        )

        image_bytes = result.images[0].data

        with open("tweet_image.png", "wb") as f:
            f.write(image_bytes)

        print("✅ Görsel başarıyla oluşturuldu!")
        return True

    except Exception as e:
        print("❌ Görsel oluşturulamadı:", e)
        return False

# -------------------------------------------------------
# 3) Twitter'a Gönderme
# -------------------------------------------------------
def post_tweet():
    print("🚀 Tweet hazırlığı başlıyor...")

    idea = get_artistic_idea()

    if not generate_image(idea["image_prompt"]):
        print("❌ Görsel oluşturulamadı, tweet iptal edildi.")
        return

    print("🐦 Twitter'a yükleniyor...")

    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)

        client_twitter = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )

        media = api.media_upload(filename="tweet_image.png")

        client_twitter.create_tweet(
            text=idea["caption"],
            media_ids=[media.media_id]
        )

        print("✅ Tweet başarıyla gönderildi!")

    except Exception as e:
        print("❌ Twitter hatası:", e)

# -------------------------------------------------------
# Çalıştır
# -------------------------------------------------------
if __name__ == "__main__":
    post_tweet()
