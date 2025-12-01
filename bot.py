import os
import requests
import random
import time
import google.generativeai as genai
import tweepy
from io import BytesIO

# --- ŞİFRELER ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
CONSUMER_KEY = os.environ.get("API_KEY")
CONSUMER_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

# Token Listesi
hf_tokens = [
    os.environ.get("HF_TOKEN_1"), os.environ.get("HF_TOKEN_2"),
    os.environ.get("HF_TOKEN_3"), os.environ.get("HF_TOKEN_4"),
    os.environ.get("HF_TOKEN_5"), os.environ.get("HF_TOKEN_6")
]
valid_tokens = [t for t in hf_tokens if t]

def get_image_prompt():
    print("🧠 Gemini: Konu düşünülüyor...")
    try:
        # Analize uygun olarak 1.5 modelini kullanıyoruz
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Keskinlik için özel prompt yapısı
        instruction = """
        Create a prompt for AI Image Generator.
        Style: Vector Art, Flat Design, or Hard-Surface 3D.
        Rules: NO "Photo", NO "Realistic", NO "Blur".
        Subject: Cyberpunk city, Minimalist nature, Space, Geometric shapes.
        Output: ONLY the prompt text.
        """
        response = model.generate_content(instruction)
        prompt = response.text.strip()
        final_prompt = prompt + ", vector art, sharp lines, flat color, 8k resolution, high contrast, masterpiece, no blur"
        print(f"💡 Fikir: {prompt}")
        return final_prompt
    except Exception as e:
        print(f"⚠️ Gemini Hatası: {e}")
        return "cyberpunk city neon lights, vector art, sharp lines, flat design, 8k"

def try_huggingface(prompt):
    print("🎨 Hugging Face (SDXL) deneniyor...")
    
    # Analizde önerilen en stabil SDXL Modeli
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": prompt}
        
        try:
            print(f"➡️ Token {idx+1} deneniyor...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                print("✅ Hugging Face BAŞARILI!")
                return response.content
            elif "loading" in response.text:
                print("⏳ Model ısınıyor, bekleniyor...")
                time.sleep(5)
            else:
                print(f"❌ Hata Kodu: {response.status_code}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            
    print("🚨 Hugging Face API yanıt vermedi. Yedeğe geçiliyor.")
    return None

def try_pollinations_backup(prompt):
    print("🛡️ YEDEK SİSTEM (Pollinations - Keskin Mod) Devrede...")
    # Burada resmi bulanıklaştırmayan özel ayarlar (enhance=false, model=flux) kullanıyoruz
    try:
        encoded = requests.utils.quote(prompt)
        # 1080x1920 dikey format
        url = f"https://pollinations.ai/p/{encoded}?width=1080&height=1920&seed={random.randint(1,1000)}&model=flux&nologo=true&enhance=false"
        
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            print("✅ Yedek sistem resmi çizdi!")
            return response.content
    except Exception as e:
        print(f"Yedek sistem hatası: {e}")
    return None

def save_and_post(image_bytes, prompt):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(image_bytes)
        
    if os.path.getsize(filename) < 1000:
        print("❌ Dosya bozuk.")
        return

    print("🐦 Twitter'a yükleniyor...")
    try:
        # V1.1 Yetkilendirme (Media Upload)
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(filename)
        
        # V2 Yetkilendirme (Tweet Post)
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "Daily Wallpaper 🎨✨\n#wallpaper #art #ai #design"
        client.create_tweet(text=text, media_ids=[media.media_id])
        print("✅ TWEET ATILDI!")
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    
    # 1. Hugging Face'i dene
    img_data = try_huggingface(prompt_text)
    
    # 2. Çalışmazsa Pollinations'ı dene
    if not img_data:
        img_data = try_pollinations_backup(prompt_text)
        
    # 3. Paylaş
    if img_data:
        save_and_post(img_data, prompt_text)
    else:
        print("❌ Tüm sistemler başarısız oldu.")
