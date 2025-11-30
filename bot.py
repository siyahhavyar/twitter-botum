import tweepy
import os
import time
import json
import base64
import io
from PIL import Image
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- GEMINI AYARLARI (Resim Üretimi İçin Güncel Model) ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-image')  # Resim desteği olan model (2025 güncel)

def get_autonomous_idea_and_image():
    print("🧠 Gemini sanat yönetmeni modunda... (Fikir + Resim Üretimi)")
    
    prompt_emir = """
    Sen benim kişisel dijital sanat asistanımsın. Twitter hesabım için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    Görevin:
    1. Minimalist Doğa, Cyberpunk, Uzay, Sürrealizm veya Estetik Geometri konularından birini seç.
    2. Benzersiz, çok havalı ve 8K kalitesinde duracak bir sahne kurgula.
    
    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı, emojili bir açıklama. Hashtagler ekle (#Minimalist #Wallpaper #Art #4K #Aesthetic).",
      "image_prompt": "Resmi çizecek AI için İNGİLİZCE prompt. Şunları MUTLAKA ekle: 'minimalist, clean lines, vertical wallpaper, highly detailed, 8k resolution, masterpiece, cinematic lighting, sharp focus, beautiful composition --no text, no watermark'."
    }
    """
    
    try:
        # Fikir üret (sadece text)
        response_idea = model.generate_content(prompt_emir)
        text = response_idea.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"✅ Fikir Bulundu: {data['caption'][:50]}...")
        
        # Resim üret (prompt'tan)
        image_prompt = f"Generate an image of: {data['image_prompt']}, aspect ratio 9:16 for vertical wallpaper"
        response_image = model.generate_content(
            image_prompt,
            generation_config=genai.types.GenerationConfig(
                response_modalities=["TEXT", "IMAGE"],  # Resim modu
                image_config=genai.types.ImageConfig(aspect_ratio="9:16", image_size="1024x1792")  # Dikey, yüksek çözünürlük
            )
        )
        
        # Resmi kaydet
        for part in response_image.candidates[0].content.parts:
            if part.inline_data:
                img_data = base64.b64decode(part.inline_data.data)
                image = Image.open(io.BytesIO(img_data))
                image.save("tweet_image.jpg")
                print("✅ Resim Gemini Tarafından Üretildi!")
                return data
        
        # Eğer resim gelmediyse fallback
        print("⚠️ Resim gelmedi, yedek kullanılıyor.")
        return {
            "caption": "Endless horizon at sunset 🌅 Minimalist vibes\n\n#Wallpaper #Minimalist #Art #Aesthetic",
            "image_prompt": "minimalist endless ocean sunset, single boat silhouette, warm colors, vertical wallpaper, 8k, masterpiece, cinematic lighting --no text"
        }
        
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek kullanılıyor.")
        # Yedek resim için basit bir generate dene
        try:
            response_fallback = model.generate_content(
                "Generate a minimalist vertical wallpaper of an endless ocean sunset, 9:16 aspect ratio, 8k",
                generation_config=genai.types.GenerationConfig(response_modalities=["IMAGE"])
            )
            for part in response_fallback.candidates[0].content.parts:
                if part.inline_data:
                    img_data = base64.b64decode(part.inline_data.data)
                    Image.open(io.BytesIO(img_data)).save("tweet_image.jpg")
                    print("✅ Yedek Resim Üretildi!")
        except:
            print("❌ Resim üretilemedi, manuel ekle.")
        return {
            "caption": "Endless horizon at sunset 🌅 Minimalist vibes\n\n#Wallpaper #Minimalist #Art #Aesthetic"
        }

def post_tweet():
    idea = get_autonomous_idea_and_image()
    
    if os.path.exists("tweet_image.jpg"):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(
                consumer_key=api_key, consumer_secret=api_secret,
                access_token=access_token, access_token_secret=access_secret
            )

            media = api.media_upload("tweet_image.jpg")
            client.create_tweet(text=idea['caption'], media_ids=[media.media_id])
            print("✅ TWEET BAŞARIYLA ATILDI! 🎉")
            
        except Exception as e:
            print(f"❌ Twitter hatası: {e}")
    else:
        print("❌ Resim dosyası yok, tweet atılmadı. Gemini quota'nı kontrol et.")

if __name__ == "__main__":
    post_tweet()