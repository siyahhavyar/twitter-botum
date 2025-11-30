import tweepy
import os
import time
import json
import requests
import random
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Hata vermeyen en sağlam model
model = genai.GenerativeModel('gemini-1.5-flash')

def get_autonomous_idea():
    print("🧠 Gemini, senin zevkine uygun ve ULTRA DETAYLI bir fikir kurguluyor...")
    
    # --- GÜNCELLENMİŞ EMİR ---
    prompt_emir = """
    Sen benim kişisel dijital sanat yönetmenimsin. Twitter hesabım için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    YARATICIMIN SEVDİĞİ TARZLAR (Bunları temel al, birleştir, şaşırt):
    1. Minimalist Doğa (Sakin, sisli, huzurlu, tek ağaç, yansımalar)
    2. Estetik Geometri (Bauhaus, düz çizgiler, pastel tonlar, soyut formlar)
    3. Temiz Bilim Kurgu (Neon, retro-fütürizm, sade uzay, yalnız astronot)
    4. Sürrealist Rüyalar (Mantık dışı ama estetik, bulutların üstü, uçan yapılar)
    5. Sinematik Işık (Gün batımı, 'Golden hour', dramatik gölgeler, loş ve huzurlu)

    GÖREVİN:
    1. Yukarıdaki tarzlardan yola çıkarak BENZERSİZ ve ÇOK HAVALI bir görsel fikir bul.
    2. Bu fikri çizmesi için yapay zekaya İNGİLİZCE bir emir (prompt) yaz.
    3. Promptun içine MUTLAKA şu kalite komutlarını gizle: '8k resolution, insanely detailed, sharp focus, intricate details, masterpiece, raw photo, cinematic lighting'.
    
    ETİKET GÖREVİN (ÇOK ÖNEMLİ):
    - Asla #art #picture gibi sıkıcı ve genel etiketler kullanma.
    - O an tasarladığın resme ÖZEL, insanların Twitter'da aratacağı, popüler ve havalı İngilizce etiketler bul.
    - Örnek: Eğer neonlu bir şehir çiziyorsan #CyberpunkAesthetic #NeonNoir #Synthwave kullan. Doğa çiziyorsan #MinimalNature #FoggyMorning kullan.

    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, çok kısa (max 1 cümle), havalı ve emojili bir açıklama. Hemen altına bulduğun o harika etiketleri ekle.",
      "image_prompt": "Yapay zeka için hazırladığın, kalite komutlarıyla dolu o muhteşem İNGİLİZCE prompt."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Fikir ve Etiketler Hazır: {data['caption'][:50]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu devreye girdi.")
        return {
            "caption": "Serenity. 🌫️ \n\n#Minimalist #FoggyAesthetic #NatureDesign #Wallpaper4K",
            "image_prompt": "A lone, perfectly symmetrical tree on a foggy island, minimalist style, vertical, 8k resolution, insanely detailed, sharp focus, cinematic lighting, raw photo"
        }

# --- ULTRA KALİTELİ RESSAM (POLLINATIONS FLUX) ---
def generate_image_flux(prompt):
    print(f"🎨 Flux ULTRA KALİTE Çiziyor: {prompt[:50]}...")
    
    encoded_prompt = requests.utils.quote(prompt)
    seed = random.randint(1, 10000000)
    
    # --- GÜNCELLEME BURADA: ÇÖZÜNÜRLÜK ARTTI (QHD+) ---
    # 1080x1920 yerine 1440x2560 kullanıyoruz. Çok daha keskin.
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1440&height=2560&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        # Yüksek kalite için indirme süresini (timeout) 120 saniyeye çıkardık.
        response = requests.get(url, timeout=120)
        
        if response.status_code == 200 and len(response.content) > 0:
            with open("tweet_image.jpg", 'wb') as f:
                f.write(response.content)
            print("✅ Ultra Kaliteli Resim İndirildi.")
            return True
        else:
            print(f"❌ Resim hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ İndirme hatası (Sunucu yoğun olabilir): {e}")
        return False

def post_tweet():
    content = get_autonomous_idea()
    
    if generate_image_flux(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            # Tweepy v1.1 API (Medya yükleme için)
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            # Tweepy v2 Client (Tweet atmak için)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            # Resmi yükle
            media = api.media_upload(filename="tweet_image.jpg")
            time.sleep(3) # Yüklemenin tamamlanması için kısa bir bekleme

            # Tweeti at
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER'DA PAYLAŞILDI! (Ultra Kalite)")
            
            # Temizlik
            if os.path.exists("tweet_image.jpg"):
                os.remove("tweet_image.jpg")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("⚠️ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()