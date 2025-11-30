import os
import requests
import time
import random
import google.generativeai as genai
import tweepy

# --- ŞİFRELERİ ALMA (Ekran Görüntüne Göre) ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")

# Twitter Şifreleri
CONSUMER_KEY = os.environ.get("API_KEY")
CONSUMER_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

# --- HUGGING FACE TOKEN HAVUZU ---
# Tüm tokenleri bir listeye topluyoruz.
hf_tokens = [
    os.environ.get("HF_TOKEN_1"),
    os.environ.get("HF_TOKEN_2"),
    os.environ.get("HF_TOKEN_3"),
    os.environ.get("HF_TOKEN_4"),
    os.environ.get("HF_TOKEN_5"),
    os.environ.get("HF_TOKEN_6")
]
# Boş olanları (None) listeden temizleyelim, sadece dolu olanlar kalsın
valid_tokens = [t for t in hf_tokens if t]

# MODEL: Playground v2.5 (En Keskin/Estetik Model)
API_URL = "https://api-inference.huggingface.co/models/playgroundai/playground-v2.5-1024px-aesthetic"

def get_image_prompt():
    print("Gemini: Playground v2.5 için estetik komut hazırlıyor...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    instruction = """
    Act as a professional wallpaper artist. Create a prompt for 'Playground v2.5'.
    Style: Sharp Focus, 8k, High Contrast, Digital Art.
    Subjects: Minimalist landscapes, cute geometric animals, neon city, abstract fluid.
    Constraint: NO TEXT.
    Output: ONLY the English prompt.
    """
    
    try:
        response = model.generate_content(instruction)
        prompt = response.text.strip()
        # Playground v2.5 Kalite Artırıcıları
        final_prompt = prompt + ", playground v2.5 style, aesthetic, 8k resolution, sharp focus, high contrast, incredibly detailed, masterpiece"
        print(f"Fikir: {prompt}")
        return final_prompt
    except Exception as e:
        print(f"Gemini Hatası: {e}")
        return "cute isometric house on floating island, sharp focus, 8k, vivid colors, playground style"

def query_huggingface_with_rotation(payload):
    # Sırayla tüm tokenleri dene
    for index, token in enumerate(valid_tokens):
        print(f"Token {index + 1}/{len(valid_tokens)} deneniyor...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Bir token içinde en fazla 3 kere "Model Yükleniyor" hatasını bekle
        for attempt in range(3):
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                
                # 1. DURUM: BAŞARILI
                if response.status_code == 200:
                    return response.content
                
                # 2. DURUM: MODEL YÜKLENİYOR (Bekle ve aynı tokeni tekrar dene)
                elif "error" in response.json() and "loading" in response.json()["error"]:
                    wait_time = response.json()["estimated_time"]
                    print(f"Model ısınıyor... {wait_time:.1f} saniye bekleniyor.")
                    time.sleep(wait_time + 2)
                    continue # Aynı token ile tekrar dene
                
                # 3. DURUM: TOKEN LİMİTİ DOLDU (Döngüyü kır, sonraki tokene geç)
                else:
                    print(f"Bu token hata verdi (Kod: {response.status_code}). Sıradakine geçiliyor...")
                    break # İç döngüyü kır, dış döngüden (sonraki tokene) devam et
                    
            except Exception as e:
                print(f"Bağlantı hatası: {e}. Sıradakine geçiliyor.")
                break 

    print("TÜM TOKENLER DENENDİ AMA BAŞARISIZ OLUNDU.")
    return None

def download_image(prompt):
    print("Playground v2.5: Resim çiziliyor...")
    
    # KARE (1024x1024) en keskin sonucu verir. Telefon bunu kırparak kullanır.
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1024,
            "height": 1024,
            "guidance_scale": 5, # Renk canlılığı
            "num_inference_steps": 50
        }
    }
    
    # Yeni rotasyonlu fonksiyonu çağırıyoruz
    image_bytes = query_huggingface_with_rotation(payload)
    
    if image_bytes:
        filename = "wallpaper_hq.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        
        # Dosya boyutu kontrolü (1KB altıysa resim değildir)
        if os.path.getsize(filename) < 1000:
            print("Hata: İnen dosya bozuk.")
            return None
            
        print("Mükemmel! Resim başarıyla kaydedildi.")
        return filename
    else:
        return None

def post_to_twitter(filename, prompt):
    print("Twitter'a yükleniyor...")
    try:
        # V1.1 Giriş (Medya Yükleme)
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename)
        media_id = media.media_id
        
        # V2 Giriş (Tweet Atma)
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        text = "Daily Aesthetic Wallpaper ✨\n#wallpaper #art #4k #aiart"
        
        client.create_tweet(text=text, media_ids=[media_id])
        print("✅ BAŞARILI: Paylaşıldı!")
        
    except Exception as e:
        print(f"Twitter Hatası: {e}")

if __name__ == "__main__":
    prompt_text = get_image_prompt()
    image_file = download_image(prompt_text)
    
    if image_file:
        post_to_twitter(image_file, prompt_text)
