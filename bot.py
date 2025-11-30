import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# --- ŞİFRELER (GitHub Secrets'tan Çeker) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Twitter Şifreleri
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# Kalite Ayarı (QHD - 1440x2560)
IMG_WIDTH = 1440
IMG_HEIGHT = 2560

def get_image_prompt():
    print("Gemini API ile fikir düşünülüyor...")
    # Model ismini düzelttik: 'gemini-1.5-flash' (Hızlı ve Bedava)
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt_instruction = """
    Create a detailed image generation prompt for a smartphone wallpaper.
    Style: Minimalist, Aesthetic, High Quality.
    Subject: Can be nature, abstract, cute animals, or geometry.
    Constraint: NO TEXT, NO WORDS.
    Output: Just the prompt string in English.
    """
    
    try:
        response = model.generate_content(prompt_instruction)
        text = response.text.strip()
        # Kalite komutlarını ekleyelim
        final_prompt = text + ", 8k resolution, ultra detailed, unreal engine 5, sharp focus, aesthetic, vivid colors"
        print(f"Fikir: {text}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return "minimalist aesthetic sunset over mountains, 8k resolution, vector art style"

def download_image(prompt):
    print("Pollinations ile resim çiziliyor...")
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 999999)
    
    url = f"https://pollinations.ai/p/{encoded_prompt}?width={IMG_WIDTH}&height={IMG_HEIGHT}&seed={seed}&model=flux&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=90) # Süreyi uzattık
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print("Resim başarıyla indi.")
            return filename
        else:
            print("Resim sunucusu hata verdi.")
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a bağlanılıyor...")
    
    try:
        # 1. Aşama: V1.1 API ile Giriş Yap (Resim yüklemek için şart)
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        # 2. Aşama: Resmi Yükle
        print("Resim yükleniyor...")
        media = api.media_upload(filename)
        media_id = media.media_id
        
        # 3. Aşama: V2 Client ile Tweet At (Daha güvenilir)
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "New 4K Wallpaper! 🎨✨\n#wallpaper #art #ai #aesthetic"
        
        # Tweeti gönder (Resim ID'sini ekleyerek)
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI: Tweet atıldı!")
        
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        print("Lütfen Twitter Developer panelinden 'App Permissions' kısmının 'Read and Write' olduğundan emin ol ve KEY'leri yeniden oluştur.")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
    else:
        print("Resim olmadığı için paylaşılmadı.")
