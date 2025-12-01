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

# --- YEDEK SENARYOLAR (Gemini Bozulursa Devreye Girer) ---
BACKUP_SCENARIOS = [
    {"p": "Cyberpunk city street raining neon lights, vector art", "c": "Neon rain. 🌃☂️ #cyberpunk"},
    {"p": "Deep space nebula with stars, high contrast", "c": "Lost in space. 🌌✨ #space"},
    {"p": "Abstract liquid gold and black marble texture", "c": "Golden touch. 🏆✨ #luxury"},
    {"p": "Majestic snowy mountains at sunrise, photorealistic", "c": "Mountain vibes. 🏔️❄️ #nature"},
    {"p": "Futuristic glass architecture skyscraper", "c": "Future cities. 🏢💠 #architecture"},
    {"p": "Macro photography of water drop on a leaf", "c": "Details matter. 💧🍃 #macro"},
    {"p": "Geometric abstract shapes 3D, orange and blue", "c": "Geometric harmony. 🔶🔷 #abstract"},
    {"p": "Underwater coral reef with colorful fish", "c": "Under the sea. 🐠🌊 #ocean"},
    {"p": "Vibrant oil painting of a flower field", "c": "Painted dreams. 🌻🎨 #art"},
    {"p": "Misty pine forest morning", "c": "Morning mist. 🌲🌫️ #forest"}
]

def get_creative_content():
    print("🧠 Gemini: Generating concept...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash') # 1.5-flash olmazsa 'gemini-pro' deneyebilirsin
        
        themes = ["Cyberpunk", "Nature", "Space", "Abstract", "Retro", "Fantasy", "Architecture", "Macro"]
        selected = random.choice(themes)

        instruction = f"""
        Act as an Art Director. Theme: "{selected}".
        TASK:
        1. Write a prompt for 'Stable Diffusion XL'. 
        2. Write a short English Tweet.
        3. Hashtags.
        
        RULES:
        - Image keywords: "8k resolution, vertical wallpaper, sharp focus, hard contrast, vector lines, no blur".
        - FORBIDDEN: "blur, bokeh, depth of field".
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [Caption]
        """
        
        response = model.generate_content(instruction)
        parts = response.text.strip().split("|||")
        
        if len(parts) == 2:
            p_text = parts[0].replace("PROMPT:", "").strip()
            c_text = parts[1].replace("CAPTION:", "").strip()
            final_prompt = p_text + ", sharp focus, 8k uhd, crystal clear, no blur"
            print(f"🎨 Gemini Success! Theme: {selected}")
            return final_prompt, c_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"⚠️ Gemini Failed. Using RANDOM BACKUP.")
        backup = random.choice(BACKUP_SCENARIOS)
        final_prompt = backup["p"] + ", vertical wallpaper, 8k resolution, sharp focus, no blur"
        return final_prompt, backup["c"]

def try_huggingface(prompt):
    print("🎨 Hugging Face (SDXL) attempting...")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # SDXL Native Boyut (En net hali)
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768, 
                "height": 1344,
                "num_inference_steps": 40,
                "guidance_scale": 7.5
            }
        }
        
        try:
            print(f"➡️ Trying Token {idx+1}...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Hugging Face SUCCESS!")
                return response.content
            elif "loading" in response.text:
                print("⏳ Model loading...")
                time.sleep(5)
            else:
                print(f"❌ Error Code: {response.status_code}")
                
        except Exception as e:
            print(f"Connection error: {e}")
            
    return None

def try_pollinations_backup(prompt):
    print("🛡️ BACKUP SYSTEM (Pollinations) Activated...")
    try:
        encoded = requests.utils.quote(prompt)
        url = f"https://pollinations.ai/p/{encoded}?width=768&height=1344&seed={random.randint(1,1000)}&model=flux-realism&nologo=true&enhance=true"
        
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            print("✅ Backup system generated image!")
            return response.content
    except Exception as e:
        print(f"Backup error: {e}")
    return None

def upscale_image_to_4k(filename):
    print("🚀 UPSCALING ENGINE: Resmi 4K Yapıyor & Keskinleştiriyor...")
    try:
        # 1. Resmi Oku
        img = cv2.imread(filename)
        if img is None:
            print("❌ Resim okunamadı.")
            return False

        # 2. Boyutları al ve 2 Katına çıkar (Upscale)
        # Lanczos4 interpolasyonu en kaliteli büyütme yöntemidir.
        h, w = img.shape[:2]
        new_w, new_h = w * 2, h * 2
        upscaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        print(f"📏 Yeni Boyut: {new_w}x{new_h} (HD/4K Ready)")

        # 3. Keskinleştirme (Sharpening Kernel) - Bulanıklığı siler
        # Bu matris, kenarları belirginleştirir.
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)

        # 4. Kaydet (Eski resmin üzerine yaz)
        cv2.imwrite(filename, sharpened, [cv2.IMWRITE_JPEG_QUALITY, 100])
        
        new_size = os.path.getsize(filename) / 1024
        print(f"✅ İŞLEM TAMAM! Yeni Dosya Boyutu: {new_size:.0f}KB")
        return True

    except Exception as e:
        print(f"Upscale Hatası: {e}")
        return False

def save_and_post(image_bytes, tweet_text):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(image_bytes)
        
    if os.path.getsize(filename) < 1000:
        print("❌ Corrupted file.")
        return

    # --- YENİ ADIM: RESMİ BÜYÜT VE NETLEŞTİR ---
    success = upscale_image_to_4k(filename)
    if not success:
        print("⚠️ Upscale başarısız oldu, orijinal resim paylaşılıyor.")

    print("🐦 Uploading to Twitter...")
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
        print("✅ TWEET POSTED SUCCESSFULLY!")
    except Exception as e:
        print(f"Twitter Error: {e}")

if __name__ == "__main__":
    prompt_text, tweet_content = get_creative_content()
    
    # 1. Resmi Üret
    img_data = try_huggingface(prompt_text)
    if not img_data:
        img_data = try_pollinations_backup(prompt_text)
        
    # 2. Resmi Büyüt, Keskinleştir ve Paylaş
    if img_data:
        save_and_post(img_data, tweet_content)
    else:
        print("❌ Failed to generate image.")
