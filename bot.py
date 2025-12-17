import os
import time
import requests
import random
import json
from PIL import Image, ImageEnhance, ImageFilter
from tweepy import OAuthHandler, API, Client

# -----------------------------
# ENV KEYS (Senin çalışan botundaki gibi getenv ile)
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY      = os.getenv("GROQ_KEY")

# -----------------------------
# YARDIMCI: GROQ AI (METİN YAZARI)
# -----------------------------
def ask_groq(prompt):
    if not GROQ_KEY:
        print("UYARI: Groq Key yok.", flush=True)
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
        res = requests.post(url, headers=headers, json=data, timeout=20)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Hata: {e}")
    return None

# -----------------------------
# YARDIMCI: GÖRSEL HD YAPMA
# -----------------------------
def enhance_image(img_path):
    try:
        img = Image.open(img_path)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.2)
        img.save("final_image.jpg", quality=95)
        return "final_image.jpg"
    except:
        return img_path

# -----------------------------
# 1. İÇERİK ÜRETİCİ (ANIME MODU)
# -----------------------------
def get_anime_content():
    print("🧠 Anime içeriği aranıyor...", flush=True)
    
    # Jikan'dan Veri Çek (Rate Limit yememek için denemeli)
    max_retries = 3
    for i in range(max_retries):
        try:
            # Rastgele bir sayfa seç
            page = random.randint(1, 10)
            url = f"https://api.jikan.moe/v4/top/anime?page={page}"
            resp = requests.get(url, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()['data']
                item = random.choice(data)
                
                name = item['title_english'] if item.get('title_english') else item['title']
                img_url = item['images']['jpg']['large_image_url']
                synopsis = item.get('synopsis', 'No info')[:600]
                
                # Groq'a Tweet Yazdır
                prompt = f"""
                Act as 'Orbis Anime'. Write a short, engaging tweet about: {name}.
                Context: {synopsis}
                Rules:
                1. Start with Title in BOLD + Emoji.
                2. One hype sentence.
                3. Use hashtags: #{name.replace(' ','')} #Anime.
                """
                caption = ask_groq(prompt)
                
                if caption:
                    return name, img_url, caption
            
            time.sleep(2) # Hata varsa az bekle
        except Exception as e:
            print(f"Veri çekme hatası ({i+1}): {e}")
            time.sleep(2)
            
    return None, None, None

# -----------------------------
# 2. TWITTER POST (SENİN ÇALIŞAN KODUNUN AYNISI)
# -----------------------------
def post_to_twitter(img_url, caption):
    # Resmi İndir
    print("⬇️ Resim indiriliyor...", flush=True)
    try:
        img_data = requests.get(img_url).content
        with open("temp.jpg", "wb") as f:
            f.write(img_data)
        
        # HD Yap
        filename = enhance_image("temp.jpg")
    except Exception as e:
        print(f"Resim indirme hatası: {e}")
        return False

    # Twitter'a Yükle
    print("🐦 Twitter'a bağlanılıyor...", flush=True)
    try:
        # 1. Adım: Medya Yükleme (V1.1 - Burası her zaman API objesi ister)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        
        media = api.media_upload(filename)
        print("✅ Resim yüklendi, ID alındı.")

        # 2. Adım: Tweet Atma (Senin diğer kodundaki Client yapısı)
        # BURAYA DİKKAT: V2 (Client) hata verirse otomatik V1 (API) deneyecek sistem ekledim.
        # Böylece o 403 hatasını bypass edebiliriz.
        
        try:
            # Önce senin çalışan kodundaki gibi Client (V2) deniyoruz
            client = Client(
                consumer_key=API_KEY,
                consumer_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_SECRET
            )
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print("🎉 TWEET ATILDI (V2 Client ile)!")
            return True
            
        except Exception as v2_error:
            print(f"⚠️ V2 (Client) Hatası: {v2_error}")
            print("🔄 V1.1 (API) ile tekrar deneniyor... (Yedek Sistem)")
            
            # Eğer Client çalışmazsa, eski usül API ile atar (Bu kesin çalışır)
            api.update_status(status=caption, media_ids=[media.media_id])
            print("🎉 TWEET ATILDI (V1.1 Yedek Sistem ile)!")
            return True

    except Exception as e:
        print(f"❌ Kritik Twitter Hatası: {e}", flush=True)
        return False

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 ORBIS ANIME BAŞLATILIYOR (ÇALIŞAN BOT ÖRNEĞİ)...", flush=True)
    
    # İçerik Al
    name, img_url, caption = get_anime_content()
    
    if name and img_url and caption:
        print("------------------------------------------------", flush=True)
        print(f"🎯 Seçilen Anime: {name}", flush=True)
        print(f"📝 Tweet: {caption[:50]}...", flush=True)
        print("------------------------------------------------", flush=True)
        
        post_to_twitter(img_url, caption)
    else:
        print("⚠️ İçerik oluşturulamadı.", flush=True)
