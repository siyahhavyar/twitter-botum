import os
import requests
import random
import time
import google.generativeai as genai
import tweepy

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

def get_creative_content():
    print("🧠 Gemini: Hem resim hem de tweet metni düşünülüyor...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # --- ZAR ATMA MEKANİZMASI (Tekrarı Önler) ---
        themes = [
            "Cyberpunk City with Neon Rain", "Minimalist Pastel Clouds", 
            "Macro Photography of Water Droplets", "Abstract Fluid Colors", 
            "Retro 80s Synthwave Sunset", "Majestic Fantasy Castle", 
            "Deep Space Nebula", "Isometric Tiny Room 3D", 
            "Paper Cutout Art Style", "Bioluminescent Forest",
            "Zen Japanese Garden", "Futuristic Glass Architecture",
            "Cute Geometric Animal Vector", "Vibrant Oil Painting Style",
            "Black and White Noir Detective Scene", "Underwater Coral Reef",
            "Pixel Art Landscape", "Dreamy Surrealism Salvador Dali Style"
        ]
        selected_theme = random.choice(themes)
        
        # --- GEMINI EMİRLERİ ---
        instruction = f"""
        You are a creative Social Media Manager and Art Director.
        
        TASK:
        1. Create a unique, highly detailed image prompt based on this theme: "{selected_theme}".
        2. Write a short, engaging, cute tweet caption (in Turkish) for this image.
        3. Add 3-4 relevant hashtags.
        
        FORMAT:
        PROMPT: [English Image Prompt] ||| CAPTION: [Turkish Tweet Text]
        
        RULES:
        - Image Prompt must imply "8k, vertical wallpaper, sharp focus, masterpiece".
        - Do NOT simply describe the image; add artistic style keywords.
        - Caption should be fun, inviting, or poetic. NOT robotic.
        """
        
        response = model.generate_content(instruction)
        raw_text = response.text.strip()
        
        # Cevabı "|||" işaretinden ikiye bölüyoruz (Resim Emri ve Tweet Metni)
        parts = raw_text.split("|||")
        
        if len(parts) == 2:
            image_prompt = parts[0].replace("PROMPT:", "").strip()
            tweet_text = parts[1].replace("CAPTION:", "").strip()
            
            # Kalite Garantisi İçin Eklemeler
            final_prompt = image_prompt + ", vertical wallpaper, 8k resolution, ultra detailed, high contrast, vivid colors, sharp focus, no blur"
            
            print(f"🎨 Konu: {image_prompt[:50]}...")
            print(f"📝 Tweet: {tweet_text}")
            return final_prompt, tweet_text
        else:
            raise Exception("Format hatası")
            
    except Exception as e:
        print(f"⚠️ Gemini Hatası: {e}")
        # Yedek Plan
        return "minimalist aesthetic sunset over ocean, vector art, 8k", "Günün huzuru burada... 🌊✨ #wallpaper #huzur"

def try_huggingface(prompt):
    print("🎨 Hugging Face (SDXL - Kaliteli Mod) deneniyor...")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # TELEFON İÇİN DİKEY FORMAT (768x1344)
        # SDXL bu oranda en keskin sonucu verir. 4K hissi yaratır.
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768, 
                "height": 1344,
                "num_inference_steps": 40, # Detay seviyesini artırır
                "guidance_scale": 7.5      # Prompta sadık kalır
            }
        }
        
        try:
            print(f"➡️ Token {idx+1} deneniyor...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 200:
                print("✅ Hugging Face BAŞARILI!")
                return response.content
            elif "loading" in response.text:
                print("⏳ Model ısınıyor...")
                time.sleep(5)
            else:
                print(f"❌ Hata Kodu: {response.status_code}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            
    print("🚨 Hugging Face yanıt vermedi. Yedeğe geçiliyor.")
    return None

def try_pollinations_backup(prompt):
    print("🛡️ YEDEK SİSTEM (Pollinations - HD Dikey) Devrede...")
    try:
        encoded = requests.utils.quote(prompt)
        # 1080x1920 TAM HD FORMAT
        url = f"https://pollinations.ai/p/{encoded}?width=1080&height=1920&seed={random.randint(1,1000)}&model=flux&nologo=true&enhance=true"
        
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            print("✅ Yedek sistem HD resmi çizdi!")
            return response.content
    except Exception as e:
        print(f"Yedek sistem hatası: {e}")
    return None

def save_and_post(image_bytes, tweet_text):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(image_bytes)
        
    if os.path.getsize(filename) < 1000:
        print("❌ Dosya bozuk.")
        return

    print("🐦 Twitter'a yükleniyor...")
    try:
        # Medya Yükleme
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(filename)
        
        # Tweet Atma (Gemini'nin yazdığı metinle)
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        print("✅ TWEET VE RESİM PAYLAŞILDI!")
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    # 1. Gemini'den hem resim fikrini hem tweet metnini al
    prompt_text, tweet_content = get_creative_content()
    
    # 2. Resmi üret (Hugging Face veya Pollinations)
    img_data = try_huggingface(prompt_text)
    if not img_data:
        img_data = try_pollinations_backup(prompt_text)
        
    # 3. Paylaş
    if img_data:
        save_and_post(img_data, tweet_content)
    else:
        print("❌ Resim üretilemediği için paylaşım yapılmadı.")
