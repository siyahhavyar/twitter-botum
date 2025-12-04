import os
import asyncio
import random
import google.generativeai as genai
import tweepy
import perchance  # Unofficial Perchance API (pip install perchance)

# ONLY THESE ARE NEEDED (No extra keys!)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

# Check for missing keys
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"MISSING: {var}")
        exit(1)

def get_completely_random_wallpaper():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    instruction = """
    You are a creative phone wallpaper artist.
    Come up with ONE completely original, beautiful, aesthetic wallpaper idea.
    
    Allowed styles (only these):
    - nature, forest, mountains, ocean, sunset, flowers, animals
    - fantasy forest, magical creatures, fairy tale, enchanted
    - minimal, pastel, cozy, soft colors, dreamy
    - vintage, retro, polaroid, old film
    - abstract watercolor, ink art, soft shapes
    - surreal landscapes, floating islands, clouds
    - cottagecore, garden, books, coffee, candles

    STRICTLY FORBIDDEN:
    - cyberpunk
