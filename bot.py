import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# --- ŞİFRELER (Horde key opsiyonel) ---
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
HORDE_API_KEY   = os.getenv("HORDE_API_KEY") or "0000000000"

# Eksik kontrolü
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    # Model ismini en stabil olanla güncel tutuyorum (Hata almamak için)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    themes = ["Neon Forest", "Space Nebula", "Crystal Cave", "Floating Islands", "Golden Desert", "Steampunk City", "Aurora Mountains", "Cyberpunk Street", "Underwater Ruins"]
    theme = random.choice(themes)
    
    # İNGİLİZCE VE DİKEY OLMA EMRİ BURADA
    instruction = f"""
    Theme: {theme}. 
    Task: Create an ultra-detailed photorealistic image prompt and a short cool caption.
    Constraint 1: Output LANGUAGE must be STRICTLY ENGLISH.
    Constraint 2: Image prompt must target Vertical/Portrait Aspect Ratio (9:16).
    Format: PROMPT: [...] ||| CAPTION: [...]
    """
    
    resp = model.generate_content(instruction).text.strip()
    try:
        p, c = resp.split("|||")
        # Prompt'a dikey olması için teknik terimler ekliyoruz
        prompt = p.replace("PROMPT:", "").strip() + ", vertical wallpaper, 9:16 aspect ratio, portrait mode, ultra detailed, sharp focus, 8k masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "beautiful mountain landscape, vertical wallpaper, portrait, ultra detailed, 8k"
        caption = "Nature vibes 🌿 #wallpaper"
    
    return prompt, caption

# PERCHANCE – ÜCRETSİZ HD (DİKEY MOD)
def perchance_image(prompt):
    print("Perchance ile DİKEY (1080x1920) resim üretiliyor...")
    encoded = requests.utils.quote(prompt)
    
    # RESOLUTION AYARINI 1080x1920 YAPTIK (PORTRAIT)
    url = f"https://perchance.org/ai-text-to-image-generator?prompt={encoded}&resolution=1080x1920&quality=high&seed={random.randint(1,100000)}&model=flux"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "https://perchance.org/ai-text-to-image-generator",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        r = requests.get(url, headers=headers, timeout=60)
        print(f"Perchance status: {r.status_code}")
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            img = r.content
            if len(img) > 50000:
                print("✅ DİKEY HD RESİM HAZIR! (Perchance)")
                return img
            else:
                print(f"Perchance error: {r.text[:200]}")
    except Exception as e:
        print(f"Perchance exception: {e}")
    return None

# HORDE – Yedek (DİKEY MOD)
def horde_image(prompt):
    print("AI Horde ile DİKEY (768x1344) resim üretiliyor...")
    url = "https://stablehorde.net/api/v2/generate/async"
    headers = {"apikey": HORDE_API_KEY}
    
    payload = {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
            "seed_variation": 1,
            # DİKEY AYARLAR (SDXL için en iyi dikey oran budur)
            "width": 768,
            "height": 1344,
            "karras": True,
            "steps": 25,
            "n": 1
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["SDXL 1.0"]
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code != 202:
            print(f"Horde create error: {r.text[:300]}")
            return None
        job_id = r.json()["id"]
        print(f"Job ID: {job_id} - Üretim başladı...")
        
        for i in range(200): 
            check = requests.get(f"https://stablehorde.net/api/v2/generate/check/{job_id}", timeout=30)
            if check.status_code == 200:
                check_json = check.json()
                if check_json["done"]:
                    status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{job_id}", timeout=30)
                    if status.status_code == 200:
                        generations = status.json()["generations"]
                        if generations:
                            img_url = generations[0]["img"]
                            img = requests.get(img_url, timeout=60).content
                            if len(img) > 50000:
                                print("✅ DİKEY HD RESİM HAZIR! (Horde)")
                                return img
            time.sleep(6)
        print("AI Horde timeout.")
        return None
    except Exception as e:
        print(f"AI Horde exception: {e}")
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
    
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    
    # İngilizce etiketler ekliyoruz
    client.create_tweet(text=caption + " \n\n#Wallpaper #Art #4K #Aesthetic #Background", media_ids=[media.media_id])
    print("✅ TWEET BAŞARIYLA ATILDI!")
    os.remove(fn)

# ANA DÖNGÜ
if __name__ == "__main__":
    print("\nPERCHANCE + HORDE (DİKEY/ENGLISH) BOT ÇALIŞIYOR!\n")
    
    # 1. Gemini İngilizce Konu ve Prompt Üretsin
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:100]}...")
    print(f"Caption: {caption}\n")

    # 2. Önce Perchance (En Kaliteli) Dikey Çizsin
    img = perchance_image(prompt)
    
    # 3. Olmazsa Horde Dikey Çizsin
    if not img:
        img = horde_image(prompt)
        
    # 4. Paylaş
    if not img:
        print("❌ Resim üretilemedi → Tweet atılmadı")
        exit(1)
        
    tweet(img, caption)
