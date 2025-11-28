import tweepy
import os
import time
import json
import requests
import random
import google.generativeai as genai

# --- ŞİFRELER ---
# Hugging Face YOK. Sadece Twitter ve Gemini.
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_smart_wallpaper_idea():
    print("🧠 Gemini (Beyin) düşünüyor...")
    
    prompt_emir = """
    Sen profesyonel bir dijital sanatçısın. Twitter için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    Konseptler (Rastgele birini seç): 
    - Minimalist Doğa (Dağlar, deniz, orman)
    - Cyberpunk & Neon Şehirler
    - Uzay ve Astronot (Derinlik hissi)
    - Soyut Geometrik (Abstract)
    - Fantastik Manzara (Uçan adalar, büyülü orman)
    
    Görevin:
    1. Çok havalı, 8K kalitesinde, insanların telefonuna arka plan yapmak isteyeceği bir sahne kurgula.
    2. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {
      "caption": "Twitter için kısa, etkileyici, emojili bir açıklama yaz (İngilizce). En sona bolca hashtag ekle (#Wallpaper #4K #Art gibi).",
      "image_prompt": "Resim için İNGİLİZCE prompt. Şunları mutlaka içersin: 'cinematic lighting, 8k resolution, photorealistic, vertical wallpaper, hyper-detailed, masterpiece, sharp focus'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu: {data['caption'][:30]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu kullanılıyor.")
        return {
            "caption": "Neon City Rain ☔ \n\n#Wallpaper #Cyberpunk #4K #AIArt",
            "image_prompt": "Cyberpunk city street at night, heavy rain, neon lights reflecting on wet asphalt, futuristic cars, cinematic, 8k, vertical, masterpiece, sharp focus"
        }

# --- YENİ ULTRA KALİTE MOTORU: FLUX ---
def generate_image_flux(prompt):
    print(f"🎨 Flux Motoru Çiziyor (Ultra Kalite)...")
    
    # Promptun sonuna kalite garantileyen sihirli kelimeler ekliyoruz
    full_prompt = f"{prompt}, high resolution, 8k, uhd, sharp focus, best quality"
    prompt_encoded = requests.utils.quote(full_prompt)
    
    # Rastgele sayı (Seed) ekle ki her resim farklı olsun
    seed = random.randint(1, 999999)
    
    # POLLINATIONS URL (Model=Flux, Genişlik=768, Yükseklik=1344)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        # İndirme işlemi (Flux biraz ağır olduğu için süre tanıdık)
        response = requests.get(url, timeout=120) 
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open("twitter_post.jpg", 'wb') as f:
                f.write(response.content)
            print("✅ Resim İndirildi (Flux Kalitesi)!")
            return True
        else:
            print(f"❌ Sunucu Hatası veya Boş Resim: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ İndirme Hatası: {e}")
        return False

def post_tweet():
    # 1. Fikri Bul
    content = get_smart_wallpaper_idea()
    
    # 2. Resmi Çiz (FLUX ile)
    if generate_image_flux(content['image_prompt']):
        
        # 3. Paylaş
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="twitter_post.jpg")
            
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER BAŞARILI! (Cam Gibi Görüntü)")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()
