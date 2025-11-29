import tweepy
import os
import time
import json
import random
import google.generativeai as genai
from huggingface_hub import InferenceClient

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- YEDEK DEPOLU TOKEN SİSTEMİ ---
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
model = genai.GenerativeModel('gemini-pro')
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

# --- 🎨 TEMİZ VE DESTANSI KONU HAVUZU (Korku Yok!) ---
KONULAR = [
    # BİLİM KURGU & UZAY
    "Futuristic City with Flying Cars", "Astronaut Walking on Mars", 
    "Spaceship Cockpit View of Earth", "Cyberpunk Street with Neon Lights",
    "Giant Mech Robot Protecting City", "Solar System Planets View",
    "Advanced Alien City (Friendly)", "Time Traveler's Machine",
    "Hacker Room with Multiple Screens", "Mars Colony Greenhouse",

    # DOĞA & MANZARA
    "Cozy Hobbit House in Green Forest", "Japanese Temple in Spring (Sakura)",
    "Snowy Mountains at Sunset", "Tropical Island Beach Paradise",
    "Northern Lights (Aurora) over Lake", "Waterfall in a Jungle",
    "Lonely Lighthouse in Calm Sea", "Autumn Road with Orange Leaves",
    "Zen Garden with Bonsai Tree", "Rainy Window City View (Cozy)",

    # FANTASTİK & MASALSI
    "Fairy Tale Castle in Clouds", "Dragon Flying over Mountains (Epic)",
    "Magical Library with Floating Books", "Crystal Cave Glowing Blue",
    "Tree of Life Glowing", "Phoenix Rising (Fire Bird)",
    "Underwater City of Atlantis (Bright)", "Elf Village in Trees",
    "Wizard's Tower (Magical)", "Flying Island in Sky",

    # TARİHİ & EYLEM
    "Viking Ship in Ocean", "Samurai Training in Dojo",
    "Medieval Knight on Horse", "Cowboy Riding in Wild West",
    "Ancient Greek Temple", "Egyptian Pyramids at Sunrise",
    "Retro 80s Arcade Room", "Steampunk Airship in Sky",
    "Old Train Journey through Alps", "Pirate Ship Sailing"
]

def get_creative_idea():
    topic = random.choice(KONULAR)
    print(f"🎯 Seçilen Konu: {topic}")
    
    # Gemini'ye "Korku yapma, Güzel bir sahne yap" emri
    prompt_emir = f"""
    Sen ödüllü bir dijital sanatçısın. Konu: "{topic}".
    
    ÖNEMLİ KURAL: Asla korku, kan, şiddet veya ürkütücü öğeler kullanma. 
    İnsanların "Vay be ne kadar güzel" diyeceği, estetik ve detaylı bir sahne anlat.
    Asla "abstract", "geometry" veya "simple" kelimelerini kullanma.
    
    Görevin:
    1. Bu konuyu al ve çok detaylı, sinematik, fotoğraf gerçekliğinde bir sahne kurgula.
    2. Bana SADECE şu JSON formatını ver:
    
    {{
      "caption": "Twitter için İngilizce, havalı, emojili kısa bir açıklama.",
      "image_prompt": "Resim için İNGİLİZCE prompt. Şunları MUTLAKA içersin: 'highly detailed, cinematic lighting, 8k resolution, photorealistic, vertical wallpaper, masterpiece, sharp focus, beautiful atmosphere'. ASLA 'horror' veya 'scary' kullanma."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {
            "caption": "Peaceful Nature 🌿 \n\n#Nature #Wallpaper #Art",
            "image_prompt": "A beautiful cozy cabin in a green forest, sunlight filtering through trees, cinematic lighting, 8k, photorealistic, vertical, masterpiece"
        }

def generate_image_sdxl(prompt):
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}. Anahtar deneniyor...")
        try:
            client = InferenceClient(model=repo_id, token=token)
            image = client.text_to_image(
                f"{prompt}, vertical wallpaper, aspect ratio 2:3", 
                width=768, height=1344
            )
            image.save("tweet_img.jpg")
            print(f"✅ Resim Çizildi ({i+1}. Anahtar).")
            return True
        except Exception as e:
            print(f"❌ {i+1}. Anahtar Hatası: {e}")
            time.sleep(1)
            
    print("🚨 HATA: Hiçbir anahtar çizemedi.")
    return False

def post_tweet():
    content = get_creative_idea()
    
    if generate_image_sdxl(content['image_prompt']):
        print("🐦 Twitter'a yükleniyor...")
        try:
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)
            client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

            media = api.media_upload(filename="tweet_img.jpg")
            client.create_tweet(text=content['caption'], media_ids=[media.media_id])
            print("✅ TWITTER'DA PAYLAŞILDI!")
            
        except Exception as e:
            print(f"❌ Twitter Hatası: {e}")
    else:
        print("❌ Resim çizilemediği için iptal.")

if __name__ == "__main__":
    post_tweet()