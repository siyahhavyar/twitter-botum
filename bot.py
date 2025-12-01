import tweepy
import os
import json
from google import genai

# --- API Anahtarları ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- Gemini Client ---
client = genai.Client(api_key=GEMINI_KEY)
MODEL = "gemini-1.5-flash"

# -------------------------------------------------------
# 1) Gemini ile JSON formatında fikir oluşturma
# -------------------------------------------------------
def get_artistic_idea():
    print("🧠 Gemini (1.5 Flash) düşünüyor...")

    prompt = """
    You are an AI that outputs STRICT JSON.

    Return ONLY:

    {
      "caption": "short english caption with hashtags",
      "image_prompt": "highly detailed aesthetic wallpaper prompt, must include: vertical wallpaper, 8k resolution, masterpiece, cinematic lighting"
    }
    """

    try:
        result = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        text = result.text.strip()
        text = text.replace("```json", "").replace("```", "")

        data = json.loads(text)
        print("✅ Fikir üretildi:", data["caption"])
        return data

    except Exception as e:
        print("⚠️ Gemini Hatası:", e)
        return {
            "caption": "Mystic Horizon ✨ #Wallpaper",
