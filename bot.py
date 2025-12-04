import tweepy
import os
import requests
import json
from datetime import datetime
import random
import time

# ---------------------------------------------------
#  ENV DEĞİŞKENLERİ (GitHub Actions veya Replit)
# ---------------------------------------------------
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

PERCHANCE_URL = os.environ["PERCHANCE_URL"]      # ÖRN: https://yourperchancemodel.perchance.org/api
DEEPAI_KEY = os.environ["DEEPAI_KEY"]            # 4K Upscaler Key (deepai.org)

# ---------------------------------------------------
#  TWITTER API BAĞLANTI
# ---------------------------------------------------
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# ---------------------------------------------------
# 1) PERCHANCE'TEN FİKİR + RESİM URL AL
# ---------------------------------------------------
def get_image_from_perchance():
    try:
        print("🎨 Perchance yeni resim oluşturuyor...")

        response = requests.get(PERCHANCE_URL, timeout=30)
        data = response.json()

        caption = data.get("caption", "Aesthetic Wallpaper ✨")
        image_url = data.get("image", None)

        if not image_url:
            print("❌ Perchance resim döndürmedi!")
            return None, None

        print("✅ Perchance tamam:", caption)
        return caption, image_url

    except Exception as e:
        print("❌ Perchance Hatası:", e)
        return None, None

# ---------------------------------------------------
# 2) GÖRSELİ 4K UPSCALE ET  (DeepAI SRGAN)
# ---------------------------------------------------
def upscale_image(image_url):
    print("⬆️ 4K Upscale başlıyor...")

    try:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            data={"image": image_url},
            headers={"api-key": DEEPAI_KEY},
            timeout=60
        ).json()

        upscaled = response.get("output_url")
        if upscaled:
            print("✅ 4K Upscale tamamlandı!")
            return upscaled
        else:
            print("⚠️ Upscale yapılamadı, orijinal resim kullanılacak.")
            return image_url
    except Exception as e:
        print("❌ Upscale Hatası:", e)
        return image_url

# ---------------------------------------------------
# 3) TWITTER'A FOTOĞRAFLI TWEET AT
# ---------------------------------------------------
def tweet_wallpaper():
    print("🚀 Tweet hazırlığı başlıyor...")

    caption, image_url = get_image_from_perchance()

    if not image_url:
        print("⛔ Tweet iptal edildi. Resim yok.")
        return

    # 4K upscale
    hd_image = upscale_image(image_url)

    # Dosyayı indir
    print("⬇️ Resim indiriliyor...")
    img_bytes = requests.get(hd_image).content
    file_path = "temp.jpg"
    with open(file_path, "wb") as f:
        f.write(img_bytes)

    # Upload to twitter
    print("📤 Twitter'a yükleniyor...")
    media = api.media_upload(file_path)

    api.update_status(status=caption, media_ids=[media.media_id])

    print("🎉 Tweet gönderildi:", caption)

# ---------------------------------------------------
#  MAIN
# ---------------------------------------------------
if __name__ == "__main__":
    print("🤖 Bot çalıştı.")
    tweet_wallpaper()
