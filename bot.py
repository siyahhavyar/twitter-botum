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
DEEPAI_KEY = os.environ['DEEPAI_KEY']  # Yeni Anahtarımız

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_artistic_idea():
    print("🧠 Gemini sanat yönetmeni modunda...")
    
    prompt_emir = """
    Sen profesyonel bir dijital sanatçısın. Twitter için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    GÖREVİN:
    1. Minimalist, Cyberpunk, Uzay, Doğa, Sürrealizm veya Geometri konularından birini seç.
    2. Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı bir açıklama ve hashtagler.",
      "image_prompt": "Resim için İNGİLİZCE prompt. Şunları EKLE: 'surrealist art, 8k resolution, masterpiece, cinematic lighting, sharp focus, vertical wallpaper style'."
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
            "caption": "Cyber City 🌃 #Wallpaper #Art",
            "image_prompt": "Futuristic cyberpunk city street at night with neon lights, raining, cinematic, 8k, vertical"
        }

def generate_image_deepai(prompt):
    print("🎨 DeepAI Resmi Çiziyor...")
    
    try:
        # DeepAI API İsteği
        r = requests.post(
            "https://api.deepai.org/api/text2img",
            data={
                'text': prompt,
                'grid_size': '1', # Tek resim
            },
            headers={'api-key': DEEPAI_KEY}
        )
        
        response_json = r.json()
        
        if 'output_url' in response_json:
            image_url = response_json['output_url']
            
            # DeepAI bir link verir, o linkten resmi indirmemiz lazım
            print("⬇️ Resim indiriliyor...")
            img_data = requests.get(image_url).content
            
            with open("tweet_image.jpg", "wb") as f:
                f.write(img_data)
                
            print("✅ Resim Hazır!")
            return True
        else:
            print(f"❌ DeepAI Hatası: {response_json}")
            return False
            
    except Exception as e:
        print(f"❌ Bağlantı Hatası: {e}")
        return False

def post_tweet():
    content = get_artistic_idea()
    
    if generate_image_deepai(content['image_prompt']):
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
