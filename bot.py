import tweepy
import os
import time
import json
import random
import requests
import google.generativeai as genai

# --- ŞİFRELER (GitHub Secrets'tan Çekilir) ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- 6 MOTORLU YEDEK DEPO SİSTEMİ (HUGGING FACE) ---
# GitHub Secrets kısmında bu isimlerle anahtar olması lazım
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),    # Ana Token
    os.environ.get('HF_TOKEN_1'),  # Yedek 1
    os.environ.get('HF_TOKEN_2'),  # Yedek 2
    os.environ.get('HF_TOKEN_3'),  # Yedek 3
    os.environ.get('HF_TOKEN_4'),  # Yedek 4
    os.environ.get('HF_TOKEN_5'),  # Yedek 5
    os.environ.get('HF_TOKEN_6')   # Yedek 6
]
# Boş olanları listeden temizle
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# EN GÜNCEL VE HIZLI MODEL: Gemini 1.5 Flash
model = genai.GenerativeModel('gemini-1.5-flash')

# EN KALİTELİ ÇİZİM MODELİ: SDXL 1.0
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def get_autonomous_idea():
    print("🧠 Gemini, senin zevkine göre yeni ve eşsiz bir fikir kurguluyor...")
    
    # SENİN ZEVK HARİTAN
    prompt_emir = """
    Sen benim kişisel dijital sanat asistanımsın. Twitter hesabım için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    BENİM SEVDİĞİM TARZLAR (Bunları karıştır, birleştir, yeniden yorumla):
    1. Minimalist Doğa (Sakin, sisli, huzurlu, tek ağaç, göl yansıması vb.)
    2. Estetik Geometri (Bauhaus tarzı, düz çizgiler, pastel tonlar, simetri)
    3. Temiz Bilim Kurgu (Neon ışıklar, sade uzay boşluğu, astronot, retro-fütürizm)
    4. Sürrealist Rüyalar (Bulutların üstünde kapılar, uçan adalar, mantık dışı ama estetik)
    5. Soft Renkler ve Işık (Gün batımı, 'Golden hour', loş ışık, huzur verici atmosfer)

    GÖREVİN:
    Yukarıdaki tarzları temel alarak, daha önce hiç yapılmamış, benzersiz ve çok havalı bir görsel fikir bul.
    Sürekli aynı şeyi yapma. Bir seferinde dağ çiziyorsan, diğerinde neon bir şehir, ötekinde soyut bir şekil çiz.

    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, çok kısa (max 1 cümle), havalı ve emojili bir açıklama. Hashtagler ekle (#Minimalist #Art #4K vb.).",
      "image_prompt": "Resmi çizecek yapay zeka için İNGİLİZCE prompt. Şunları MUTLAKA ekle: 'minimalist, clean lines, vertical wallpaper, 8k resolution, masterpiece, high quality, cinematic lighting, photorealistic, sharp focus, --no text'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Fikir Bulundu: {data['caption']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu kullanılıyor.")
        return {
            "caption": "Serenity in Blue 🌊 \n\n#Minimalist #Wallpaper #Art",
            "image_prompt": "A single sailboat on a calm blue ocean, minimalist style, vertical, 8k, photorealistic"
        }

def query_huggingface(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def generate_image_raw(prompt):
    # Tüm anahtarları sırayla dener
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Anahtar deneniyor...")
        
        # Dikey format için parametreler (SDXL bunları destekler)
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "text, watermark, blurry, low quality, distorted, ugly, hands, fingers",
                # SDXL boyutu (Dikey'e yakın)
                "width": 768, 
                "height": 1344 
            }
        }
        
        try:
            response = query_huggingface(payload, token)
            
            # EĞER MODEL UYUYORSA (503 HATASI) - BEKLEME MANTIĞI
            if response.status_code == 503:
                estimated_time = response.json().get("estimated_time", 20)
                print(f"💤 Model uyuyor! {estimated_time} saniye bekleniyor...")
                time.sleep(estimated_time)
                # Tekrar dene
                response = query_huggingface(payload, token)
            
            if response.status_code == 200:
                with open("tweet_image.jpg", "wb") as f:
                    f.write(response.content)
                print(f"✅ Resim Başarıyla Çizildi! ({i+1}. Anahtar)")
                return True
            else:
                print(f"❌ Hata Kodu: {response.status_code} - Mesaj: {response.text}")
                
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")
            
    print("🚨 HATA: Hiçbir anahtar resmi çizemedi.")
    return False

def post_tweet():
    content = get_autonomous_idea()
    
    if generate_image_raw(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="tweet_image.jpg")
            
            # Paylaş
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER BAŞARILI! (Yüksek Kalite Modu)")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()