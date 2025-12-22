import os
import time
import requests
import tweepy
import random
import urllib.parse
# google-genai için güvenli import
try:
    import google.genai as genai
except ImportError:
    genai = None

from datetime import datetime
from tweepy import OAuthHandler, API, Client

# -----------------------------
# ENV KEYS
# -----------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# -----------------------------
# HORDE KEYS (Senin verdiğin 7 key)
# -----------------------------
HORDE_KEYS = [
    "cQ9Kty7vhFWfD8nddDOq7Q",
    "ceIr0GFCjybUk_3ItTju0w",
    "_UZ8x88JEw4_zkIVI1GkpQ",
    "8PbI2lLTICOUMLE4gKzb0w",
    "SwxAZZWFvruz8ugHkFJV5w",
    "AEFG4kHNWHKPCWvZlEjVUg",
    "Q-zqB1m-7kjc5pywX52uKg"
]

HORDE_KEY = "0000000000"  # Varsayılan anonim
print("🔑 Horde key'leri test ediliyor...", flush=True)

for key in HORDE_KEYS:
    try:
        test_url = "https://stablehorde.net/api/v2/find_user"
        headers = {
            "apikey": key,
            "Client-Agent": "MyTwitterBot:v5.0"
        }
        response = requests.get(test_url, headers=headers, timeout=15)
        
        print(f"   → Test: {key[:8]}... → Status: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("id")
            username = data.get("username", "Bilinmiyor")
            kudos = data.get("kudos", 0)
            
            if user_id and user_id != 0:  # Registered kullanıcı
                HORDE_KEY = key
                print(f"✅ ÇALIŞAN KEY BULUNDU: {key[:8]}... (User: {username}, Kudos: {kudos})", flush=True)
                break
            else:
                print(f"   → Anonim/kısıtlı hesap (ID: {user_id})", flush=True)
        else:
            print(f"   → Geçersiz yanıt (Kod: {response.status_code})", flush=True)
    except Exception as e:
        print(f"   → Bağlantı hatası: {e}", flush=True)
        continue

if HORDE_KEY == "0000000000":
    print("⚠️ Hiçbir key registered olarak doğrulanamadı, anonim modda devam ediliyor (daha yavaş).", flush=True)
else:
    print(f"🚀 Horde Key aktif ve registered! Hızlı generation bekleniyor.", flush=True)

# -----------------------------
# YENİ: TWITTER API İLE GLOBAL TREND HASHTAG
# -----------------------------
def get_current_trending_hashtag():
    try:
        print("🌍 Global trend hashtag çekiliyor...", flush=True)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        
        trends = api.get_place_trends(1)  # 1 = Worldwide
        trend_list = trends[0]['trends']
        
        hashtag_trends = [t['name'] for t in trend_list if t['name'].startswith('#')]
        
        if hashtag_trends:
            selected = random.choice(hashtag_trends[:5])
            print(f"✅ Trend hashtag: {selected}", flush=True)
            return selected
        else:
            return "#Art"
    except Exception as e:
        print(f"⚠️ Trend çekilemedi: {e} → #Art", flush=True)
        return "#Art"

# -----------------------------
# 1. FİKİR ÜRETİCİ (MİNİMALİST SANATÇI)
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka sanatçı koltuğuna oturuyor...", flush=True)
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    instruction_prompt = f"""
    You are an independent visionary mobile wallpaper artist with a strong personal aesthetic.
    Today's date and time: {current_timestamp}
    
    You have complete creative freedom.
    
    Your signature style tends toward minimalism: clean compositions, negative space, subtle gradients, simple forms, emotional resonance through restraint.
    You love quiet beauty, elegance, and concepts that feel timeless yet contemporary.
    
    Every single artwork you create is unique.
    
    Output exactly two lines, nothing else:
    PROMPT: <Original English description of your minimalist vision. Include composition, colors, lighting, mood.>
    CAPTION: <Short, poetic, artistic English tweet caption (max 140 chars). No hashtags.>
    """

    if GROQ_KEY:
        try:
            print("🧠 Groq hayal kuruyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.4,
                "top_p": 0.95,
                "max_tokens": 500
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                prompt_line = next((l for l in lines if l.startswith("PROMPT:")), None)
                caption_line = next((l for l in lines if l.startswith("CAPTION:")), None)
                if prompt_line and caption_line:
                    return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"Groq hatası: {e}", flush=True)

    if GEMINI_KEY and genai is not None:
        try:
            print("🧠 Gemini düşünüyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                instruction_prompt,
                generation_config=genai.types.GenerationConfig(temperature=1.3, top_p=0.95, max_output_tokens=500)
            )
            text = response.text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            prompt_line = next((l for l in lines if l.startswith("PROMPT:")), None)
            caption_line = next((l for l in lines if l.startswith("CAPTION:")), None)
            if prompt_line and caption_line:
                return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"Gemini hatası: {e}", flush=True)

    # Fallback
    print("🧠 Fallback minimalist...", flush=True)
    concepts = [
        "A vast empty space in soft off-white with a single delicate curved line in pale rose",
        "Deep charcoal background with a faint circular gradient in muted teal",
        "Subtle horizontal bands of warm sand and cool mist",
        "Pure midnight blue with a tiny glowing amber dot near the bottom",
        "Endless pale gray expanse with one thin golden arc"
    ]
    captions = ["less is more.", "silence speaks", "breathing room", "quiet presence", "the beauty of restraint"]
    return random.choice(concepts), random.choice(captions)

