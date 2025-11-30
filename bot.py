import os
import requests
import time
import random
import google.generativeai as genai
import tweepy

# --- ŞİFRELER ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
CONSUMER_KEY = os.environ.get("API_KEY")
CONSUMER_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

def get_image_prompt():
    print("Gemini: Konu düşünülüyor...")
    
    # Python sürümünü yükselttik, artık bu model kesin çalışacak
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    instruction = """
    You are an AI Wallpaper Prompt Generator.
    Goal: Create a prompt for a minimalist, vector-style wallpaper.
    CRITICAL RULES:
    1. NO "Photo", "Realistic", "3D Render" keywords (These cause blur).
    2. USE: "Vector Art", "Flat Design", "Clean Lines", "Anime Background".
    3. Subject: Cyberpunk city, Japanese landscape, Space, or Geometric Animals.
    Output: ONLY the prompt text.
    """
    
    try:
        response = model.generate_content(instruction)
        prompt = response.text.strip()
        # Resmi keskinleştiren sihirli eklentiler
        final_prompt = prompt + ", vector art, sharp outlines, flat color, high contrast, 8k, svg style, no blur, hd"
        print(f"Fikir: {prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        # Eğer Gemini yine de hata verirse bu yedek devreye girer
        return "minimalist japanese sunset with mountains, vector art, flat design, sharp lines, high contrast, 8k"

def download_image(prompt):
    print("Pollinations (Flux): Resim çiziliyor...")
    
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 999999)
    
    # 1. YÖNTEM: Flux Modeli (En iyisi)
    # nologo=true : Logo yok
    # enhance=false : Yapaylık yok, doğal netlik
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920&seed={seed}&model=flux&nologo=true&enhance=false"
    
    try:
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Boyut kontrolü
            if os.path.getsize(filename) < 1000:
                print("Hata: Dosya çok küçük.")
                return None
                
            print("Mükemmel! Resim indi.")
            return filename
        else:
            print(f"Sunucu hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a yükleniyor...")
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        media_id = media.media_id
        
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "Daily Wallpaper 🎨\n#wallpaper #vector #art"
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI!")
        
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
