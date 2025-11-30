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

# --- HUGGING FACE TOKEN LİSTESİ (6 tane varsa hepsini ekle) ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),
    os.environ.get('HF_TOKEN_1'),
    os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'),
    os.environ.get('HF_TOKEN_4'),
    os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t]  # Boşları temizle

# --- GEMINI AYARLARI (2025'te çalışan model) ---
genai.configure(api_key=GEMINI_KEY)
# 2025'te en stabil ve hızlı çalışan model:
model = genai.GenerativeModel('gemini-2.5-flash')

# --- HUGGING FACE API (Daha az token yakan + hızlı yüklenen model) ---
# SD 2.1 çok daha az 503 verir, tokenın daha uzun gider
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

def get_autonomous_idea():
    print("Gemini sanat yönetmeni modunda...")
    
    prompt_emir = """
    Sen benim kişisel dijital sanat asistanımsın. Twitter hesabım için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    Görevin:
    1. Minimalist Doğa, Cyberpunk, Uzay, Sürrealizm veya Estetik Geometri konularından birini seç.
    2. Benzersiz, çok havalı ve 8K kalitesinde duracak bir sahne kurgula.
    
    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı, emojili bir açıklama. Hashtagler ekle (#Minimalist #Wallpaper #Art #4K #Aesthetic).",
      "image_prompt": "Resmi çizecek yapay zeka için İNGİLİZCE prompt. Şunları MUTLAKA ekle: 'minimalist, clean lines, vertical wallpaper, highly detailed, 8k resolution, masterpiece, cinematic lighting, sharp focus, beautiful composition --no text, no watermark'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"Fikir Bulundu: {data['caption'][:50]}...")
        return data
    except Exception as e:
        print(f"Gemini Hatası ({e}), yedek konu kullanılıyor.")
        return {
            "caption": "Endless horizon at sunset Minimalist vibes\n\n#Wallpaper #Minimalist #Art #Aesthetic",
            "image_prompt": "minimalist endless ocean sunset, single boat silhouette, warm colors, vertical wallpaper, 8k, masterpiece, cinematic lighting --no text"
        }

def query_huggingface(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response

def generate_image_raw(prompt):
    random.shuffle(TOKEN_LISTESI)  # Tokenları karıştır, eşit dağılsın
    
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"{i+1}/{len(TOKEN_LISTESI)}. token deneniyor...")
        
        payload = {
            "inputs": prompt + ", vertical phone wallpaper, 8k, ultra detailed",
            "parameters": {
                "negative_prompt": "text, watermark, logo, blurry, low quality, deformed, ugly, bad anatomy",
                "width": 512,
                "height": 768,   # Dikey wallpaper için mükemmel
                "num_inference_steps": 28,
                "guidance_scale": 7.5
            }
        }
        
        for attempt in range(4):  # Her token için maksimum 4 deneme
            try:
                response = query_huggingface(payload, token)
                
                if response.status_code == 503:
                    wait = response.json().get("estimated_time", 25)
                    print(f"Model yükleniyor... {wait + 10} saniye bekleniyor (Deneme {attempt+1}/4)")
                    time.sleep(wait + 10)
                    continue
                
                if response.status_code == 200:
                    with open("tweet_image.jpg", "wb") as f:
                        f.write(response.content)
                    print(f"RESİM ÇİZİLDİ! ({i+1}. token, {attempt+1}. denemede)")
                    return True
                    
                else:
                    print(f"Hata {response.status_code}: {response.text[:100]}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"Bağlantı hatası: {e}")
                time.sleep(5)
        
        print(f"{i+1}. token başarısız oldu.")
    
    print("HİÇBİR TOKEN RESİM ÇİZEMEDİ!")
    return False

def post_tweet():
    idea = get_autonomous_idea()
    
    if generate_image_raw(idea['image_prompt']):
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
            client.create_tweet(text=idea['caption'], media_ids=[media.media_id])
            print("TWEET BAŞARIYLA ATILDI!")
            
        except Exception as e:
            print(f"Twitter hatası: {e}")
    else:
        print("Resim çizilemedi, tweet atılmadı.")

if __name__ == "__main__":
    post_tweet()