def prepare_final_prompt(raw_prompt):
    return f"{raw_prompt}, minimalist composition, vertical phone wallpaper, 9:21 aspect ratio, soft lighting, subtle colors, clean design, negative space"

# -----------------------------
# 2. AI HORDE GENERATION
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim üretiliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    headers = {"apikey": HORDE_KEY, "Client-Agent": "MyTwitterBot:v5.0"}
    
    payload_high = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7,               
            "width": 640,    
            "height": 1408,               
            "steps": 30,
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"]
        },
        "nsfw": False, "censor_nsfw": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"] 
    }

    try:
        req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
        
        if req.status_code != 202:
            error_msg = req.text
            print(f"⚠️ Yüksek kalite reddedildi: {error_msg[:100]}...", flush=True)
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Ekonomi moduna geçiliyor...", flush=True)
                payload_high["params"]["post_processing"] = []
                payload_high["params"]["steps"] = 20
                req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
                if req.status_code != 202:
                    return None
            else:
                return None

        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}", flush=True)
        
    except Exception as e:
        print(f"⚠️ Bağlantı hatası: {e}", flush=True)
        return None

    wait_time = 0
    max_wait = 1800
    while wait_time < max_wait:
        time.sleep(20)
        wait_time += 20
        try:
            status_url = f"https://stablehorde.net/api/v2/generate/status/{task_id}"
            check = requests.get(status_url, timeout=30)
            status_data = check.json()
            
            if status_data['done']:
                generations = status_data['generations']
                if generations:
                    print("⬇️ Resim indiriliyor...", flush=True)
                    img_url = generations[0]['img']
                    return requests.get(img_url, timeout=60).content
            
            queue = status_data.get('queue_position', '?')
            wait_t = status_data.get('wait_time', '?')
            print(f"⏳ {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn", flush=True)
        except:
            time.sleep(5)

    print("⚠️ Zaman aşımı.", flush=True)
    return None

# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
    trending_tag = get_current_trending_hashtag()
    art_hashtags = "#Minimalism #AbstractArt #PhoneWallpaper #DigitalArt #Wallpaper"
    final_caption = f"{caption} {art_hashtags} {trending_tag}"
    
    if len(final_caption) > 280:
        final_caption = final_caption[:277] + "..."
    
    print(f"📝 Tweet: {final_caption}", flush=True)
    
    filename = "wallpaper_mobile.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    try:
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)
        client = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        client.create_tweet(text=final_caption, media_ids=[media.media_id])
        print("🐦 TWEET ATILDI!", flush=True)
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {e}", flush=True)
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Bot başlatılıyor... (Minimalist Sanatçı + Trend Hashtag)", flush=True)
    
    prompt, base_caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Prompt:", prompt[:100] + ("..." if len(prompt) > 100 else ""), flush=True)
    print("📝 Caption:", base_caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme = 1
    while not basari:
        print(f"\n🔄 Deneme {deneme}", flush=True)
        img = try_generate_image(prompt)
        if img and post_to_twitter(img, base_caption):
            basari = True
            print("🎉 Başarılı! Bot kapanıyor.", flush=True)
        else:
            print("💤 3 dakika bekleniyor...", flush=True)
            time.sleep(180)
            deneme += 1
