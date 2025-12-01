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
    print("🧠 Gemini (Pro): Generating concept...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # GÜNCELLEME: En güvenli model 'gemini-pro'dur.
        model = genai.GenerativeModel('gemini-pro')
        
        themes = [
            "Cyberpunk City Neon Rain", "Minimalist Zen Garden", "Space Nebula", 
            "Futuristic Architecture", "Bioluminescent Forest", "Sunset Mountains",
            "Abstract Liquid 3D", "Geometric Shapes", "Synthwave Retro",
            "Macro Nature Photography", "Underwater Reef", "Vibrant Oil Painting",
            "Stormy Ocean", "Mechanical Watch Gears", "Glitch Art"
        ]
        theme = random.choice(themes)
        
        instruction = f"""
        Act as an Art Director. Theme: "{theme}".
        
        TASK:
        1. Write a prompt for 'Stable Diffusion XL'.
        2. Write a short English Tweet caption.
        3. Hashtags.
        
        RULES:
        - Keywords: "8k resolution, photorealistic, sharp focus, incredibly detailed, hard contrast".
        - FORBIDDEN: "blur, bokeh, soft focus" (Must be sharp).
        
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
        return "cyberpunk city street night neon, vector art, sharp focus, 8k", "Neon vibes. 🌃✨ #wallpaper #cyberpunk"

def download_image_hf(prompt):
    print("🎨 Hugging Face (SDXL): Rendering HD image...")
    
    # SDXL Base 1.0 (En stabil ve kaliteli açık model)
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    # Her bir tokeni sırayla dene
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # 768x1344 = SDXL'in Dikey HD doğal çözünürlüğü. (Bulanık olmaz)
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
                
                filename = "wallpaper.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                size = os.path.getsize(filename) / 1024
                # 50KB altıysa hata mesajıdır
                if size < 50:
                    print("❌ File too small (Error). Trying next token...")
                    continue
                    
                print(f"✅ Image Ready! Size: {size:.0f}KB")
                return filename
                
            elif "loading" in response.text:
                print("⏳ Model loading... Waiting 10s")
                time.sleep(10)
            else:
                print(f"❌ Error Code: {response.status_code}")
                
        except Exception as e:
            print(f"Connection error: {e}")
            
    print("🚨 All tokens failed.")
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
    image_file = download_image_hf(prompt)
    
    if image_file:
        post_to_twitter(image_file, caption)
    else:
        print("❌ Process failed.")
