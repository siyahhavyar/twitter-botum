import os
import requests
import random
import google.generativeai as genai
import tweepy

# KEYLER
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

# Eksik kontrol
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_random_wallpaper():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    instruction = """
    You are a creative phone wallpaper artist.
    Create ONE completely unique, beautiful, aesthetic vertical phone wallpaper idea.
    Only nature, fantasy, cozy, dreamy, vintage, pastel, surreal, cottagecore styles.
    NO cyberpunk, technology, city, robot, neon.
    Output ONLY in English.
    Format exactly:
    PROMPT: [ultra detailed prompt] ||| CAPTION: [short English caption]
    """
    
    try:
        resp = model.generate_content(instruction).text.strip()
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", vertical phone wallpaper, 9:16 ratio, ultra detailed, masterpiece, 8k"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "soft pastel cherry blossom forest at twilight, vertical phone wallpaper, 9:16, ultra detailed, 8k"
        caption = "Whispers of spring"
    
    return prompt, caption

# DEZGO – %100 ÇALIŞAN ÜCRETSİZ HD (1080x1920)
def dezgo_image(prompt):
    print("Dezgo ile 1080x1920 dikey wallpaper üretiliyor (kesin çalışır)...")
    encoded = requests.utils.quote(prompt)
    url = f"https://dezgo.com/api/v1/generate?prompt={encoded}&width=1080&height=1920&model=flux&steps=30&guidance=7"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://dezgo.com/",
        "Accept": "image/*"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=90)
        if r.status_code == 200 and len(r.content) > 100000:
            print("DEZGO → DİKEY HD WALLPAPER HAZIR!")
            return r.content
    except Exception as e:
        print(f"Dezgo hatası: {e}")
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
    client.create_tweet(text=caption + " #Wallpaper #Aesthetic #Nature #Art", media_ids=[media.media_id])
    print("TWEET GÖNDERİLDİ!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nDEZGO %100 ÇALIŞAN ÜCRETSİZ WALLPAPER BOTU ÇALIŞIYOR!\n")
    
    prompt, caption = get_random_wallpaper()
    print(f"Fikir: {caption}")
    print(f"Prompt: {prompt[:120]}...\n")
    
    img = dezgo_image(prompt)
    if not img:
        print("Bugün bir hata oldu, yarın tekrar dene :)")
        exit(1)
    
    tweet(img, caption)
