import tweepy
import os
import time
import json
import random
import requests
import google.generativeai as genai

# --- ŞİFRELER ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- HF TOKEN LİSTESİ (Ayrı Hesaplar Varsa Süper!) ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'), os.environ.get('HF_TOKEN_1'), os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3'), os.environ.get('HF_TOKEN_4'), os.environ.get('HF_TOKEN_5'),
    os.environ.get('HF_TOKEN_6'), os.environ.get('HF_TOKEN_7'), os.environ.get('HF_TOKEN_8'),
    os.environ.get('HF_TOKEN_9')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t]

# --- REPLICATE FALLBACK (Yeni Token Ekle!) ---
REPLICATE_TOKEN = os.environ.get('REPLICATE_TOKEN')  # replicate.com'dan al, free kredi var
REPLICATE_URL = "https://api.replicate.com/v1/predictions"
REPLICATE_MODEL = "black-forest-labs/flux-schnell"  # Hızlı ve ücretsiz dostu

# --- GEMINI AYARLARI ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- HF API (FLUX) ---
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

def get_autonomous_idea():
    print("🧠 Gemini sanat yönetmeni modunda...")
    
    prompt_emir = """
    Sen benim kişisel dijital sanat asistanımsın. Twitter hesabım için 'Günün Duvar Kağıdı'nı tasarlıyorsun.
    
    Görevin:
    1. Minimalist Doğa, Cyberpunk, Uzay, Sürrealizm veya Estetik Geometri konularından birini seç.
    2. Benzersiz, çok havalı ve 8K kalitesinde duracak bir sahne kurgula.
    
    Bana SADECE şu JSON formatında cevap ver:
    {
      "caption": "Twitter için İngilizce, kısa, havalı, emojili bir açıklama. Hashtagler ekle (#Minimalist #Wallpaper #Art #4K #Aesthetic).",
      "image_prompt": "Resmi çizecek yapay zeka için İNGİLİZCE prompt. Şunları MUTLAKA ekle: 'minimalist, clean lines, vertical wallpaper, highly detailed, 8k resolution, masterpiece, cinematic lighting, sharp focus, beautiful composition --no text, no watermark'."
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"✅ Fikir Bulundu: {data['caption'][:50]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu kullanılıyor.")
        return {
            "caption": "Endless horizon at sunset 🌅 Minimalist vibes\n\n#Wallpaper #Minimalist #Art #Aesthetic",
            "image_prompt": "minimalist endless ocean sunset, single boat silhouette, warm colors, vertical wallpaper, 8k, masterpiece, cinematic lighting --no text"
        }

def query_huggingface(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=180)
    return response

def generate_with_replicate(prompt):
    if not REPLICATE_TOKEN:
        print("❌ Replicate token yok! replicate.com'dan al.")
        return False
    
    print("🔄 HF başarısız, Replicate'e geçiliyor...")
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "1f208f8c8705b9c1389a20dae6d317b9873dacfb9f8236a24d1e57c68e2d1b9e",  # Flux Schnell versiyonu
        "input": {
            "prompt": prompt + ", vertical wallpaper, 8k, detailed",
            "aspect_ratio": "9:16",  # Dikey için
            "output_format": "jpg",
            "num_outputs": 1,
            "num_inference_steps": 4
        }
    }
    
    try:
        response = requests.post(REPLICATE_URL, headers=headers, json=data)
        if response.status_code == 201:
            pred_id = response.json()['id']
            # Poll for result
            while True:
                poll = requests.get(f"{REPLICATE_URL}/{pred_id}", headers=headers)
                if poll.status_code == 200 and poll.json().get('status') == 'succeeded':
                    img_url = poll.json()['output'][0]
                    img_data = requests.get(img_url).content
                    with open("tweet_image.jpg", "wb") as f:
                        f.write(img_data)
                    print("✅ Replicate ile RESİM ÇİZİLDİ!")
                    return True
                elif poll.json().get('status') == 'failed':
                    print(f"❌ Replicate hatası: {poll.json()}")
                    return False
                time.sleep(5)
        else:
            print(f"❌ Replicate hata: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Replicate bağlantı hatası: {e}")
        return False

def generate_image_raw(prompt):
    if not TOKEN_LISTESI:
        print("❌ HF token yok, direkt Replicate dene.")
        return generate_with_replicate(prompt)
    
    random.shuffle(TOKEN_LISTESI)
    
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 {i+1}/{len(TOKEN_LISTESI)} HF token deneniyor...")
        
        payload = {
            "inputs": prompt + ", vertical phone wallpaper, ultra detailed, high quality",
            "parameters": {
                "negative_prompt": "text, watermark, blurry, low quality, deformed",
                "width": 512,
                "height": 768,
                "num_inference_steps": 4,
                "guidance_scale": 3.5
            }
        }
        
        for attempt in range(3):
            try:
                response = query_huggingface(payload, token)
                
                if response.status_code == 503:
                    wait = response.json().get("estimated_time", 30)
                    print(f"💤 HF busy... {wait + 20} sn bekle (Deneme {attempt+1}/3)")
                    time.sleep(wait + 20)
                    continue
                
                if response.status_code == 200:
                    with open("tweet_image.jpg", "wb") as f:
                        f.write(response.content)
                    print(f"✅ HF ile RESİM ÇİZİLDİ! ({i+1}. token)")
                    return True
                
                elif response.status_code in [402, 429] or 'quota' in response.text.lower() or 'exceeded' in response.text.lower() or 'rate' in response.text.lower():
                    print(f"🚫 HF quota/rate limit ({response.status_code})! Bu tokenı skip, Replicate'e geçiliyor...")
                    return generate_with_replicate(prompt)  # Direkt Replicate'e atla
                
                else:
                    print(f"❌ HF Hata {response.status_code}: {response.text[:100]}")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"❌ HF Bağlantı hatası: {e}")
                time.sleep(10)
        
        print(f"⏭️ {i+1}. HF token skip edildi.")
    
    print("🚨 HF TÜMÜ BAŞARISIZ! Replicate fallback deneniyor...")
    return generate_with_replicate(prompt)

def post_tweet():
    idea = get_autonomous_idea()
    
    if generate_image_raw(idea['image_prompt']):
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
        print("❌ Resim çizilemedi. HF quota/IP sorunu – Replicate token ekle veya Pro al. Yarın (1 Aralık) resetlenir!")

if __name__ == "__main__":
    post_tweet()