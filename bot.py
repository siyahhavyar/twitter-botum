import tweepy
import os
import time
import json
import random
import google.generativeai as genai
from huggingface_hub import InferenceClient

# --- ŞİFRELER (GitHub Kasasından) ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- YEDEK DEPOLU TOKEN SİSTEMİ ---
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

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# En iyi sonuç veren model
model = genai.GenerativeModel('gemini-1.5-flash')
# Kalitenin kralı SDXL
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_artistic_vision():
    print("🧠 Sanatçı (Gemini) ilham arıyor...")
    
    # --- İŞTE BURASI ÇOK ÖNEMLİ ---
    # Ona kısıtlı bir liste vermiyoruz. Ona "Sen Sanatçısın" diyoruz.
    
    prompt_emir = """
    Sen dünyaca ünlü, vizyoner bir dijital sanatçısın ve küratörsün.
    Görevin: Twitter (X) kitlesi için insanların telefonlarına "Duvar Kağıdı" yapmak isteyeceği, estetik açıdan kusursuz bir eser tasarlamak.
    
    KURALLARIN:
    1. ASLA korku, kan, şiddet, cinsellik, rahatsız edici veya tiksindirici öğeler kullanma.
    2. Sıradan, sıkıcı veya çok basit şeyler yapma.
    3. İnsanların "Vay be, bu ne kadar güzel" diyeceği, renk uyumu mükemmel, kompozisyonu harika şeyler düşün.
    4. Konu seçiminde ÖZGÜRSÜN. İster fütüristik bir şehir, ister huzurlu bir doğa, ister soyut bir rüya, ister antik bir tapınak... O an içinden ne geliyorsa. Tek kriter: ESTETİK ve GÜZEL olması.
    
    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı, emojili bir sanatçı notu. (Eserin adı gibi)",
      "image_prompt": "Resmi çizecek yapay zeka için İNGİLİZCE, çok detaylı, 8k çözünürlükte, sinematik ışıklandırmalı, dikey formatta (vertical wallpaper), fotoğraf gerçekliğinde (photorealistic) ve 'masterpiece' kalitesinde prompt. Asla 'text' olmasın."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Sanatçı Kararını Verdi: {data['caption']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini İlham Gelmedi ({e}), yedek devreye giriyor.")
        return {
            "caption": "Dreamscape 🌌 \n\n#Art #Wallpaper #AI",
            "image_prompt": "A majestic floating island in the sky with waterfalls, dreamy atmosphere, cinematic lighting, 8k, vertical, photorealistic, masterpiece"
        }

def generate_image_sdxl(prompt):
    # Yedek anahtarları sırayla dener
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Fırça (Anahtar) deneniyor...")
        try:
            client = InferenceClient(model=repo_id, token=token)
            
            # SDXL ile Dikey ve Yüksek Kalite
            image = client.text_to_image(
                f"{prompt}, vertical wallpaper, aspect ratio 2:3, 8k resolution, highly detailed", 
                width=768, height=1344
            )
            image.save("art_piece.jpg")
            print(f"✅ Eser Çizildi ({i+1}. Anahtar).")
            return True
        except Exception as e:
            print(f"❌ {i+1}. Anahtar Hatası: {e}")
            time.sleep(1)
            
    print("🚨 HATA: Hiçbir anahtar çizemedi.")
    return False

def post_tweet():
    content = get_artistic_vision()
    
    if generate_image_sdxl(content['image_prompt']):
        print("🐦 Galeriye (Twitter) yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="art_piece.jpg")
            
            # Paylaş
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ SANAT ESERİ PAYLAŞILDI!")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()