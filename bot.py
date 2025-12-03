import tweepy
import os
import time
import json
import random
import requests
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- 6 MOTORLU YEDEK DEPO (HUGGING FACE) ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),
    os.environ.get('HF_TOKEN_1'),
    os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'),
    os.environ.get('HF_TOKEN_4'),
    os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Hata vermeyen güncel model
model = genai.GenerativeModel('gemini-1.5-flash')

# SDXL API URL
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

def get_artistic_idea():
    print("🧠 Gemini (Art Director) is thinking in English...")
    
    # --- İNGİLİZCE PROMPT EMRİ ---
    prompt_emir = """
    You are a professional digital art curator for a Twitter 'Daily Wallpaper' account.
    
    YOUR TASK:
    1. Imagine a unique, stunning, and aesthetic scene based on: Minimalist Nature, Cyberpunk, Space, Abstract, or Surrealism.
    2. Output ONLY the following JSON format (No markdown, no extra text):
    
    {
      "caption": "Write a short, cool, engaging caption in ENGLISH. Use emojis. Add 3-5 popular hashtags (e.g. #Wallpaper #Art #4K #Aesthetic).",
      "image_prompt": "Write a highly detailed image generation prompt in ENGLISH. MUST INCLUDE: 'vertical wallpaper, 8k resolution, photorealistic, masterpiece, cinematic lighting, sharp focus, --no text'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        if text.startswith("json"): text = text[4:] 
        data = json.loads(text)
        print(f"✅ Idea Found: {data['caption']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Error ({e}), using backup.")
        return {
            "caption": "Serenity in the Stars 🌌 \n\n#Wallpaper #Space #Art #Aesthetic",
            "image_prompt": "A majestic nebula in deep space, glowing stars, cinematic, 8k, vertical, masterpiece"
        }

def query_huggingface(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def generate_image_raw(prompt):
    # Tüm anahtarları sırayla dener
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 Trying Token {i+1}...")
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "text, watermark, blurry, low quality, distorted, ugly, bad anatomy",
                "width": 768, 
                "height": 1344 
            }
        }
        
        try:
            response = query_huggingface(payload, token)
            
            # MODEL UYUYORSA (503) - BEKLE
            if response.status_code == 503:
                print("💤 Model is loading... Waiting 20s...")
                time.sleep(20)
                print("🔄 Retrying...")
                response = query_huggingface(payload, token)
            
            if response.status_code == 200:
                with open("tweet_image.jpg", "wb") as f:
                    f.write(response.content)
                print(f"✅ Image Generated Successfully! (Token {i+1})")
                return True
            else:
                print(f"❌ Error Code: {response.status_code} - Message: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            
    print("🚨 ERROR: All tokens failed.")
    return False

def post_tweet():
    content = get_artistic_idea()
    
    if generate_image_raw(content['image_prompt']):
        print("🐦 Uploading to Twitter...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="tweet_image.jpg")
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER SUCCESS!")
            
        except Exception as e:
            print(f"❌ Twitter Error: {e}")
    else:
        print("⚠️ Image generation failed, skipping tweet.")

if __name__ == "__main__":
    post_tweet()
