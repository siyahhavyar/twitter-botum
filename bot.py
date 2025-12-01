import os
import requests
import random
import time
import google.generativeai as genai
import tweepy
import cv2
import numpy as np

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
    print("🧠 Gemini (Pro): Generating Ultra-High-Res concept...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro') 
        
        themes = [
            "Hyper-Detailed Cyberpunk Street", "Macro Water Drop on Leaf", 
            "Ultra-Realistic Eye Iris", "Space Galaxy Nebula 8K", 
            "Bioluminescent Avatar Forest", "Crystal Clear Ice Cave",
            "Futuristic Gold & Marble Architecture", "Neon Noir Rain",
            "Detailed Mechanical Watch Movement", "Vibrant Oil Painting Texture"
        ]
        theme = random.choice(themes)
        
        instruction = f"""
        Role: Art Director. Theme: "{theme}".
        
        TASK:
        1. Write a prompt for 'Stable Diffusion XL'.
        2. Write a short English Tweet caption.
        3. Hashtags.
        
        RULES:
        - Keywords: "8k resolution, photorealistic, sharp focus, incredibly detailed, hard contrast, ray tracing, unreal engine 5".
        - FORBIDDEN: "blur, bokeh, soft focus, fuzzy, low res".
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [Caption]
        """
        
        response = model.generate_content(instruction)
        parts = response.text.strip().split("|||")
        
        if len(parts) == 2:
            p_text = parts[0].replace("PROMPT:", "").strip()
            c_text = parts[1].replace("CAPTION:", "").strip()
            # Keskinlik Komutları (16K hissi için)
            final_prompt = p_text + ", sharp focus, 8k uhd, crystal clear, high fidelity, no blur, highly detailed, hdr"
            print(f"🎨 Theme: {theme}")
            return final_prompt, c_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        return "cyberpunk city street night neon, sharp focus, 8k, hdr", "Neon vibes. 🌃✨ #wallpaper"

def download_image_sdxl(prompt):
    print("🎨 1. AŞAMA: Hugging Face (SDXL) Baz Resmi Çiziyor...")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # 768x1344 -> SDXL'in en temiz olduğu boyut.
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768,
                "height": 1344,
                "num_inference_steps": 45, # Detay için artırdık
                "guidance_scale": 8.0     # Prompta daha sıkı bağlılık
            }
        }
        
        try:
            print(f"➡️ Token {idx+1} deneniyor...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=40)
            
            if response.status_code == 200:
                print("✅ Baz Resim Hazır.")
                return response.content
            elif "loading" in response.text:
                print("⏳ Model ısınıyor...")
                time.sleep(5)
            else:
                print(f"❌ Hata: {response.status_code}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            
    return None

def ai_upscale_image(image_bytes):
    print("🚀 2. AŞAMA: Yapay Zeka ile Büyütülüyor (x2 Upscale)...")
    
    # Bu model resmi bulanıklık olmadan 2 katına çıkarır (Yaklaşık 3000px yükseklik)
    UPSCALER_URL = "https://api-inference.huggingface.co/models/caidas/swin2SR-classical-sr-x2-64"
    
    for token in valid_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.post(UPSCALER_URL, headers=headers, data=image_bytes, timeout=80)
            
            if response.status_code == 200:
                print("✅ Upscale Başarılı! Çözünürlük arttı.")
                return response.content
            
            elif "loading" in response.text:
                print("⏳ Upscaler ısınıyor...")
                time.sleep(10)
                # Tekrar dene
                response = requests.post(UPSCALER_URL, headers=headers, data=image_bytes, timeout=80)
                if response.status_code == 200:
                    return response.content
            
        except Exception as e:
            print(f"Upscale Hatası: {e}")
            
    return None

def enhance_clarity(filename):
    print("💎 3. AŞAMA: '16K Hissi' Veren Keskinleştirme (HDR Effect)...")
    try:
        img = cv2.imread(filename)
        if img is None: return False

        # A) Keskinleştirme Filtresi (Unsharp Mask)
        # Görüntüyü hafif bulanıklaştırıp orijinalden çıkararak kenarları belirginleştirir.
        gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
        unsharp_image = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0, img)

        # B) Detay Artırma (CLAHE - Contrast Limited Adaptive Histogram Equalization)
        # Bu işlem renkleri patlatır ve gölgelerdeki detayları ortaya çıkarır.
        # Önce LAB renk uzayına çeviriyoruz
        lab = cv2.cvtColor(unsharp_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        limg = cv2.merge((cl,a,b))
        final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Kaydet (Maksimum kalite JPG)
        cv2.imwrite(filename, final_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
        
        new_size = os.path.getsize(filename) / 1024
        print(f"✅ FİNAL GÖRÜNTÜ HAZIR! Dosya Boyutu: {new_size:.0f}KB")
        return True

    except Exception as e:
        print(f"Efekt Hatası: {e}")
        return False

def save_and_post(final_image_bytes, tweet_text):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(final_image_bytes)
        
    size = os.path.getsize(filename) / 1024
    if size < 50:
        print("❌ Dosya bozuk.")
        return

    # --- YENİ ADIM: HDR ve KESKİNLİK EFEKTİ ---
    enhance_clarity(filename)

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
    
    # 1. SDXL ile Temiz Baz Resim
    original_img = download_image_sdxl(prompt_text)
    
    if original_img:
        # 2. Yapay Zeka ile Büyüt (AI Upscale)
        upscaled_img = ai_upscale_image(original_img)
        
        if upscaled_img:
            # Upscale olmuş resmi kaydet ve Efekt uygula
            save_and_post(upscaled_img, tweet_content)
        else:
            print("⚠️ Upscale olmadı, orijinali HDleştirip atıyoruz.")
            save_and_post(original_img, tweet_content)
    else:
        print("❌ Resim üretilemedi.")
