import tweepy
import os
import time
import json
import random
import google.generativeai as genai
from huggingface_hub import InferenceClient

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- DEV YEDEK DEPOSU (6 MOTORLU) ---
# GitHub'a eklediğin HF_TOKEN_1, HF_TOKEN_2 ... HF_TOKEN_6 hepsini buraya ekledim.
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),    # Ana Token
    os.environ.get('HF_TOKEN_1'),  # Yedek 1
    os.environ.get('HF_TOKEN_2'),  # Yedek 2
    os.environ.get('HF_TOKEN_3'),  # Yedek 3
    os.environ.get('HF_TOKEN_4'),  # Yedek 4
    os.environ.get('HF_TOKEN_5'),  # Yedek 5
    os.environ.get('HF_TOKEN_6')   # Yedek 6
]
# Boş olanları temizle (Hepsini girmemiş olsan bile hata vermez)
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_smart_wallpaper_idea():
    print("🧠 Gemini içerik düşünüyor...")
    
    prompt_emir = """
    Sen profesyonel bir dijital sanatçısın. Twitter için 'Duvar Kağıdı' tasarlıyorsun.
    Konseptler: Minimalist Doğa, Cyberpunk, Uzay, Soyut, Neon Şehir, Fantastik.
    
    Görevin:
    1. Çok havalı, 8K kalitesinde, net ve pürüzsüz bir sahne kurgula.
    2. SADECE aşağıdaki JSON formatında cevap ver:
    
    {
      "caption": "Twitter için İngilizce, kısa, havalı, emojili açıklama ve hashtagler.",
      "image_prompt": "Resim için İNGİLİZCE, 8k resolution, cinematic lighting, photorealistic, vertical wallpaper, sharp focus, masterpiece prompt."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu: {data['caption'][:30]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu.")
        return {
            "caption": "Deep Space 🌌 \n\n#Wallpaper #Space #8K",
            "image_prompt": "Nebula in deep space, glowing stars, cinematic, 8k, vertical, masterpiece"
        }

def generate_high_quality_image(prompt):
    # Sırayla anahtarları dener
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Ressam Anahtarı deneniyor...")
        try:
            client = InferenceClient(model=repo_id, token=token)
            
            # --- KALİTE AYARLARI ---
            image = client.text_to_image(
                f"{prompt}, vertical wallpaper, aspect ratio 2:3, 8k resolution, photorealistic, masterpiece, highly detailed, --no text, --no blur", 
                width=768, height=1344
            )
            image.save("twitter_post.jpg")
            print(f"✅ BAŞARILI! ({i+1}. Anahtar çalıştı)")
            return True
        except Exception as e:
            print(f"❌ {i+1}. Anahtar Hatası (Kota dolmuş olabilir): {e}")
            print("Diğer anahtara geçiliyor...")
            time.sleep(2) 
            
    print("🚨 HATA: Tüm anahtarlar denendi ama başarısız oldu.")
    return False

def post_tweet():
    content = get_smart_wallpaper_idea()
    
    if generate_high_quality_image(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="twitter_post.jpg")
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER BAŞARILI!")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemedi.")

if __name__ == "__main__":
    post_tweet()
