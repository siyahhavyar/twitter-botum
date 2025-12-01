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
    print("🧠 Gemini: Thinking of a concept and caption in English...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # SENİN İSTEDİĞİN GİBİ BURAYA DOKUNMADIM, AYNI KALIYOR
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        themes = [
            "Minimalist Pastel Clouds", 
            "Macro Photography of Water Droplets", "Abstract Fluid Colors", 
            "Retro 80s Synthwave Sunset", "Majestic Fantasy Castle", 
            "Deep Space Nebula", "Isometric Tiny Room 3D", 
            "Bioluminescent Forest", "Zen Japanese Garden", 
            "Futuristic Glass Architecture", "Cute Geometric Animal Vector", 
            "Vibrant Oil Painting Style", "Black and White Noir City", 
            "Underwater Coral Reef", "Pixel Art Landscape", 
            "Dreamy Surrealism", "Glitch Art Aesthetic"
        ]
        selected_theme = random.choice(themes)
        
        instruction = f"""
        You are a professional Social Media Manager and Art Director.
        
        TASK:
        1. Create a unique, highly detailed image prompt based on: "{selected_theme}".
        2. Write a short, engaging, aesthetic tweet caption (in English) for this image.
        3. Add 3-4 relevant hashtags (e.g., #Wallpaper #Art).
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [English Tweet Text]
        
        RULES:
        - Image Prompt must imply "8k, vertical wallpaper, sharp focus, masterpiece".
        - Caption should be cool, minimal, or poetic. NOT robotic.
        """
        
        response = model.generate_content(instruction)
        raw_text = response.text.strip()
        
        parts = raw_text.split("|||")
        
        if len(parts) == 2:
            image_prompt = parts[0].replace("PROMPT:", "").strip()
            tweet_text = parts[1].replace("CAPTION:", "").strip()
            
            # Kalite Garantisi (Burası promptu güçlendirir)
            final_prompt = image_prompt + ", vertical wallpaper, 8k resolution, ultra detailed, high contrast, vivid colors, sharp focus, no blur, crystal clear"
            
            print(f"🎨 Theme: {selected_theme}")
            print(f"📝 Caption: {tweet_text}")
            return final_prompt, tweet_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        return "minimalist aesthetic sunset over ocean, vector art, 8k", "Nature vibes... 🌊✨ #wallpaper #art #aesthetic"

def try_huggingface(prompt):
    print("🎨 Hugging Face (SDXL) attempting...")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # SDXL'in EN NET olduğu doğal çözünürlük budur (768x1344).
        # Bunu değiştirirsek görüntü bulanıklaşır.
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 768, 
                "height": 1344,
                "num_inference_steps": 40, # Detay seviyesi yüksek
                "guidance_scale": 7.5
            }
        }
        
        try:
            print(f"➡️ Trying Token {idx+1}...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
            
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
            
    print("🚨 Hugging Face failed. Switching to Backup.")
    return None

def try_pollinations_backup(prompt):
    print("🛡️ BACKUP SYSTEM (Pollinations) Activated...")
    try:
        encoded = requests.utils.quote(prompt)
        
        # --- İŞTE KALİTE AYARI BURADA ---
        # 1920 yerine 1344 yapıyoruz. Bu sayede "sündürme" olmuyor, görüntü cam gibi net çıkıyor.
        # model=flux-realism yaptık ki daha gerçekçi olsun.
        url = f"https://pollinations.ai/p/{encoded}?width=768&height=1344&seed={random.randint(1,1000)}&model=flux-realism&nologo=true&enhance=true"
        
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            print("✅ Backup system generated SHARP HD image!")
            return response.content
    except Exception as e:
        print(f"Backup error: {e}")
    return None

def save_and_post(image_bytes, tweet_text):
    filename = "wallpaper.jpg"
    with open(filename, "wb") as f:
        f.write(image_bytes)
        
    if os.path.getsize(filename) < 1000:
        print("❌ Corrupted file.")
        return

    print("🐦 Uploading to Twitter...")
    try:
        # Upload Media
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        media = api.media_upload(filename)
        
        # Post Tweet
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
    
    img_data = try_huggingface(prompt_text)
    if not img_data:
        img_data = try_pollinations_backup(prompt_text)
        
    if img_data:
        save_and_post(img_data, tweet_content)
    else:
        print("❌ Failed to generate image.")
