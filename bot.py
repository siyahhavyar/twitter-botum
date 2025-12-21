import os
import time
import requests
import tweepy
import random
import urllib.parse
# google.generativeai YERİNE YENİ PAKET (eğer kullanıyorsan)
try:
    import google.genai as genai  # Yeni resmi paket
except ImportError:
    genai = None  # Eğer yüklü değilse, Gemini devre dışı kalır (Groq varsa sorun yok)

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
HORDE_KEY     = os.getenv("HORDE_API_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# Anonim Mod Kontrolü
if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Horde Key yok, Anonim mod (Yavaş olabilir).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# YENİ: TWITTER API İLE GLOBAL TREND HASHTAG ÇEK
# -----------------------------
def get_current_trending_hashtag():
    try:
        print("🌍 Global trend hashtag çekiliyor (Twitter API ile)...", flush=True)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        
        # WOEID=1 → Dünya geneli trendler
        trends = api.get_place_trends(1)  # 1 = Worldwide
        trend_list = trends[0]['trends']
        
        # Hashtag olanları filtrele, volume'u yüksek olanları tercih et
        hashtag_trends = [t['name'] for t in trend_list if t['name'].startswith('#') and t['tweet_volume'] is not None]
        if not hashtag_trends:
            hashtag_trends = [t['name'] for t in trend_list if t['name'].startswith('#')]
        
        if hashtag_trends:
            selected = random.choice(hashtag_trends[:5])  # En popüler ilk 5'ten biri
            print(f"✅ Bugünün trend hashtag'i: {selected}", flush=True)
            return selected
        else:
            return "#Art"
    except Exception as e:
        print(f"⚠️ Trend çekilemedi: {e} → Fallback #Art", flush=True)
        return "#Art"

# -----------------------------
# 1. FİKİR ÜRETİCİ (MİNİMALİST SANATÇI MODU)
# -----------------------------
def get_idea_ultimate():
    print("🧠 Yapay Zeka sanatçı koltuğuna oturuyor ve derin derin düşünüyor...", flush=True)
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    instruction_prompt = f"""
    You are an independent visionary mobile wallpaper artist with a strong personal aesthetic.
    Today's date and time: {current_timestamp}
    
    You have complete creative freedom. No one is giving you a theme, style, or direction.
    
    Your signature style tends toward minimalism: clean compositions, negative space, subtle gradients, simple forms, emotional resonance through restraint.
    You love quiet beauty, elegance, and concepts that feel timeless yet contemporary.
    
    Every single artwork you create is unique — you never repeat yourself.
    
    Right now, sit in silence for a moment and create something new from scratch.
    Ask yourself:
    - What subtle emotion do I want to evoke today?
    - What simple visual element could carry deep meaning?
    - How can empty space become the main character?
    
    Output exactly two lines, nothing else:
    PROMPT: <A highly detailed, original English description of your minimalist vision. Include composition, colors, lighting, mood. Do not use words like "masterpiece", "highly detailed", "8k", "stunning">
    CAPTION: <A short, poetic, artistic English tweet caption (max 140 chars) that feels like something a real artist would write. Do NOT include any hashtags here>
    """

    # --- PLAN A: GROQ ---
    if GROQ_KEY:
        try:
            print("🧠 Groq sessizce hayal kuruyor...", flush=True)
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
                    print("✅ Groq harika bir minimalist vizyon yarattı!", flush=True)
                    return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"Groq hatası: {e}", flush=True)

    # --- PLAN B: GEMINI (Yeni paket ile) ---
    if GEMINI_KEY and genai is not None:
        try:
            print("🧠 Gemini minimalist bir dünya tasarlıyor...", flush=True)
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
                print("✅ Gemini derin bir minimalist eser üretti!", flush=True)
                return prompt_line[7:].strip(), caption_line[8:].strip()
        except Exception as e:
            print(f"Gemini hatası: {e}", flush=True)

    # --- SON ÇARE: FALLBACK ---
    print("🧠 Kendi iç dünyama dönüyorum...", flush=True)
    minimalist_concepts = [
        "A vast empty space in soft off-white with a single delicate curved line in pale rose descending from the top",
        "Deep charcoal background with a faint circular gradient in muted teal emerging from the center",
        "Subtle horizontal bands of warm sand and cool mist, separated by generous negative space",
        "Pure midnight blue canvas interrupted only by a tiny glowing amber dot near the bottom edge",
        "Endless pale gray expanse with one barely visible thin golden arc in the upper third"
    ]
    prompt = random.choice(minimalist_concepts)
    captions = [
        "less is more.",
        "silence speaks",
        "breathing room",
        "quiet presence",
        "the beauty of restraint"
    ]
    caption = random.choice(captions)
    return prompt, caption


