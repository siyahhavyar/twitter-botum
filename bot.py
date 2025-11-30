import subprocess
import sys
# GitHub Actions'ta eksik paketleri otomatik kur
subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai", "tweepy", "requests"])

import tweepy
import os
import time
import json
import requests
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']
REPLICATE_TOKEN = os.environ.get('REPLICATE_TOKEN')  # <-- Senin az önce eklediğin!

# --- GEMINI (sadece metin için, quota yemiyor) ---
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')  # Text-only, free quota var

# --- REPLICATE (resim üretimi) ---
REPLICATE_API = "https://api.replicate.com/v1/predictions"

def get_caption_and_prompt():
    print("Gemini fikir & prompt üretiyor...")
    prompt = """
    Twitter için dikey duvar kağıdı botumdasın.
    Minimalist Doğa, Cyberpunk, Uzay, Sürrealizm veya Geometrik temalardan birini seç.
    Sadece şu JSON formatında cevap ver:
    {
      "caption": "İngilizce kısa havalı caption + emoji + hashtagler (#Wallpaper #Art #Minimalist #Aesthetic)",
      "image_prompt": "İngilizce detaylı prompt, dikey telefon duvar kağıdı, 8k, no text, no watermark"
    }
    """
    try:
        resp = gemini_model.generate_content(prompt)
        text = resp.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"Caption: {data['caption'][:60]}...")
        return data["caption"], data["image_prompt"]
    except Exception as e:
        print(f"Gemini hatası: {e} → Yedek kullanılıyor")
        return (
            "Floating islands in twilight Minimalist dream\n\n#Wallpaper #Art #Aesthetic",
            "minimalist floating islands, purple twilight sky, calm ocean below, vertical phone wallpaper, 8k, masterpiece --no text"
        )

def generate_image_with_replicate(prompt):
    if not REPLICATE_TOKEN:
        print("REPLICATE_TOKEN eksik! GitHub Secrets'e ekle.")
        return False

    print("Replicate ile resim üretiliyor (Flux / Imagen 4)...")
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": "1f208f8c8705b9c1389a20dae6d317b9873dacfb9f8236a24d1e57c68e2d1b9e",  # Flux Schnell (hızlı & kaliteli)
        "input": {
            "prompt": prompt + ", vertical phone wallpaper, ultra detailed, 8k, masterpiece",
            "aspect_ratio": "9:16",
            "num_inference_steps": 4,
            "guidance_scale": 3.5
        }
    }

    try:
        r = requests.post(REPLICATE_API, headers=headers, json=payload, timeout=180)
        if r.status_code != 201:
            print(f"Replicate başlatma hatası: {r.status_code} - {r.text}")
            return False

        prediction_id = r.json()["id"]
        url = f"{REPLICATE_API}/{prediction_id}"

        # Sonucu bekle
        while True:
            res = requests.get(url, headers=headers)
            data = res.json()
            if data["status"] == "succeeded":
                img_url = data["output"][0]
                img_data = requests.get(img_url).content
                with open("tweet_image.jpg", "wb") as f:
                    f.write(img_data)
                print("RESİM HAZIR! Replicate başarıyla çizdi")
                return True
            elif data["status"] in ["failed", "canceled"]:
                print(f"Replicate hata verdi: {data.get('error')}")
                return False
            time.sleep(4)

    except Exception as e:
        print(f"Replicate bağlantı hatası: {e}")
        return False

def post_tweet():
    caption, image_prompt = get_caption_and_prompt()

    if generate_image_with_replicate(image_prompt):
        print("Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            media = api.media_upload("tweet_image.jpg")
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print("TWEET BAŞARIYLA GİTTİ!")
        except Exception as e:
            print(f"Twitter hatası: {e}")
    else:
        print("Resim üretilemedi, tweet atılmadı.")

if __name__ == "__main__":
    post_tweet()
