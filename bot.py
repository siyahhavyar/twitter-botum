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

# --- 🎨 KARMAŞIK VE ÇEŞİTLİ KONU HAVUZU ---
KONULAR = [
    # SÜRREALİST & İMKANSIZ
    "A city built on the back of a giant flying turtle",
    "A library where books are portals to other worlds, floating",
    "Stairs leading to a door in the clouds",
    "A forest where trees are made of crystal and glass",
    "An hourglass with a whole galaxy inside it",
    "A train traveling through the sky on tracks made of light",
    "Melting clocks in a desert landscape (Dali style)",

    # FÜTÜRİSTİK & CYBERPUNK
    "A futuristic city with vertical gardens and flying vehicles",
    "A cyberpunk street market in the rain with neon signs",
    "An underwater city dome glowing in the deep ocean",
    "A bustling spaceport on a distant planet with alien ships",
    "A robot tending to a complex mechanical garden",
    "A futuristic observatory on a mountain peak looking at a nebula",

    # FANTASTİK & MİTOLOJİK
    "An ancient dragon guarding a hoard of glowing treasure in a cave",
    "A wizard's tower full of magical artifacts and glowing runes",
    "A steampunk airship fleet sailing through the clouds",
    "A mythical phoenix rising from ashes, made of fire and light",
    "An elf village seamlessly integrated into massive ancient trees",
    "A hidden temple in a jungle overgrown with bioluminescent plants",

    # TARİHİ & ALTERNATİF
    "An ancient Roman city but with advanced clockwork technology",
    "A vibrant market in a bustling medieval fantasy city",
    "A samurai duel in a mystical, fog-covered landscape",
    "A pirate ship sailing on a sea of stars instead of water",
    "An Art Deco style metropolis from the 1920s of the future",
    "A detailed alchemist's laboratory filled with strange potions",

    # DOĞA & ATMOSFER (Ama daha dramatik)
    "A dramatic thunderstorm over a jagged mountain range",
    "A mysterious bioluminescent forest at night",
    "A vast desert landscape with strange, towering rock formations",
    "An ancient, gnarled tree of life glowing in a dark forest",
    "A breathtaking aurora borealis reflecting in a frozen lake",
    "A secret garden hidden behind a waterfall",

    # KAVRAMSAL & SOYUT (Korku yok)
    "A visual representation of 'Time' as a complex machine",
    "A dreamscape with floating islands and impossible architecture",
    "A symphony of light and color forming a cosmic structure",
    "A world made entirely of clockwork gears and mechanisms"
]

def get_creative_idea():
    topic = random.choice(KONULAR)
    print(f"🎯 Seçilen Konu: {topic}")
    
    # Gemini'ye "Sıradan olma, Şaşırt, Karmaşık yap" emri
    prompt_emir = f"""
    Sen ödüllü bir dijital sanatçısın. Konu: "{topic}".
    
    ÖNEMLİ KURAL: Asla korku, kan, şiddet veya ürkütücü öğeler kullanma.
    
    Görevin:
    1. Bu konuyu temel alarak, sıradanlıktan uzak, görsel olarak zengin, karmaşık ve düşündürücü bir sahne kurgula.
    2. İzleyiciyi şaşırtacak, detaylarla dolu bir kompozisyon hayal et. Sürrealist veya beklenmedik unsurlar eklemekten çekinme.
    
    2. Bana SADECE şu JSON formatını ver:
    {{
      "caption": "Twitter için İngilizce, konuyu yansıtan havalı, emojili kısa bir açıklama.",
      "image_prompt": "Resim için İNGİLİZCE prompt. Şunları MUTLAKA içersin: 'highly detailed, cinematic lighting, 8k resolution, photorealistic, vertical wallpaper, masterpiece, sharp focus, intricate details'. ASLA 'horror' veya 'scary' kullanma."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {
            "caption": "A Glimpse of the Infinite ✨ \n\n#Surreal #Art #Wallpaper",
            "image_prompt": "A surreal landscape with floating islands and ancient ruins under a nebula sky, cinematic lighting, 8k, photorealistic, vertical, masterpiece, intricate details"
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