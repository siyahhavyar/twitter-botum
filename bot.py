import os
import requests
import google.generativeai as genai
import tweepy

# KEYS
GEMINI_KEY    = os.getenv("GEMINI_KEY")
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    instruction = """
    Create ONE beautiful vertical phone wallpaper idea (9:16).
    NO cyberpunk, sci-fi neon city robot technology.
    Only nature, fantasy, cozy, pastel, dreamy, cottagecore, forest, animals, flowers, sunset.
    Output exactly:
    PROMPT: [ultra detailed English prompt] ||| CAPTION: [short beautiful English caption]
    """
    try:
        resp = model.generate_content(instruction).text.strip()
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, best quality, 8k"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, 8k"
        caption = "Whispers of spring"
    return prompt, caption

# 2025'TE ÇALIŞAN TEK ÜCRETSİZ APİ: POLLINATIONS (no signup, no limit, 1080x1920 destekli)
def pollinations_image(prompt):
    print("Pollinations ile 1080x1920 dikey wallpaper üretiliyor (ücretsiz, limitsiz)...")
    url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1080&height=1920&seed={os.urandom(4).hex()}&nologo=true"
    try:
        r = requests.get(url, timeout=45)
        if r.status_code == 200 and len(r.content) > 100000:
            print("POLLINATIONS → DİKEY HD HAZIR!")
            return r.content
    except:
        pass
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "wallpaper.jpg"
    open(fn, "wb").write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=caption + " #Wallpaper #Aesthetic #AIArt", media_ids=[media.media_id])
    print("TWEET BAŞARIYLA GÖNDERİLDİ!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nPOLLINATIONS %100 ÇALIŞAN ÜCRETSİZ WALLPAPER BOTU\n")
    prompt, caption = get_prompt_caption()
    print(f"Fikir: {caption}")
    print(f"Prompt: {prompt[:100]}...\n")
    
    img = pollinations_image(prompt)
    if not img:
        print("Hata oldu, yarın tekrar dene :)")
        exit(1)
    
    tweet(img, caption)
