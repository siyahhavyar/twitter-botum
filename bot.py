import os
import requests
import random
import google.generativeai as genai
import tweepy

# SADECE BUNLAR LAZIM (No Replicate/Pixelcut!)
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

# Eksik kontrol (sadece Twitter + Gemini)
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Steampunk City","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → ultra detaylı photorealistic prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text.strip()
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, high resolution 1024x1024, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "futuristic cyberpunk city night rain reflections, ultra detailed, high resolution 1024x1024, 8k"
        caption = "Neon dreams"
    return prompt, caption

# PERCHANCE – ÜCRETSİZ 1024x1024+ HD (No signup/credit!)
def perchance_image(prompt):
    print("Perchance ile ücretsiz 1024x1024+ HD resim üretiliyor...")
    # Perchance API-like GET (no key, no limit)
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded_prompt}&resolution=1024x1024&quality=high&seed={random.randint(1,100000)}"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and 'image' in r.headers['Content-Type']:
            img = r.content
            if len(img) > 50000:
                print("Ücretsiz HD RESİM HAZIR! (Perchance kalitesi, 4K'ya yakın)")
                return img
        print(f"Perchance error: {r.status_code}")
    except Exception as e:
        print(f"Perchance exception: {e}")
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
    client.create_tweet(text=caption + " #AIArt #Wallpaper #4K", media_ids=[media.media_id])
    print("TWEET ATILDI!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nPERCHANCE ÜCRETSİZ HD BOT ÇALIŞIYOR (No credit/signup!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = perchance_image(prompt)
    if not img:
        print("Resim üretilemedi → Tweet atılmadı")
        exit(1)
    tweet(img, caption)
