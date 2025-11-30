import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# --- AYARLAR ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# --- KALİTE AYARLARI ---
# Telefonlar için en net görüntü oranı (9:16)
# Standart HD: 1080x1920
# Bizim Hedefimiz (Ultra Kalite): 1440x2560 (QHD)
IMG_WIDTH = 1440
IMG_HEIGHT = 2560

# 1. BÖLÜM: BEYİN (GEMINI) - FİKİR ÜRETME
def get_image_prompt():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    # Sisteme verdiğimiz "Sanat Yönetmeni" emri
    system_instruction = """
    You are an expert wallpaper curator for high-end smartphones.
    Task: Create a text-to-image prompt for a wallpaper.
    Style: Minimalist, Cute, Aesthetic, 3D Render or Vector Art.
    
    CRITICAL RULES:
    1. NO TEXT, NO LETTERS, NO WORDS in the image.
    2. High contrast, vivid pastel colors.
    3. Center the main subject so it is not covered by phone clock/icons.
    4. Provide ONLY the English prompt.
    5. Subject ideas: Cute animals, abstract fluid shapes, cozy rooms, nature close-ups.
    """
    
    try:
        response = model.generate_content(system_instruction)
        base_prompt = response.text.strip()
        
        # --- KALİTE SİHRİ BURADA ---
        # Gemini ne verirse versin, sonuna bu kalite kodlarını ekliyoruz.
        quality_boosters = ", 8k resolution, ultra detailed, sharp focus, octane render, ray tracing, high fidelity, masterpiece, vivid colors, no blur, crystal clear"
        
        final_prompt = base_prompt + quality_boosters
        print(f"Oluşturulacak Sahne: {base_prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        # Hata olursa yedek bir prompt kullanalım
        return "cute fluffy cat sitting on a cloud, minimalist style, pastel colors, 8k resolution, sharp focus, masterpiece"

# 2. BÖLÜM: RESSAM (POLLINATIONS/FLUX) - YÜKSEK ÇÖZÜNÜRLÜK
def download_image(prompt):
    print("Yüksek kaliteli render işlemi başlıyor... (Bu işlem biraz sürebilir)")
    
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 999999) # Her seferinde eşsiz olması için
    
    # Model: 'flux' (Şu an ücretsizler arasında en keskin ve akıllı olanı)
    # Enhance: true (Renkleri ve detayları patlatır)
    image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={IMG_WIDTH}&height={IMG_HEIGHT}&seed={seed}&model=flux&enhance=true&nologo=true"
    
    try:
        # Büyük dosya olduğu için stream=True kullanıyoruz
        response = requests.get(image_url, stream=True)
        
        if response.status_code == 200:
            filename = "wallpaper_hq.jpg"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(filename) / 1024 / 1024 # MB cinsinden
            print(f"Resim indirildi! Boyut: {file_size:.2f} MB. Kalite: {IMG_WIDTH}x{IMG_HEIGHT}")
            return filename
        else:
            print(f"Resim indirilemedi. Sunucu kodu: {response.status_code}")
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

# 3. BÖLÜM: TWITTER - PAYLAŞIM
def post_to_twitter(filename, prompt):
    if not CONSUMER_KEY:
        print("Twitter API anahtarları yok. Sadece resim oluşturuldu.")
        return

    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        print("Twitter'a yükleniyor...")
        media = api.media_upload(filename)
        
        # Prompt'un ilk cümlesini veya güzel bir başlık seçelim
        tweet_text = f"✨ Daily Wallpaper Request ✨\n\n⬇️ HD/4K Download\n#wallpaper #background #art #aesthetic #4k"
        
        api.update_status(status=tweet_text, media_ids=[media.media_id])
        print("✅ Başarıyla paylaşıldı!")
    except Exception as e:
        print(f"Twitter Paylaşım Hatası: {e}")

# --- ANA ÇALIŞTIRMA ---
if __name__ == "__main__":
    prompt = get_image_prompt()
    image_path = download_image(prompt)
    
    if image_path:
        post_to_twitter(image_path, prompt)
    else:
        print("İşlem başarısız oldu.")
