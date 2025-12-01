# bot.py – 4K AI Wallpaper Bot (Tamamen .env / Environment Variable destekli)

import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy

# ========================== TÜM KEYLER ÇEVRESEL DEĞİŞKENDEN ALINIYOR ==========================
GEMINI_API_KEY      = os.getenv("GEMINI_KEY")           # Senin Gemini key
CONSUMER_KEY        = os.getenv("API_KEY")
CONSUMER_SECRET     = os.getenv("API_SECRET")
ACCESS_TOKEN        = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET       = os.getenv("ACCESS_SECRET")
PIXELCUT_API_KEY    = os.getenv("PIXELCUT_API_KEY")     # sk_1156ff78fca542cba0742894bc631a7a (seninkini koy)

# Kontrol: Eksik key varsa hemen uyarı verip çıksın
required = ["GEMINI_KEY", "API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET", "PIXELCUT_API_KEY"]
missing = [var for var in required if os.getenv(var) is None]
if missing:
    print("EKSİK KEYLER VAR! Lütfen şunları ayarla:")
    for m in missing:
        print(f"   → {m}")
    exit()

# ========================== GEMİNİ PROMPT + CAPTION ==========================
def get_creative_content():
    print("Gemini düşünüyor...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        themes = [
            "Cyberpunk Tokyo Night", "Dreamy Cherry Blossom", "Interstellar Nebula", "Crystal Cave",
            "Floating Sky Islands", "Neon Retro Arcade", "Golden Desert Dunes", "Ancient Underwater Ruins",
            "Steampunk Airships", "Aurora Borealis Iceland", "Holographic City", "Macro Crystal World"
        ]
        theme = random.choice(themes)

        prompt_instruction = f"""
        Tema: {theme}
        Görev: Flux Realism için ultra detaylı İngilizce prompt + kısa tweet caption yaz.
        Zorunlu kelimeler: 8k resolution, ultra detailed, sharp focus, photorealistic, masterpiece
        Yasak: blur, blurry, bokeh, low quality
        Format: PROMPT: [prompt] ||| CAPTION: [caption]
        """
        response = model.generate_content(prompt_instruction).text.strip()
        
        if "|||" not in response:
            raise Exception("Format hatası")

        prompt, caption = response.split("|||", 1)
        prompt = prompt.replace("PROMPT:", "").strip() + ", masterpiece, 8k uhd, ultra sharp"
        caption = caption.replace("CAPTION:", "").strip()

        print(f"Tema: {theme}")
        return prompt, caption

    except Exception as e:
        print(f"Gemini hatası: {e}")
        return ("cyberpunk neon city rain reflections, ultra detailed, 8k", 
                "Lost in the neon 🌃✨ #AIArt")

# ========================== POLLİNATİONS RESİM ==========================
def download_base_image(prompt):
    print("Pollinations ile resim üretiliyor (Flux Realism)...")
    encoded = requests.utils.quote(prompt)
    seed = random.randint(1, 999999)
    url = f"https://pollinations.ai/p/{encoded}?model=flux-realism&width=768&height=1344&seed={seed}&nologo=true&enhance=true"
    
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 50000:
            print("Temel resim hazır!")
            return r.content
    except: pass
    return None

# ========================== PIXELCUT 4X UPSCALER → GERÇEK 4K ==========================
def pixelcut_upscale(image_bytes):
    print("Pixelcut ile 4K'ya yükseltiliyor... (4x upscale)")
    url = "https://api.pixelcut.ai/v1/image-upscaler/upscale"
    payload = {
        "image": base64.b64encode(image_bytes).decode('utf-8'),
        "scale": 4
    }
    headers = {
        "Authorization": f"Bearer {PIXELCUT_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        if resp.status_code == 200:
            result_url = resp.json().get("result_url")
            if result_url:
                final = requests.get(result_url, timeout=60).content
                print("4K RESİM TAMAM! Ultra net")
                return final
        else:
            print(f"Pixelcut hata: {resp.status_code} → {resp.text}")
    except Exception as e:
        print(f"Pixelcut bağlantı hatası: {e}")
    return None

# ========================== TWEET AT ==========================
def tweet_image(image_bytes, caption):
    filename = "4k_wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(image_bytes)

    print("X'e (Twitter) yükleniyor...")
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(filename)

        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        client.create_tweet(
            text=caption + " #AIArt #4K #Wallpaper #DigitalArt",
            media_ids=[media.media_id]
        )
        print("TWEET BAŞARIYLA ATILDI!")
        os.remove(filename)
    except Exception as e:
        print(f"Twitter hatası: {e}")

# ========================== ANA PROGRAM ==========================
if __name__ == "__main__":
    print("\n4K AI WALLPAPER BOT BAŞLADI!\n")
    
    prompt, caption = get_creative_content()
    print(f"Prompt: {prompt[:120]}...")
    print(f"Caption: {caption}\n")

    base = download_base_image(prompt)
    if not base:
        print("Resim üretilemedi!")
        exit()

    final = pixelcut_upscale(base) or base  # 4K olmazsa orijinali kullan

    tweet_image(final, caption)
