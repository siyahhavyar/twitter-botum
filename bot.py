import os
import asyncio
import random
import google.generativeai as genai
import tweepy
from perchance import ImageGenerator  # Unofficial Perchance library

# KEYS
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
    - cyberpunk, neon, technology, robot, city, sci-fi, futuristic, digital art, glitch

    Must be vertical phone wallpaper (9:16).
    Output ONLY in English.
    Format exactly:
    PROMPT: [ultra detailed English prompt] ||| CAPTION: [short beautiful English caption]
    """
    
    try:
        resp = model.generate_content(instruction).text.strip()
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, 8k, soft natural lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper, 9:16, ultra detailed, 8k"
        caption = "Whispers of spring"
    
    return prompt, caption

# UNOFFICIAL PERCHANCE API – FREE HD VERTICAL (No signup, works on Actions!)
async def perchance_image(prompt):
    print("Generating vertical HD wallpaper with Unofficial Perchance API (free)...")
    gen = ImageGenerator()
    try:
        async with await gen.image(prompt) as result:
            binary = await result.download()
            if len(binary) > 50000:
                print("PERCHANCE API → VERTICAL HD READY!")
                return binary
    except Exception as e:
        print(f"Perchance API error: {e}")
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "wallpaper.jpg"
    with open(fn, "wb") as f:
        f.write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=caption + " #Wallpaper #Aesthetic #Nature #Art", media_ids=[media.media_id])
    print("TWEET SUCCESSFULLY POSTED!")
    os.remove(fn)

# MAIN
if __name__ == "__main__":
    print("\nUNOFFICIAL PERCHANCE API FREE VERTICAL BOT RUNNING!\n")
    
    prompt, caption = get_completely_random_wallpaper()
    print(f"Idea: {caption}")
    print(f"Prompt: {prompt[:120]}...\n")
    
    # Run async for Perchance library
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    img = loop.run_until_complete(perchance_image(prompt))
    loop.close()
    
    if not img:
        print("Image generation failed today, try again tomorrow :)")
        exit(1)
    
    tweet(img, caption)
