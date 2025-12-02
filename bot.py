import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# SADECE BUNLAR LAZIM
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Eksik kontrol (sadece 6 tane)
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","REPLICATE_API_TOKEN"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    themes = ["Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → ultra detaylı photorealistic prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text.strip()
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "futuristic cyberpunk city night rain reflections, ultra detailed, 8k"
        caption = "Neon dreams"
    return prompt, caption

# REPLICATE – 1024×1024 HD (Güncel hash ile!)
def replicate_image(prompt):
    print("Replicate ile 1024×1024 HD resim üretiliyor...")
    url = "https://api.replicate.com/v1/predictions"
    headers = {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "version": "stability-ai/sdxl:c221b2b8a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # Güncel SDXL hash (2025 stabil)
        "input": {
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1,
            "num_inference_steps": 28,
            "guidance_scale": 7.5  # Kalite için
        }
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code != 201: 
            print(f"Replicate create error: {r.status_code} - {r.text[:200]}")
            return None
        pred_id = r.json()["id"]
        print(f"Prediction ID: {pred_id} - İşlem başladı...")
        for i in range(30):  # Max 3 dk bekle (6 sn aralık)
            status = requests.get(f"{url}/{pred_id}", headers=headers, timeout=30).json()
            if status["status"] == "succeeded":
                img_url = status["output"][0]
                img = requests.get(img_url, timeout=60).content
                if len(img) > 50000:
                    print("1024×1024 HD RESİM HAZIR! (SDXL native kalite)")
                    return img
            elif status["status"] == "failed":
                print(f"Replicate failed: {status.get('error', 'Unknown')}")
                return None
            time.sleep(6)
        print("Replicate timeout - Resim hazır değil.")
        return None
    except Exception as e:
        print(f"Replicate exception: {e}")
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
    print("\nREPLICATE 1024×1024 HD BOT ÇALIŞIYOR (Güncel hash ile!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = replicate_image(prompt)
    if not img:
        print("Resim üretilemedi → Tweet atılmadı")
        exit(1)
    tweet(img, caption)
