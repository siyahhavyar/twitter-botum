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

# --- 6 MOTORLU GÜÇ SİSTEMİ (HUGGING FACE) ---
# Bu sistem sayesinde bot asla "kota doldu" diye durmaz.
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),
    os.environ.get('HF_TOKEN_1'),
    os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'),
    os.environ.get('HF_TOKEN_4'),
    os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6')
]
# Boş olanları listeden temizle
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Beyin: Gemini 1.5 Flash (Hatasız, hızlı)
model = genai.GenerativeModel('gemini-1.5-flash')
# Ressam: SDXL 1.0 (En yüksek kalite)
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_artistic_vision():
    print("🧠 Sanat Yönetmeni (Gemini) vizyonunu oluşturuyor...")
    
    # --- TAM OTONOM SANATÇI EMRİ ---
    # Liste yok. Sınırlama yok. Sadece "Estetik ve Güzel" olma kuralı var.
    
    prompt_emir = """
    Sen dünyaca ünlü, vizyoner bir dijital sanatçısın (Art Director).
    Görevin: Twitter (X) kitlesi için insanların telefonlarına "Duvar Kağıdı" yapmak isteyeceği, estetik açıdan kusursuz, büyüleyici bir eser tasarlamak.
    
    KESİN KURALLARIN:
    1. ASLA korku, kan, şiddet, cinsellik, +18, rahatsız edici veya tiksindirici öğeler kullanma.
    2. Sıradan, sıkıcı veya çok basit (sadece bir daire gibi) şeyler yapma.
    3. İnsanların görünce "Vay be, bunu kaydetmeliyim" diyeceği, renk uyumu mükemmel, kompozisyonu harika şeyler düşün.
    
    Konu seçiminde TAMAMEN ÖZGÜRSÜN. O anki ilhamına göre fütüristik bir şehir, mistik bir orman, soyut bir rüya alemi veya antik bir yapı tasarlayabilirsin. Tek kriter: GÖZ ALICI ve KALİTELİ olması.
    
    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, çok kısa, havalı, emojili bir sanatçı notu (Eserin adı gibi).",
      "image_prompt": "Resmi çizecek yapay zeka için İNGİLİZCE, çok detaylı, 8k çözünürlükte, sinematik ışıklandırmalı, dikey formatta (vertical wallpaper), fotoğraf gerçekliğinde (photorealistic) ve 'masterpiece' kalitesinde prompt. Asla 'text' veya 'watermark' olmasın."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Vizyon Belirlendi: {data['caption']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini İlham Gelmedi ({e}), yedek devreye giriyor.")
        # Çok nadir bir hata olursa yedek olarak bunu çizer.
        return {
            "caption": "Dreamscape 🌌 \n\n#Art #Wallpaper #AI",
            "image_prompt": "A majestic floating island in the sky with waterfalls, dreamy atmosphere, cinematic lighting, 8k, vertical, photorealistic, masterpiece"
        }

def generate_image_sdxl(prompt):
    # Elimizdeki 6 motoru (anahtarı) sırayla dener. Biri çalışmazsa diğerine geçer.
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Ressam Motoru (Anahtar) deneniyor...")
        try:
            client = InferenceClient(model=repo_id, token=token)
            
            # SDXL ile Dikey ve Yüksek Kalite Çizim (Bu oran telefon için en iyisidir)
            image = client.text_to_image(
                f"{prompt}", 
                width=768, height=1344
            )
            image.save("art_piece.jpg")
            print(f"✅ Eser Başarıyla Çizildi ({i+1}. Motor).")
            return True
        except Exception as e:
            # Eğer 418 veya 429 hatası (kota doldu) gelirse burası çalışır.
            print(f"⚠️ {i+1}. Motor Hatası (Diğerine geçiliyor): {e}")
            time.sleep(1) # 1 saniye bekle ve diğer anahtarı dene
            
    print("🚨 HATA: Tüm motorlar denendi ama hiçbiri çalışmadı (İnanılmaz!).")
    return False

def post_tweet():
    # 1. Beyin (Gemini) konuyu bulur
    content = get_artistic_vision()
    
    # 2. El (Hugging Face SDXL) resmi çizer
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