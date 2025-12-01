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
    print("🧠 Gemini (Pro): Thinking...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        themes = [
            "Cyberpunk City Neon Rain", "Minimalist Zen Garden", "Deep Space Nebula", 
            "Futuristic Architecture", "Bioluminescent Forest", "Sunset Snowy Mountains",
            "Abstract Liquid Gold", "Geometric 3D Shapes", "Synthwave Retro Road", 
            "Macro Water Droplet", "Underwater Coral Reef", "Vibrant Oil Painting",
            "Stormy Ocean Waves", "Mechanical Watch Gears"
        ]
        theme = random.choice(themes)
        
        instruction = f"""
        Role: Art Director. Theme: "{theme}".
        TASK:
        1. Write a prompt for 'Stable Diffusion XL'.
        2. Write a short English Tweet caption.
        3. Hashtags.
        
        RULES:
        - Keywords: "8k resolution, photorealistic, sharp focus, incredibly detailed, hard contrast".
        - FORBIDDEN: "blur, bokeh, soft focus, fuzzy".
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [Caption]
        """
        
        response = model.generate_content(instruction)
        parts = response.text.strip().split("|||")
        
        if len(parts) == 2:
            p_text = parts[0].replace("PROMPT:", "").strip()
            c_text = parts[1].replace("CAPTION:", "").strip()
            # "Real-ESRGAN" modeli için promptu temiz tutuyoruz
            final_prompt = p_text + ", sharp focus, 8k uhd, highly detailed"
            print(f"🎨 Theme: {theme}")
            return final_prompt, c_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        return "cyberpunk city street night neon, 8k, sharp focus", "Neon vibes. 🌃✨ #wallpaper"

def download_base_image(prompt):
    print("🎨 1. AŞAMA: SDXL Baz Resmi Çiziyor...")
    # SDXL Modeli
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # 768x1344 (En temiz ham görüntü)
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768,
                "height": 1344,
                "num_inference_steps": 35,
                "guidance_scale": 7.5
            }
        }
        
        try:
            print(f"➡️ Token {idx+1} deneniyor...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Baz Resim Hazır.")
                return response.content
            elif "loading" in response.text:
                time.sleep(5)
            else:
                print(f"❌ Hata: {response.status_code}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            
    return None

def imgupscaler_engine(image_bytes):
    print("🚀 2. AŞAMA: Real-ESRGAN Motoru Çalışıyor (ImgUpscaler Teknolojisi)...")
    
    # BU MODEL 'imgupscaler.com' GİBİ SİTELERİN KULLANDIĞI MOTORUN AYNISIDIR.
    # Resmi alır, çözünürlüğü 2x veya 4x yapar ve detayları yapay zeka ile çizer.
    UPSCALER_URL = "https://api-inference.huggingface.co/models/ai-forever/Real-ESRGAN"
    
    for token in valid_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Resmi modele gönderiyoruz
            response = requests.post(UPSCALER_URL, headers=headers, data=image_bytes, timeout=60)
            
            if response.status_code == 200:
                print("✅ MÜKEMMEL! Resim Upscale edildi (Kalite Yükseltildi).")
                return response.content
            
            elif "loading" in response.text:
                print("⏳ Upscaler ısınıyor (Bekleyiniz)...")
                time.sleep(15)
                # Tekrar dene
                response = requests.post(UPSCALER_URL, headers=headers, data=image_bytes, timeout=60)
                if response.status_code == 200:
                    return response.content
            
            else:
                print(f"⚠️ Upscale Hatası (Kod {response.status_code}). Orijinal kullanılacak.")
                
        except Exception as e:
            print(f"Upscale Bağlantı Hatası: {e}")
            
    return None

def save_and_post(final_image_bytes, tweet_text):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(final_image_bytes)
        
    size = os.path.getsize(filename) / 1024
    print(f"💾 Paylaşılacak Dosya Boyutu: {size:.0f}KB")
    
    if size < 50:
        print("❌ Hata: Dosya bozuk, paylaşılmıyor.")
        return

    print("🐦 Twitter'a yükleniyor...")
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(filename)
        
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        print("✅ BAŞARILI! Tweet Atıldı.")
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text, tweet_content = get_creative_content()
    
    # 1. SDXL ile Resmi Oluştur
    original_img = download_base_image(prompt_text)
    
    if original_img:
        # 2. Real-ESRGAN (ImgUpscaler Teknolojisi) ile Kaliteyi Artır
        # Ben dokunmuyorum, yapay zeka yapıyor.
        upscaled_img = imgupscaler_engine(original_img)
        
        if upscaled_img:
            save_and_post(upscaled_img, tweet_content)
        else:
            print("⚠️ Upscale servisi yanıt vermedi, orijinal (HD) resim paylaşılıyor.")
            save_and_post(original_img, tweet_content)
    else:
        print("❌ Resim üretilemedi.")
