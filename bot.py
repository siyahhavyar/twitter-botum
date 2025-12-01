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

# --- GEMINI ÇALIŞMAZSA DEVREYE GİRECEK 50 FARKLI SENARYO ---
# Artık "Nature vibes" hatası almayacaksın.
BACKUP_SCENARIOS = [
    {"p": "Cyberpunk city street raining neon lights, vector art, sharp lines", "c": "Neon rain. 🌃☂️ #cyberpunk #wallpaper"},
    {"p": "Minimalist japanese zen garden, flat design, pastel colors", "c": "Peace of mind. 🌿🏯 #zen #minimalist"},
    {"p": "Deep space nebula with stars, high contrast, 8k resolution", "c": "Lost in space. 🌌✨ #space #universe"},
    {"p": "Abstract liquid gold and black marble texture, sharp focus", "c": "Golden touch. 🏆✨ #luxury #wallpaper"},
    {"p": "Retro 80s synthwave sunset road, vector art, vibrant colors", "c": "Retro vibes. 🚗🌅 #synthwave #80s"},
    {"p": "Isometric tiny minimalist room 3D render, cute style", "c": "Tiny living. 🏠✨ #isometric #cute"},
    {"p": "Majestic snowy mountains at sunrise, photorealistic, 8k", "c": "Mountain calling. 🏔️❄️ #nature #wallpaper"},
    {"p": "Bioluminescent forest with glowing mushrooms, fantasy art", "c": "Magic forest. 🍄✨ #fantasy #art"},
    {"p": "Futuristic glass architecture skyscraper, clean lines", "c": "Future cities. 🏢💠 #architecture #future"},
    {"p": "Macro photography of water drop on a leaf, crystal clear", "c": "Details matter. 💧🍃 #macro #nature"},
    {"p": "Geometric abstract shapes 3D, orange and blue", "c": "Geometric harmony. 🔶🔷 #abstract #design"},
    {"p": "Cute vector cat sleeping on a cloud, kawaii style", "c": "Dreamy naps. 🐱☁️ #cute #kawaii"},
    {"p": "Underwater coral reef with colorful fish, 8k detailed", "c": "Under the sea. 🐠🌊 #ocean #life"},
    {"p": "Vibrant oil painting of a flower field, impasto style", "c": "Painted dreams. 🌻🎨 #art #painting"},
    {"p": "Black and white noir detective city street, high contrast", "c": "City shadows. 🕵️‍♂️🌑 #noir #bnw"},
    {"p": "Steampunk airship in the sky, detailed gears", "c": "Steam power. ⚙️🎈 #steampunk #art"},
    {"p": "Glitch art portrait, digital distortion aesthetic", "c": "System failure. 📺👾 #glitch #art"},
    {"p": "Ancient greek statue with neon glasses, vaporwave", "c": "Modern classics. 🗿🕶️ #vaporwave #art"},
    {"p": "Misty pine forest morning, atmospheric lighting", "c": "Morning mist. 🌲🌫️ #forest #mood"},
    {"p": "Paper cutout art style landscape, layered depth", "c": "Paper world. ✂️🏞️ #paperart #craft"}
]

def get_creative_content():
    print("🧠 Gemini: Trying to generate content...")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Çeşitlilik için rastgele tema
        themes = ["Cyberpunk", "Nature", "Space", "Abstract", "Retro", "Fantasy", "Minimalist", "Architecture"]
        selected = random.choice(themes)

        instruction = f"""
        Act as an Art Director. Theme: "{selected}".
        TASK:
        1. Write a prompt for 'Flux' AI. 
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
        print(f"⚠️ Gemini Failed ({e}). Using RANDOM BACKUP SCENARIO.")
        # --- İŞTE BURASI O APTAL HATAYI ENGELLEYEN YER ---
        # Sabit bir metin yerine, yukarıdaki listeden rastgele birini seçiyoruz.
        backup = random.choice(BACKUP_SCENARIOS)
        
        final_prompt = backup["p"] + ", vertical wallpaper, 8k resolution, sharp focus, no blur, high fidelity"
        print(f"🔄 Backup Selected: {backup['c']}")
        return final_prompt, backup["c"]

def try_huggingface(prompt):
    print("🎨 Hugging Face (SDXL) attempting...")
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    for idx, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # TELEFON İÇİN DİKEY HD (768x1344)
        # Bu çözünürlük SDXL için "Native"dir, bulanık olmaz.
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
        
        # 768x1344 -> NET GÖRÜNTÜ İÇİN
        # model=flux-realism
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
