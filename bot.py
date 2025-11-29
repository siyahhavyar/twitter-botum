import tweepy
import os
import time
import json
import random
import requests
import google.generativeai as genai
from huggingface_hub import InferenceClient # Yeni eklenen kütüphane

# --- API ANAHTARLARI (GitHub Secrets'tan) ---
consumer_key = os.environ['API_KEY']
consumer_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- RESİM OLUŞTURMA AYARLARI ---
# Hugging Face için varsayılan SDXL modeli ve kütüphane bağlantısı
repo_id = "stabilityai/stable-diffusion-xl-base-1.0" 

# --- YEDEK DEPOLU TOKEN SİSTEMİ (Resim çizmek için) ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'), os.environ.get('HF_TOKEN_1'), os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'), os.environ.get('HF_TOKEN_4'), os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 🧱 ÇEKİRDEK KONSEPTLER (Gemini'nin evirip çevireceği ana malzemeler) ---
WALLPAPER_THEMES = [
    "Minimalist",
    "Abstract Geometry",
    "Surrealism",
    "Cyberpunk",
    "Retro Synthwave",
    "Brutalist Architecture",
    "Glassmorphism",
    "Liquid Metal",
    "Dark Academia",
    "Monochrome Noir",
    "Cozy Lo-Fi",
    "Optical Illusion",
    "Glitchcore / Error Aesthetic",
    "Japanese Zen"
]

def get_wallpaper_idea():
    # 1. Geniş bir tema seç (Çekirdek Malzeme)
    broad_theme = random.choice(WALLPAPER_THEMES)
    print(f"🎨 Ana Tema Seçildi: {broad_theme}")

    print("🧠 Gemini konsepti evirip çevirip yeni bir fikir üretiyor...")

    # 2. Gemini'ye Mutasyon Emri Veriyoruz
    prompt_emir = f"""
    Sen bir Yapay Zeka Sanat Konsept Uzmanısın.
    Görevin: '{broad_theme}' ana temasını alıp, onu bambaşka, spesifik ve viral olacak bir alt-konsepte dönüştürmek.

    Örnekler:
    - Ana Tema: Minimalist -> Alt-Konsept: 'Minimalist bir çölde, gökyüzünde parlak mor bir küre'.
    - Ana Tema: Liquid Metal -> Alt-Konsept: 'Akan sıvı metalden yapılmış, 17. yüzyıl Avrupa kütüphanesi'.
    - Ana Tema: Dark Academia -> Alt-Konsept: 'Sadece yanan bir mumla aydınlatılmış gotik pencereden sızan su damlaları'.

    Yeni, benzersiz alt-konsepti yarattıktan sonra, bu alt-konsepte uygun çıktıyı üret.
    
    Çıktı Formatı SADECE şu JSON yapısında olmalıdır:
    {{
      "sub_theme": "Gemini'nin yarattığı yeni ve spesifik alt-konsept (Türkçe/Kısa)",
      "caption": "Twitter için İngilizce, havalı ve emojili bir başlık ve hashtag'ler (#Wallpaper #Art #4K vb.).",
      "image_prompt": "Yeni alt-konsept için İNGİLİZCE prompt. Şunları mutlaka içersin: 'minimalist, clean lines, vertical wallpaper, 8k resolution, masterpiece, high quality, cinematic lighting, --no text, signature'."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"✨ Yeni Konsept: {data['sub_theme']}")
        print(f"✅ Metin hazır: {data['caption'][:30]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası, yedek kullanılıyor: {e}")
        return {
            "sub_theme": "Yedek Tema: Neo-Minimalizm",
            "caption": "Minimalist Geometry. 📐\n\n#Abstract #Wallpaper #AI",
            "image_prompt": "Clean, vertical geometric pattern in neon pink and cyan, minimalist, 8k, photorealistic"
        }

def generate_high_quality_image(prompt):
    # Sırayla tüm yedek anahtarları dener
    for i, token in enumerate(TOKEN_LISTESI):
        if not token: continue
        print(f"🔄 {i+1}. Ressam Anahtarı deneniyor...")
        try:
            # Hugging Face token kullanılarak SDXL modeli çağrılır
            client = InferenceClient(model=repo_id, token=token)
            
            # SDXL Modeli ile çizim
            image = client.text_to_image(
                prompt=f"{prompt}", 
                width=768, height=1344 # Telefon ekranına uygun dikey çözünürlük
            )
            image.save("wallpaper.jpg")
            print(f"✅ Resim Çizildi ({i+1}. Anahtar çalıştı).")
            return True
        except Exception as e:
            print(f"❌ {i+1}. Anahtar Hatası (Kota dolmuş olabilir): {e}")
            print("Diğer anahtara geçiliyor...")
            time.sleep(2) 
            
    print("🚨 HATA: Hiçbir anahtar resmi çizemedi.")
    return False

def post_tweet():
    content = get_wallpaper_idea()
    
    if generate_high_quality_image(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)

            media = api.media_upload(filename="wallpaper.jpg")
            
            # Paylaş
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER'DA PAYLAŞILDI!")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("⚠️ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()