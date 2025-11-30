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

# --- ÇÖZÜNÜRLÜK ---
# 1080x1920 en temiz orandır.
IMG_WIDTH = 1080
IMG_HEIGHT = 1920

def get_image_prompt():
    print("Gemini: Keskin çizgi stili için prompt hazırlanıyor...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # BURASI ÇOK KRİTİK. Yapay zekaya "Bulanık yapma şansı" bırakmıyoruz.
    prompt_instruction = """
    Create a wallpaper prompt for a smartphone.
    MANDATORY STYLE: "Vector Art", "Flat Design", "Cel Shaded" or "Anime Background Style".
    
    FORBIDDEN: Do not use "3d render", "photorealistic", "fluffy", "fur", "soft lighting". These cause blur.
    
    SUBJECTS:
    1. Cute minimalist animals (drawn as vector icons, not 3d).
    2. Japanese landscape (Makoto Shinkai style).
    3. Cyberpunk city with neon lines.
    4. Abstract geometric shapes with hard edges.
    
    OUTPUT: ONLY the English prompt.
    """
    
    try:
        response = model.generate_content(prompt_instruction)
        base_prompt = response.text.strip()
        
        # --- NETLİK İĞNESİ ---
        # Bu kelimeler resmi keskinleştirir
        sharpness_boosters = ", vector art, hard outlines, flat colors, clean lines, svg style, high contrast, 8k resolution, retina display, sharp edges, no blur, masterpiece"
        
        final_prompt = base_prompt + sharpness_boosters
        print(f"Fikir: {base_prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return "minimalist black cat looking at moon, vector art, flat design, clean lines, sharp edges, 8k"

def download_image(prompt):
    print("Pollinations: Vektör tabanlı çizim yapılıyor...")
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 999999)
    
    # model=flux-realism yerine 'flux' kullanıyoruz ama stili prompt ile zorluyoruz.
    # enhance=false yapıyoruz çünkü enhance bazen resmi yapaylaştırıp bozuyor.
    url = f"https://pollinations.ai/p/{encoded_prompt}?width={IMG_WIDTH}&height={IMG_HEIGHT}&seed={seed}&model=flux&nologo=true&enhance=false"
    
    try:
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Resim İndi! Boyut: {IMG_WIDTH}x{IMG_HEIGHT}")
            return filename
        else:
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a yükleniyor...")
    try:
        # V1.1 Yetkilendirme
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        media_id = media.media_id
        
        # V2 Client
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "Daily Wallpaper ✨\n\n#wallpaper #vectorart #minimalist #art #4k"
        
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI: Paylaşıldı!")
        
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
    else:
        print("Hata oluştu.")
