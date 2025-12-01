import os
import requests
import time
import random
import google.generativeai as genai
import tweepy

# --- ŞİFRELER ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
CONSUMER_KEY = os.environ.get("API_KEY")
CONSUMER_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

# --- HUGGING FACE TOKEN LİSTESİ (Yedekli Sistem) ---
hf_tokens = [
    os.environ.get("HF_TOKEN_1"),
    os.environ.get("HF_TOKEN_2"),
    os.environ.get("HF_TOKEN_3"),
    os.environ.get("HF_TOKEN_4"),
    os.environ.get("HF_TOKEN_5"),
    os.environ.get("HF_TOKEN_6")
]
valid_tokens = [t for t in hf_tokens if t]

# --- YENİ MODEL LİSTESİ (Çalışanlar) ---
# Playground kapandığı için FLUX ve SD 3.5'e geçtik.
MODELS_TO_TRY = [
    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large",
    "https://api-inference.huggingface.co/models/ByteDance/SDXL-Lightning"
]

def get_image_prompt():
    print("Gemini 1.5: Konu düşünülüyor...")
    try:
        # Python sürümünü yükselttiğimiz için artık 1.5 Flash çalışacak
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        instruction = """
        You are an AI Wallpaper Art Director.
        Goal: Create a prompt for FLUX.1 AI.
        Style: "Vector Art", "Anime Background", "Digital Illustration".
        Rules: NO "Realistic", NO "3D Render" (To avoid blur).
        Subject: Cyberpunk city, Japanese Aesthetic, Space, Minimalist Nature.
        Output: ONLY the prompt text.
        """
        
        response = model.generate_content(instruction)
        prompt = response.text.strip()
        final_prompt = prompt + ", vector art, sharp lines, flat color, cel shaded, 8k resolution, high contrast, masterpiece"
        print(f"Fikir: {prompt}")
        return final_prompt
    except Exception as e:
        print(f"⚠️ Gemini Hatası: {e}")
        return "cyberpunk city street with neon lights, vector art, sharp lines, flat colors, 8k resolution"

def query_huggingface_smart(payload):
    # Dış Döngü: TOKENLER
    for t_index, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # İç Döngü: MODELLER
        for m_index, model_url in enumerate(MODELS_TO_TRY):
            print(f"➡️ Deneme: Token {t_index+1} -> Model: {model_url.split('/')[-1]}")
            
            for attempt in range(3): # 3 kere dene
                try:
                    response = requests.post(model_url, headers=headers, json=payload)
                    
                    # BAŞARILI
                    if response.status_code == 200:
                        print(f"✅ BAŞARILI! Resim çizildi.")
                        return response.content
                    
                    # ISINIYOR (Wait)
                    elif "error" in response.json() and "loading" in response.json()["error"]:
                        wait_time = response.json()["estimated_time"]
                        print(f"⏳ Model ısınıyor... {wait_time:.1f}sn bekle.")
                        time.sleep(wait_time + 2)
                        continue
                    
                    # KAPALI MODEL (410) veya BULUNAMADI (404)
                    elif response.status_code in [404, 410]:
                        print(f"❌ Bu model artık çalışmıyor. Sonrakine geçiliyor.")
                        break # Bu model döngüsünü kır, diğer modele geç
                    
                    # YETKİ YOK (403) - Token hatası olabilir
                    elif response.status_code == 403:
                        print(f"❌ Bu Token için yetki yok. Diğer Tokene geçiliyor.")
                        break # Diğer tokene geçmek için
                        
                    else:
                        print(f"⚠️ Hata kodu: {response.status_code}. Tekrar deneniyor...")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"Bağlantı hatası: {e}")
                    time.sleep(2)
            
            # Eğer resim geldiyse fonksiyondan çık
            # Gelmediyse sonraki modele geçecek
            
    print("🚨 HATA: Tüm Tokenler ve Modeller denendi, sonuç alınamadı.")
    return None

def download_image(prompt):
    print("Hugging Face: Resim çizimi başlatılıyor...")
    
    # 1024x1024 Kare (En net sonuç için)
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1024,
            "height": 1024,
            "guidance_scale": 7.0,
            "num_inference_steps": 25 # FLUX için 25 yeterli
        }
    }
    
    image_bytes = query_huggingface_smart(payload)
    
    if image_bytes:
        filename = "wallpaper_hq.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        
        if os.path.getsize(filename) < 1000:
            print("❌ Hata: İnen dosya bozuk.")
            return None
            
        print("💾 Resim başarıyla kaydedildi.")
        return filename
    else:
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a yükleniyor...")
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
        
        text = "Daily Wallpaper 🎨✨\n#wallpaper #art #ai #4k"
        client.create_tweet(text=text, media_ids=[media.media_id])
        print("✅ TWEET ATILDI!")
        
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
