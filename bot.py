import os
import time
import requests
import tweepy
import random
import urllib.parse
import google.generativeai as genai
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

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Key yok, Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Key aktif! ({HORDE_KEY[:4]}***)", flush=True)

# -----------------------------
# 1. FİKİR ÜRETİCİ (GÜVENLİ LİSTE YÖNTEMİ)
# -----------------------------
def get_idea_ultimate():
    
    # --- GÜVENLİ TARZ LİSTESİ ---
    styles_map = {
        "Minimalism": "Minimalist digital art, simple geometry, vast negative space, soothing colors",
        "Abstract": "Abstract fluid art, swirling paint, colorful patterns, no specific objects",
        "Cyberpunk": "Futuristic neon city lights, blurry bokeh effect, synthwave colors, abstract tech",
        "Pop Art": "Vibrant pop art pattern, halftone dots, comic book style background, colorful",
        "Low Poly": "Low poly landscape, geometric mountains, pastel colors, 3d render style",
        "Neon": "Glowing neon lines, dark background, abstract light trails, long exposure",
        "Gradient": "Smooth color gradients, aura aesthetic, grainy texture, noise effect",
        "Liquid": "Liquid metal texture, chrome reflection, iridescent colors, 3d render",
        "Glass": "Frosted glass texture, blurred shapes behind glass, soft lighting, minimalism"
    }
    
    # %60 Minimalizm, %40 Diğerleri
    keys = list(styles_map.keys())
    weights = [60 if k == "Minimalism" else 5 for k in keys]
    
    chosen_key = random.choices(keys, weights=weights, k=1)[0]
    safe_prompt_base = styles_map[chosen_key]
    
    print(f"🎨 SEÇİLEN GÜVENLİ TARZ: {chosen_key.upper()}", flush=True)

    # Gemini'ye sadece "Renk ve Detay" eklemesini söylüyoruz. Konu seçtirtmiyoruz.
    instruction_prompt = f"""
    Act as an AI Art Curator.
    BASE STYLE: {safe_prompt_base}
    
    TASK: Add 2-3 safe adjectives to describe colors or mood (e.g. "blue and gold", "peaceful", "energetic").
    DO NOT change the subject. DO NOT mention people, animals, or specific places.
    KEEP IT ABSTRACT AND SIMPLE.
    
    Return exactly two lines:
    PROMPT: <The full combined prompt>
    CAPTION: <Tweet caption with hashtags>
    """

    # --- PLAN A: GEMINI ---
    if GEMINI_KEY:
        try:
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=0.9) # Düşük yaratıcılık = Daha güvenli
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            
            response = model.generate_content(instruction_prompt)
            parts = response.text.split("CAPTION:")
            
            if len(parts) >= 2:
                print("✅ Gemini Başarılı!", flush=True)
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    # --- PLAN B: GROQ ---
    if GROQ_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile", 
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 0.8
            }
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    print("✅ Groq Başarılı!", flush=True)
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    # YEDEK (Hiçbiri çalışmazsa en güvenli prompt)
    return f"{safe_prompt_base}, 8k resolution", f"Art of the day ({chosen_key}) #AIArt #Wallpaper"


def prepare_final_prompt(raw_prompt):
    # BURASI ÇOK ÖNEMLİ: "No children" gibi kelimeleri SİLDİK.
    # Çünkü bazen filtreler "children" kelimesini görünce ne dediğine bakmadan engelliyor.
    # Sadece pozitif ve güvenli kelimeler kullanıyoruz.
    return (
        f"{raw_prompt}, "
        "vertical wallpaper, 9:21 aspect ratio, full screen, "
        "high quality, aesthetic, clean look"
    )

# -----------------------------
# 2. AI HORDE (RESİM ÇİZİCİ)
# -----------------------------
def try_generate_image(prompt_text):
    final_prompt = prepare_final_prompt(prompt_text)
    print("🎨 AI Horde → Resim çiziliyor...", flush=True)
    print(f"ℹ️ Güvenli Prompt: {final_prompt[:60]}...", flush=True)
    
    unique_seed = str(random.randint(1, 9999999999))
    
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {
        "apikey": HORDE_KEY,
        "Client-Agent": "MyTwitterBot:v20.0-WhitelistMode"
    }
    
    payload = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7,               
            "width": 640,    
            "height": 1408,               
            "steps": 28,                 
            "seed": unique_seed,
            "post_processing": ["RealESRGAN_x4plus"] 
        },
        "nsfw": False,
        "censor_nsfw": True,
        # Bu model daha soyut ve sanatsal işlerde iyidir, filtreye daha az takılır
        "models": ["AlbedoBase XL (SDXL)"] 
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers, timeout=30)
        
        # Filtreye takılırsa (400 Hatası)
        if req.status_code == 400 or "CSAN" in req.text or "filter" in req.text.lower():
             print("🚨 FİLTRE UYARISI! Prompt tamamen değiştiriliyor...", flush=True)
             # En güvenli, risksiz prompt
             payload["prompt"] = "Abstract colorful gradient background, soft texture, 8k wallpaper"
             req = requests.post(generate_url, json=payload, headers=headers, timeout=30)
        
        if req.status_code != 202:
            print(f"⚠️ Sunucu Hatası: {req.text}", flush=True)
            return None 
        
        task_id = req.json()['id']
        print(f"✅ Görev alındı ID: {task_id}. Bekleniyor...", flush=True)
    except Exception as e:
        print(f"⚠️ Bağlantı Hatası: {e}", flush=True)
        return None

    wait_time = 0
    max_wait = 2700 
    
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
                else:
                    print("⚠️ Horde boş yanıt döndü.", flush=True)
                    return None
            
            wait_t = status_data.get('wait_time', '?')
            print(f"⏳ Geçen: {wait_time}sn | Tahmini: {wait_t}sn", flush=True)
        except Exception as e:
            time.sleep(5) 

    print("⚠️ Zaman aşımı.", flush=True)
    return None

# -----------------------------
# 3. TWITTER POST
# -----------------------------
def post_to_twitter(img_bytes, caption):
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
        
        client.create_tweet(text=caption, media_ids=[media.media_id])
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
    print("🚀 Bot Başlatılıyor... (Whitelist Mode - %100 Güvenli)", flush=True)
    
    prompt, caption = get_idea_ultimate()
    print("------------------------------------------------", flush=True)
    print("🎯 Seçilen Konu:", prompt[:100] + "...", flush=True)
    
    basari = False
    deneme_sayisi = 1
    
    while not basari:
        print(f"\n🔄 RESİM ÇİZİM DENEMESİ: {deneme_sayisi}", flush=True)
        img = try_generate_image(prompt)
        
        if img:
            if post_to_twitter(img, caption):
                basari = True 
                print("🎉 Görev Başarılı! Bot kapanıyor.", flush=True)
            else:
                print("⚠️ Resim var ama Tweet atılamadı.", flush=True)
                break 
        else:
            print("⚠️ Resim çizilemedi.", flush=True)
            if deneme_sayisi >= 3:
                print("❌ Deneme hakkı bitti.")
                break
            
            time.sleep(60) 
            deneme_sayisi += 1
        
