import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy
import json  # Replicate için eklendi

# TÜM KEYLER GİTHUB SECRETS'TEN
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
PIXELCUT_KEY    = os.getenv("PIXELCUT_API_KEY")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # Yeni: Replicate token'ını secrets'e koy

# Eksik key kontrolü
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","PIXELCUT_API_KEY","REPLICATE_API_TOKEN"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Steampunk City","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(
        f"Tema: {theme}\n"
        "Ultra detaylı, photorealistic bir AI sanat prompt’u yaz + kısa etkileyici tweet caption.\n"
        "Format: PROMPT: [prompt burada] ||| CAPTION: [caption burada]"
    ).text.strip()

    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, 8k, masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "futuristic cyberpunk city at night, neon lights, rain reflections, ultra detailed, 8k, masterpiece"
        caption = "Lost in the neon"
    return prompt, caption

# REPLICATE – SADECE BU VAR, ÜCRETSİZ HD (1024x1024 native SDXL)
def replicate_image(prompt):
    print("Replicate ile HD resim üretiliyor (SDXL modeli)...")
    # SDXL model version (stabil, ücretsiz)
    version = "stability-ai/stable-diffusion-xl-base-1.0:93cc1a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a"  # Güncel SDXL version
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": version,
        "input": {
            "prompt": prompt,
            "width": 1024,      # HD genişlik
            "height": 1024,     # HD yükseklik
            "num_outputs": 1,
            "num_inference_steps": 20  # Kalite için
        }
    }
    try:
        # Prediction oluştur
        create_resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if create_resp.status_code != 201:
            print(f"Replicate create hata: {create_resp.status_code} → {create_resp.text[:200]}")
            return None

        pred_id = create_resp.json()["id"]
        
        # Poll et (resim hazır olana kadar, max 2 dk)
        status_url = f"{url}/{pred_id}"
        for _ in range(20):  # 20 deneme, 6 sn aralık
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            if status_resp.status_code == 200:
                result = status_resp.json()
                if result["status"] == "succeeded":
                    img_url = result["output"][0]  # İlk resim URL
                    img_bytes = requests.get(img_url, timeout=60).content
                    if len(img_bytes) > 50000:
                        print("Replicate HD resim hazır! (1024x1024 native)")
                        return img_bytes
                elif result["status"] == "failed":
                    print(f"Replicate failed: {result.get('error', 'Unknown')}")
                    return None
            time.sleep(6)  # Bekle
        
        print("Replicate timeout (resim hazır değil).")
        return None

    except Exception as e:
        print(f"Replicate exception: {e}")
        return None

# PIXELCUT 4K UPSCALE (Opsiyonel, Replicate zaten HD)
def pixelcut_4k(img_bytes):
    print("Pixelcut ile 4x upscale → Ekstra 4K...")
    try:
        r = requests.post(
            "https://api.pixelcut.ai/v1/image-upscaler/upscale",
            json={"image": base64.b64encode(img_bytes).decode("utf-8"), "scale": 4},
            headers={"Authorization": f"Bearer {PIXELCUT_KEY}"},
            timeout=120
        )
        if r.status_code == 200:
            result_url = r.json().get("result_url")
            if result_url:
                final = requests.get(result_url, timeout=60).content
                print("4K RESİM HAZIR!")
                return final
        else:
            print(f"Pixelcut hata: {r.status_code}")
    except Exception as e:
        print(f"Pixelcut exception: {e}")
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "4k_wallpaper.jpg"
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
    client.create_tweet(text=caption + " #AIArt #4K #Wallpaper", media_ids=[media.media_id])
    print("TWEET BAŞARIYLA ATILDI!")
    os.remove(fn)

# ANA PROGRAM – REPLICATE + PIXELCUT
if __name__ == "__main__":
    import time  # Poll için eklendi
    print("\nREPLICATE + PIXELCUT 4K BOT ÇALIŞIYOR (DeepAI de yasaklandı!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = replicate_image(prompt)
    if not img:
        print("Replicate resim üretemedi → Tweet atılmadı (kalite düşürmek yok!)")
        exit(1)

    final_img = pixelcut_4k(img) or img  # Upscale patlarsa HD Replicate gider
    tweet(final_img, caption)
