import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# 1. ŞİFRELERİ GITHUB KASASINDAN ÇEKİYORUZ
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
INSTA_SESSION = os.environ.get('INSTA_SESSION')

# 2. GEMINI AYARLARI (HATA VERMEYEN YENİ MODEL)
genai.configure(api_key=GEMINI_KEY)
# ESKİSİ: gemini-pro (Hata veriyordu)
# YENİSİ: gemini-1.5-flash (Hatasız çalışır)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. KONU HAVUZU
KONULAR = [
    "Tarihin Çözülememiş Gizemleri", "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları", "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler", "Paranormal Olaylar", "Arkeolojik Keşifler",
    "Kayıp Kıtalar", "Simya ve Okültizm"
]

def icerik_uret():
    print("🧠 Gemini (1.5 Flash) içerik üretiyor...")
    secilen_konu = random.choice(KONULAR)
    
    prompt = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yazarısın. Konu: {secilen_konu}.
    
    Görevin:
    1. Bu konuda şok edici, az bilinen bir olay seç.
    2. Instagram için 10 GÖRSELLİ, hikaye anlatan bir kaydırmalı (Carousel) post hazırla.
    3. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {{
      "baslik": "İlgi çekici Türkçe Başlık",
      "aciklama": "Konuyu anlatan 5-6 paragraflık detaylı Türkçe metin. En sona etiketleri ekle.",
      "gorsel_komutlari": [
        "1. görsel için İngilizce prompt (vertical, 8k, cinematic)",
        "2. görsel için İngilizce prompt (vertical)",
        "3. görsel için İngilizce prompt (vertical)",
        "4. görsel için İngilizce prompt (vertical)",
        "5. görsel için İngilizce prompt (vertical)",
        "6. görsel için İngilizce prompt (vertical)",
        "7. görsel için İngilizce prompt (vertical)",
        "8. görsel için İngilizce prompt (vertical)",
        "9. görsel için İngilizce prompt (vertical)",
        "10. görsel için İngilizce prompt (vertical)"
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu: {data['baslik']}")
        return data
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return None

def resim_ciz(prompt, dosya_adi):
    print(f"🎨 Çiziliyor: {dosya_adi}...")
    # Pollinations Flux (Sınırsız ve GitHub'da çalışır)
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k resolution, photorealistic, cinematic")
    seed = random.randint(1, 1000000)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def main_job():
    # A) İçerik
    data = icerik_uret()
    if not data: return

    # B) Resimler
    resim_listesi = []
    print("📸 10 Resim hazırlanıyor (GitHub Sunucuda)...")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            time.sleep(2) 
    
    if len(resim_listesi) < 2:
        print("❌ Yeterli resim çizilemedi.")
        return

    # C) Paylaşım
    print(f"🚀 {len(resim_listesi)} resim Instagram'a yükleniyor...")
    cl = Client()
    
    try:
        # GitHub Secrets'taki Session ile giriş
        if INSTA_SESSION:
            try:
                print("🎫 Session ile giriliyor...")
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                print("⚠️ Session geçersiz, şifreyle deneniyor...")
                cl.login(INSTA_USER, INSTA_PASS)
        else:
            print("🔑 Şifre ile giriliyor...")
            cl.login(INSTA_USER, INSTA_PASS)

        print("✅ Giriş Başarılı!")

        cl.album_upload(
            paths=resim_listesi,
            caption=f"📢 {data['baslik']}\n\n{data['aciklama']}"
        )
        print("🎉 TEBRİKLER! GÖNDERİ PAYLAŞILDI!")
        
        # Temizlik
        for r in resim_listesi:
            if os.path.exists(r): os.remove(r)
            
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
