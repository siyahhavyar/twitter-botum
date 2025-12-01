import tweepy
import os
import time
import json
import random
import requests
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- 6 MOTORLU YEDEK DEPO ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),
    os.environ.get('HF_TOKEN_1'),
    os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'),
    os.environ.get('HF_TOKEN_4'),
    os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR (DÜZELTİLDİ) ---
genai.configure(api_key=GEMINI_KEY)
# GARANTİ MODEL: gemini-pro
model = genai.GenerativeModel('gemini-pro')

# GARANTİ ADRES: Klasik API
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def get_artistic_idea():
    print("🧠 Gemini (Pro) düşünüyor...")
    
    prompt_emir = """
    Sen profesyonel bir dijital sanatçısın. Twitter için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    GÖREVİN:
    1. Minimalist, Cyberpunk, Uzay, Doğa veya Soyut konulardan BENZERSİZ bir sahne hayal et.
    2. Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı bir açıklama ve hashtagler.",
      "image_prompt": "Resim için İNGİLİZCE prompt. Şunları EKLE: 'vertical wallpaper, 8k resolution, photorealistic, masterpiece, cinematic lighting, sharp focus'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        if text.startswith("json"): text = text[4:] 
        data = json.loads(text)
        print(f"✅ Fikir Bulundu: {data['caption']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu kullanılıyor.")
        return {
            "caption": "Serenity 🌌 #Wallpaper #Art",
            "image_prompt": "A majestic mountain reflection in a calm lake at night, starry sky, cinematic, 8k, vertical"
        }

def query_huggingface(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def generate_image_raw(prompt):
    # Tüm anahtarları sırayla dener
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Anahtar deneniyor...")
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "text, watermark, blurry, low quality, distorted, ugly",
                "width": 768, 
                "height": 1344
            }
        }
        
        try:
            response = query_huggingface(payload, token)
            
            # MODEL UYUYORSA (503) - BEKLE
            if response.status_code == 503:
                print("💤 Model ısınıyor... 20 saniye bekleniyor...")
                time.sleep(20)
                print("🔄 Tekrar deneniyor...")
                response = query_huggingface(payload, token)
            
            if response.status_code == 200:
                with open("tweet_image.jpg", "wb") as f:
                    f.write(response.content)
                print(f"✅ Resim Başarıyla İndirildi! ({i+1}. Anahtar)")
                return True
            else:
                print(f"❌ Hata Kodu: {response.status_code} - Mesaj: {response.text}")
                
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")
            
    print("🚨 HATA: Hiçbir anahtar resmi çizemedi.")
    return False

def post_tweet():
    content = get_artistic_idea()
    
    if generate_image_raw(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="tweet_image.jpg")
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER BAŞARILI!")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("⚠️ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()
