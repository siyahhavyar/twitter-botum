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
    print("🧠 Gemini: Generating concept...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Model ismini güncelledik, artık hata vermeyecek
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # KONU LİSTESİ (Çeşitlilik için)
        themes = [
            "Cyberpunk City Rain Neon", "Minimalist Zen Garden", "Hyper-Realistic Water Droplets", 
            "Neon Noir Street", "Deep Space Nebula", "Crystal Cave", 
            "Futuristic Glass Architecture", "Bioluminescent Forest", "Sunset snowy mountains",
            "Abstract Liquid Gold", "Geometric 3D shapes", "Synthwave 80s Road",
            "Macro Eye Photography", "Underwater Coral Reef", "Misty Pine Forest",
            "Vibrant Oil Painting", "Paper Cutout Art", "Stormy Ocean Waves", 
            "Detailed Mechanical Watch", "Fire and Ice Abstract", "Dreamy Clouds Pastel", 
            "Isometric Tiny House", "Steampunk Airship", "Glitch Art Portrait", 
            "Marble Texture Gold", "Double Exposure Nature", "Majestic Lion Portrait"
        ]
        theme = random.choice(themes)
        
        instruction = f"""
        Act as an Art Director. Theme: "{theme}".
        
        TASK:
        1. Write a prompt for 'Flux' AI. 
        2. Write a short English Tweet.
        3. Hashtags.
        
        RULES:
        - Keywords to include: "8k resolution, photorealistic, sharp focus, incredibly detailed, macro photography, hard contrast".
        - FORBIDDEN: "blur, bokeh, soft, depth of field" (We want full sharpness).
        
        FORMAT:
        PROMPT: [Image Prompt] ||| CAPTION: [Caption]
        """
        
        response = model.generate_content(instruction)
        parts = response.text.strip().split("|||")
        
        if len(parts) == 2:
            p_text = parts[0].replace("PROMPT:", "").strip()
            c_text = parts[1].replace("CAPTION:", "").strip()
            # Keskinlik Garantisi
            final_prompt = p_text + ", sharp focus, 8k uhd, crystal clear, high fidelity, no blur, highly detailed"
            print(f"🎨 Theme: {theme}")
            return final_prompt, c_text
        else:
            raise Exception("Format Error")
            
    except Exception as e:
        print(f"⚠️ Gemini Error: {e}")
        # Yedek Plan
        return "hyper-realistic water drop on leaf, macro photo, 8k, sharp focus, high contrast", "Nature details. 🌿💧 #wallpaper"

def download_image_sharp(prompt):
    print("💎 Pollinations (Flux): Rendering sharp image...")
    
    encoded = requests.utils.quote(prompt)
    seed = random.randint(1, 100000)
    
    # --- KALİTE AYARLARI ---
    # Width/Height: 768x1344 (Bu yapay zekanın "Native" boyutudur. EN NET sonucu bu verir)
    # Model: flux (En stabili budur)
    # Enhance: true (Renkleri canlandırır)
    
    url = f"https://pollinations.ai/p/{encoded}?width=768&height=1344&seed={seed}&model=flux&nologo=true&enhance=true"
    
    try:
        # İndirme süresini biraz uzattık (timeout=90) ki yarıda kesilmesin
        response = requests.get(url, timeout=90)
        
        if response.status_code == 200:
            filename = "wallpaper.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            size = os.path.getsize(filename) / 1024
            print(f"✅ Image Downloaded! Size: {size:.0f}KB")
            
            # Eğer dosya 50KB'dan küçükse resim inmemiş demektir
            if size < 50: 
                print("❌ File too small (Error text returned). Retrying with simple prompt...")
                return None
                
            return filename
        else:
            print(f"❌ Server Error: {response.status_code}")
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
    
    # İlk deneme
    image_file = download_image_sharp(prompt)
    
    # Eğer ilk deneme başarısız olursa, basit bir prompt ile tekrar dene (Yedek)
    if not image_file:
        print("🔄 Retrying with backup prompt...")
        image_file = download_image_sharp("minimalist abstract geometric shapes, 8k, sharp focus, vibrant colors")
        caption = "Abstract vibes. ✨ #wallpaper #art"
    
    if image_file:
        post_to_twitter(image_file, caption)
    else:
        print("❌ Final failure. No image generated.")
