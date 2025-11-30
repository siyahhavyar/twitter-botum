import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

# --- ŞİFRELER ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

# --- KALİTE AYARI (KRİTİK GÜNCELLEME) ---
# Yapay zekanın "çamurlaşmadan" en keskin detay verdiği boyut budur.
# 1080x1920 telefonda 1440p'den daha net görünür çünkü piksel hatası olmaz.
IMG_WIDTH = 1080
IMG_HEIGHT = 1920

def get_image_prompt():
    print("Gemini API ile ultra net fikir düşünülüyor...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # İPUCU: Yapay zekaya "Fotoğraf" değil "3D Render" veya "Vektör" çizdirirsek daha net olur.
    prompt_instruction = """
    Create a prompt for a smartphone wallpaper.
    Style: 3D Render, Vector Art, or Digital Illustration (Avoid realistic photos to prevent blur).
    Subject: Minimalist nature, abstract geometry, cute characters, or fluid shapes.
    Constraint: NO TEXT.
    Output: ONLY the English prompt.
    """
    
    try:
        response = model.generate_content(prompt_instruction)
        base_prompt = response.text.strip()
        
        # --- KESKİNLİK FORMÜLÜ ---
        # Bu kelimeler resmi "Jilet" gibi yapar:
        quality_boosters = ", 8k resolution, sharp focus, crystal clear, vector lines, highly detailed, unreal engine 5 render, octane render, no blur, high contrast"
        
        final_prompt = base_prompt + quality_boosters
        print(f"Fikir: {base_prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return "cute cat on a cloud, 3d render, 8k, sharp focus, minimalist"

def download_image(prompt):
    print("Pollinations ile resim çiziliyor...")
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 999999)
    
    # NOT: 'enhance=true' bazen görüntüyü bozar, 'nologo=true' temiz yapar.
    # Model 'flux' detay için en iyisidir.
    url = f"https://pollinations.ai/p/{encoded_prompt}?width={IMG_WIDTH}&height={IMG_HEIGHT}&seed={seed}&model=flux&nologo=true"
    
    try:
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Resim İndi! Boyut: {IMG_WIDTH}x{IMG_HEIGHT}")
            return filename
        else:
            print("Sunucu hatası.")
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a gönderiliyor...")
    try:
        # V1.1 API ile Medya Yükleme
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        media_id = media.media_id
        
        # V2 API ile Tweet Atma
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        # Hashtagler etkileşim için önemli
        text = "New Wallpaper! 🎨✨\n\n#wallpaper #art #aesthetic #4k #background"
        
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI: Tweet HD olarak paylaşıldı!")
        
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
    else:
        print("Hata oluştu.")