def prepare_final_prompt(raw_prompt):
    return f"{raw_prompt}, minimalist composition, vertical phone wallpaper, 9:21 aspect ratio, soft lighting, subtle colors, clean design, negative space"


# -----------------------------
# 2. AI HORDE (değişmedi)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    
    current_key = HORDE_KEY if HORDE_KEY else "0000000000"
    headers = {"apikey": current_key, "Client-Agent": "MyTwitterBot:v5.0"}
    
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
            print(f"⚠️ Yüksek Kalite Reddedildi: {error_msg[:100]}...", flush=True)
            
            if "Kudos" in error_msg or "demand" in error_msg or req.status_code == 503:
                print("🔄 Sunucular dolu! Ekonomi Modu...", flush=True)
                payload_high["params"]["post_processing"] = []
                payload_high["params"]["steps"] = 20
                
                req = requests.post(generate_url, json=payload_high, headers=headers, timeout=30)
                if req.status_code != 202:
                    return None
            else:
                return None

        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...", flush=True)
        
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}", flush=True)
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
                if len(generations) > 0:
                    print("⬇️ Resim indiriliyor...", flush=True)
                    img_url = generations[0]['img']
                    return requests.get(img_url, timeout=60).content
            
            wait_t = status_data.get('wait_time', '?')
            queue = status_data.get('queue_position', '?')
            print(f"⏳ Geçen: {wait_time}sn | Sıra: {queue} | Tahmini: {wait_t}sn", flush=True)
        except Exception:
            time.sleep(5) 

    print("⚠️ Zaman aşımı.", flush=True)
    return None

# -----------------------------
# 3. TWITTER POST + HASHTAG
# -----------------------------
def post_to_twitter(img_bytes, caption):
    trending_tag = get_current_trending_hashtag()
    art_hashtags = "#Minimalism #AbstractArt #PhoneWallpaper #DigitalArt #Wallpaper"
    final_caption = f"{caption} {art_hashtags} {trending_tag}"
    
    if len(final_caption) > 280:
        final_caption = final_caption[:277] + "..."
    
    print(f"📝 Final Tweet: {final_caption}", flush=True)
    
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
        print("🐦 TWEET BAŞARIYLA ATILDI!", flush=True)
        return True 
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}", flush=True)
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Bot Başlatılıyor... (MİNİMALİST + GERÇEK ZAMANLI TREND HASHTAG)", flush=True)
    
    prompt, base_caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Yapay Zekanın Bulduğu Konu:", prompt[:100] + ("..." if len(prompt) > 100 else ""), flush=True)
    print("📝 Temel Caption:", base_caption, flush=True)
    print("------------------------------------------------", flush=True)

    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n🔄 DENEME: {deneme_sayisi}", flush=True)
        
        try:
            img = try_generate_image(prompt)
            if img:
                if post_to_twitter(img, base_caption):
                    basari = True 
                    print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
                else:
                    print("⚠️ Resim var ama Tweet atılamadı.", flush=True)
            else:
                print("⚠️ Resim çizilemedi.", flush=True)
                
        except Exception as e:
            print(f"⚠️ Genel Hata: {e}", flush=True)
        
        if not basari:
            print("💤 3 dakika bekleyip tekrar deniyorum...", flush=True)
            time.sleep(180) 
            deneme_sayisi += 1
