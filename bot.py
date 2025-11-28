import tweepy
import os
import time
import json
import requests
import random
import google.generativeai as genai

# --- ŞİFRELER (KASADAN ÇEKİLİR) ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY'] # Gemini Anahtarı (Ekli değilse ekle!)

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_smart_wallpaper_idea():
    print("🧠 Gemini yeni bir duvar kağıdı fikri düşünüyor...")
    
    # Twitter için özel prompt: Minimalist, Estetik ve Havalı şeyler istiyoruz.
    prompt_emir = """
    Sen profesyonel bir dijital sanatçısın. Twitter için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    Konseptler: Minimalist, Cyberpunk, Doğa, Uzay, Soyut, Popüler Kültür (Marvel, Anime vb.), Synthwave.
    
    Görevin:
    1. Bu konseptlerden rastgele birini seç ve çok havalı, insanların telefonuna arka plan yapmak isteyeceği bir sahne kurgula.
    2. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {
      "caption": "Twitter için kısa, etkileyici, emojili İngilizce veya Türkçe (karışık olabilir) bir açıklama yaz. En sona bolca ilgili hashtag ekle.",
      "image_prompt": "Resim için İNGİLİZCE, çok detaylı, cinematic, 8k, photorealistic, vertical wallpaper prompt yaz."
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
            "caption": "Lost in Space 🌌 \n\n#Wallpaper #Space #Art #AI",
            "image_prompt": "Astronaut floating in deep space nebula, glowing colors, cinematic, 8k, vertical, masterpiece"
        }

# --- YENİ SINIRSIZ RESSAM (POLLINATIONS) ---
def generate_image_pollinations(prompt):
    print(f"🎨 Pollinations (Flux) Çiziyor...")
    
    # Promptu URL uyumlu hale getir
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical wallpaper, 8k, masterpiece, high quality")
    
    # Model: Flux (Çok kalitelidir) | Boyut: 768x1344 (Telefon Ekranı)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=768&height=1344&model=flux&seed={random.randint(1, 100000)}"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open("twitter_post.jpg", 'wb') as f:
                f.write(response.content)
            print("✅ Resim İndirildi!")
            return True
        else:
            print(f"❌ Çizim Hatası Kodu: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ İndirme Hatası: {e}")
        return False

def post_tweet():
    # 1. Fikri Bul
    content = get_smart_wallpaper_idea()
    
    # 2. Resmi Çiz (Sınırsız)
    if generate_image_pollinations(content['image_prompt']):
        
        # 3. Paylaş
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="twitter_post.jpg")
            
            # Caption
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER BAŞARILI! (Sınırsız Mod)")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()
