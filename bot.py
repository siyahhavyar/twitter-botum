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

def get_creative_content():
    print("🧠 Gemini: Generating sharp creative concept...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # ÇEŞİTLİLİK İÇİN 30 FARKLI TEMA
        themes = [
            "Cyberpunk City Rain", "Minimalist Zen Garden", "Hyper-Realistic Water Droplets", 
            "Neon Noir Street", "Deep Space Nebula", "Crystal Cave", 
            "Futuristic Glass Building", "Bioluminescent Forest", "Sunset over snowy mountains",
            "Abstract Liquid Gold", "Geometric 3D shapes", "Synthwave 80s Road",
            "Macro Eye Photography", "Underwater Coral Reef", "Misty Pine Forest",
            "Ancient Greek Statue with Neon", "Vibrant Oil Painting", "Paper Cutout Art",
            "Stormy Ocean Waves", "Detailed Mechanical Watch Gear", "Fire and Ice Abstract",
            "Dreamy Clouds Pastel", "Isometric Tiny House", "Steampunk Airship",
            "Glitch Art Portrait", "Marble Texture Gold", "Double Exposure Nature",
            "Majestic Lion Portrait", "Tokyo Street Night", "Northern Lights Aurora"
        ]
        theme = random.choice(themes)
        
        # GEMINI İÇİN KESKİNLİK EMRİ
        instruction = f"""
        You are an Art Director.
        Topic: "{theme}"
        
        TASK:
        1. Write a highly detailed image prompt for 'Flux-Realism' AI.
        2. Write a short, cool English caption for Twitter.
        3. Hashtags.
        
        CRITICAL RULES FOR IMAGE PROMPT:
        - Use keywords: "8k resolution, photorealistic, sharp focus, incredibly detailed, macro photography, ray tracing, unreal engine 5, hard contrast".
        - FORBIDDEN: "blur, bokeh, depth of field, soft" (We want everything sharp).
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [Caption]
        """
        
        response = model.generate_content(instruction)
        parts = response.text.strip().split("|||")
        
        if len(parts) == 2:
            p_text = parts[0].replace("PROMPT:", "").strip()
            c_text = parts[1].replace("CAPTION:", "").strip()
            # Ekstra Keskinlik Güçlendiriciler
            final_prompt = p_text + ", sharp focus, 8k uhd, crystal clear, high fidelity, no blur, highly detailed"
            print(f"🎨 Theme: {theme}")
            return final_prompt, c_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "hyper-realistic water drop on leaf, macro photo, 8k, sharp focus", "Nature details. 🌿💧 #wallpaper"

def download_image_sharp(prompt):
    print("💎 Pollinations (Flux-Realism): Rendering sharp image...")
    
    encoded = requests.utils.quote(prompt)
    seed = random.randint(1, 100000)
    
    # --- İŞTE SİHİRLİ AYARLAR BURADA ---
    # Width/Height: 768x1344 (SDXL ve Flux'ın doğal çözünürlüğü - EN NET GÖRÜNTÜ BUDUR)
    # Model: flux-realism (Daha gerçekçi ve net)
    # Enhance: True (Renkleri patlatır)
    
    url = f"https://pollinations.ai/p/{encoded}?width=768&height=1344&seed={seed}&model=flux-realism&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            size = os.path.getsize(filename) / 1024
            print(f"✅ Image Downloaded! Size: {size:.0f}KB")
            
            if size < 50: # Dosya çok küçükse (hata varsa)
                print("❌ File too small, probably failed.")
                return None
                
            return filename
        else:
            print("❌ Server Error.")
            return None
    except Exception as e:
        print(f"Download Error: {e}")
        return None

def post_to_twitter(filename, text):
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
        
        client.create_tweet(text=text, media_ids=[media.media_id])
        print("✅ SUCCESS! Tweet Posted.")
    except Exception as e:
        print(f"Twitter Error: {e}")

if __name__ == "__main__":
    prompt, caption = get_creative_content()
    image_file = download_image_sharp(prompt)
    
    if image_file:
        post_to_twitter(image_file, caption)
    else:
        print("❌ Process failed.")
