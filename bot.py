import tweepy
import os
import time
import json
import random
from google import genai

# --- ANAHTARLAR ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- GEMINI AYAR ---
client = genai.Client(api_key=GEMINI_KEY)
TEXT_MODEL = "gemini-1.5-flash"
IMAGE_MODEL = "gemini-1.5-flash"

# --------------------------------------------------------
# 1) TWITTER METİN + PROMPT OLUŞTURMA (Gemini)
# --------------------------------------------------------
def get_artistic_idea():
    print("🧠 Gemini (1.5 Flash) düşünüyor...")

    prompt_emir = """
    You are a digital artist creating a unique daily wallpaper.
    Respond ONLY in pure JSON, no other text.

    {
      "caption": "short cool english caption with hashtags",
      "image_prompt": "highly detailed english prompt describing a vertical aesthetic wallpaper, include: 'vertical wallpaper, 8k resolution, masterpiece, cinematic lighting, sharp focus'"
    }
    """

    try:
        response = client.models.generate_text(
            model=TEXT_MODEL,
            prompt=prompt_emir
        )

        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "")

        data = json.loads(text)
        print("✅ Fikir üretildi:", data["caption"])
        return data

    except Exception as e:
        print("⚠️ Gemini Hatası:", e)
        return {
            "caption": "Cosmic Serenity ✨ #Wallpaper",
            "image_prompt": "A calm cosmic nebula with glowing lights, vertical wallpaper, 8k resolution, masterpiece"
        }

# --------------------------------------------------------
# 2) GEMINI İLE RESİM ÜRETME (HUGGINGFACE YOK)
# --------------------------------------------------------
def generate_image(prompt):
    print("🎨 Gemini resim oluşturuyor...")

    try:
        result = client.models.generate_image(
            model=IMAGE_MODEL,
            prompt=prompt
        )

        image_bytes = result.images[0].data
        with open("tweet_image.png", "wb") as f:
            f.write(image_bytes)

        print("✅ Resim başarıyla oluşturuldu!")
        return True

    except Exception as e:
        print("❌ Resim Hatası:", e)
        return False

# --------------------------------------------------------
# 3) TWITTER'A YÜKLEME
# --------------------------------------------------------
def post_tweet():
    content = get_artistic_idea()

    if generate_image(content["image_prompt"]):
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
                text=content["caption"],
                media_ids=[media.media_id]
            )

            print("✅ TWITTER GÖNDERİLDİ!")

        except Exception as e:
            print("❌ Twitter Hatası:", e)

    else:
        print("⚠️ Resim oluşturulamadı, tweet iptal.")

# --------------------------------------------------------
# BAŞLAT
# --------------------------------------------------------
if __name__ == "__main__":
    post_tweet()
