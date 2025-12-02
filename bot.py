import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy

# TÜM KEYLER GİTHUB SECRETS'TEN GELİYOR
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
PIXELCUT_KEY    = os.getenv("PIXELCUT_API_KEY")
DEEPAI_KEY      = os.getenv("DEEPAI_API_KEY", "quickstart-QUdJIGlzIGNvbWluZy4uLi4K")  # ücretsiz test keyi

# Eksik key varsa hemen çıksın
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","PIXELCUT_API_KEY"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → Flux/DeepAI için ultra detaylı prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", 8k, ultra detailed, masterpiece"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "cyberpunk city night rain reflections, ultra detailed, 8k"
        caption = "Neon rain vibes"
    return prompt, caption

# DEEPAI → HD NATİVE (1024x1024)
def deepai_image(prompt):
    print("DeepAI HD resim üretiyor...")
    r = requests.post("https://api.deepai.org/api/text2img",
        headers={"api-key": DEEPAI_KEY},
        json={"text": prompt, "width": 1024, "height": 1024},
        timeout=90
    )
    if r.status_code == 200:
        url = r.json().get("output_url")
        if url:
            return requests.get(url, timeout=60).content
    return None

# PIXELCUT → 4K UPSCALE
def pixelcut_4k(img_bytes):
    print("Pixelcut 4x upscale → Gerçek 4K...")
    r = requests.post("https://api.pixelcut.ai/v1/image-upscaler/upscale",
        json={"image": base64.b64encode(img_bytes).decode(), "scale": 4},
        headers={"Authorization": f"Bearer {PIXELCUT_KEY}"},
        timeout=120
    )
    if r.status_code == 200:
        url = r.json().get("result_url")
        if url:
            return requests.get(url).content
    return None

# TWEET
def tweet(img_bytes, text):
    fn = "wall.jpg"
    open(fn,"wb").write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=text + " #AIArt #4K #Wallpaper", media_ids=[media.media_id])
    print("TWEET ATILDI!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nDEEPAI + PIXELCUT 4K BOT ÇALIŞIYOR\n")
    prompt, caption = get_prompt_caption()
    img = deepai_image(prompt)
    if not img:
        print("DeepAI başarısız, çıkılıyor.")
        exit(1)
    final = pixelcut_4k(img) or img
    tweet(final, caption)
