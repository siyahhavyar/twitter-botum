import os
import requests
import random
import tweepy
import google.generativeai as genai
import asyncio
from perchance import ImageGenerator  # Unofficial Perchance API (pip install perchance)

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
        "aspect
