import os
import requests
import time
import random
import google.generativeai as genai
import tweepy

# --- ŞİFRELER ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")

# Twitter Şifreleri
CONSUMER_KEY = os.environ.get("API_KEY")
CONSUMER_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

# --- HUGGING FACE TOKEN LİSTESİ ---
hf_tokens = [
    os.environ.get("HF_TOKEN_1"),
    os.environ.get("HF_TOKEN_2"),
    os.environ.get("HF_TOKEN_3"),
    os.environ.get("HF_TOKEN_4"),
    os.environ.get("HF_TOKEN_5"),
    os.environ.get("HF_TOKEN_6")
]
# Sadece dolu olan tokenleri al
valid_tokens = [t for t in hf_tokens if t]

# --- AKILLI MODEL LİSTESİ (Sırayla Dener) ---
# 1. Öncelik: Senin istediğin Playground v2.5
# 2. Öncelik: Proteus (Çok keskin ve estetik bir modeldir, yedeğimiz bu)
# 3. Öncelik: SDXL (En güvenli liman)
MODELS_TO_TRY = [
    "https://api-inference.huggingface.co/models/playgroundai/playground-v2.5-1024px-aesthetic",
    "https://api-inference.huggingface.co/models/dataautogpt3/ProteusV0.4-Lighting", 
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
]

def get_image_prompt():
    print("Gemini: Konu düşünülüyor...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # HATA DÜZELTME: 'gemini-1.5-flash' hata verdiği için 'gemini-pro' kullanıyoruz.
    # Bu model her zaman çalışır.
    model = genai.GenerativeModel('gemini-pro')
    
    instruction = """
    Act as a professional wallpaper curator.
    Task: Create a highly detailed, high-contrast prompt for AI image generation.
    Style: Vector Art, Digital Illustration, or Sharp Anime Style.
    Forbidden: Do not use "photorealistic" or "soft shading" to avoid blur.
    Subject: Aesthetic landscapes, cyberpunk neon city, cute geometric animals, or space.
    Output: ONLY the English prompt.
    """
    
    try:
        response = model.generate_content(instruction)
        prompt = response.text.strip()
        # Keskinlik artırıcı sihirli kelimeler
        final_prompt = prompt + ", aesthetic, 8k resolution, sharp focus, high contrast, vector style, vivid colors, masterpiece, no blur"
        print(f"Fikir: {prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return "cyberpunk city street at night with neon lights, vector art, sharp lines, 8k, high contrast"

def query_huggingface_smart(payload):
    # Dış Döngü: TOKENLERİ Gez
    for t_index, token in enumerate(valid_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        
        # İç Döngü: MODELLERİ Gez
        for m_index, model_url in enumerate(MODELS_TO_TRY):
            print(f"Deneme: Token {t_index+1} ile Model {m_index+1} deneniyor...")
            
            # Bir kombinasyonu 3 kere dene (belki o anlık hatadır)
            for attempt in range(3):
                try:
                    response = requests.post(model_url, headers=headers, json=payload)
                    
                    # BAŞARILI OLDUYSA
                    if response.status_code == 200:
                        print(f"BAŞARILI! Model {m_index+1} resmi çizdi.")
                        return response.content
                    
                    # MODEL ISINIYORSA (Bekle)
                    elif "error" in response.json() and "loading" in response.json()["error"]:
                        wait_time = response.json()["estimated_time"]
                        print(f"Model ısınıyor... {wait_time:.1f}sn bekle.")
                        time.sleep(wait_time + 2)
                        continue
                    
                    # 410 (Kapanmış) veya 404 (Bulunamadı) HATASI
                    elif response.status_code in [404, 410]:
                        print(f"Bu model ({model_url}) şu an yanıt vermiyor (Kod {response.status_code}). Diğer modele geçiliyor.")
                        break # Bu modeli atla, listeki diğer modele geç
                    
                    # DİĞER HATALAR (Token limit vs)
                    else:
                        print(f"Hata kodu: {response.status_code}. Tekrar deneniyor...")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"Bağlantı hatası: {e}")
                    time.sleep(2)
            
            # Eğer buraya geldiysek bu model bu tokenla çalışmadı, sonraki modele geç.
            
    print("TÜM KOMBİNASYONLAR DENENDİ, RESİM ÇİZİLEMEDİ.")
    return None

def download_image(prompt):
    print("Resim oluşturma süreci başladı...")
    
    # 1024x1024 Kare format (En net sonuç için)
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1024,
            "height": 1024,
            "guidance_scale": 6, 
            "num_inference_steps": 40
        }
    }
    
    image_bytes = query_huggingface_smart(payload)
    
    if image_bytes:
        filename = "wallpaper_hq.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        
        # Dosya kontrolü
        if os.path.getsize(filename) < 1000:
            print("Hata: İnen dosya bozuk.")
            return None
            
        print("Resim başarıyla kaydedildi.")
        return filename
    else:
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a yükleniyor...")
    try:
        # V1.1
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        media_id = media.media_id
        
        # V2
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "Daily 4K Wallpaper ✨\n#wallpaper #art #aiart #design"
        
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI: Paylaşıldı!")
        
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
