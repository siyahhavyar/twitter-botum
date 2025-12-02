import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy

# TÜM KEYLER GİTHUB SECRETS'TEN GELİYOR
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
PIXELCUT_KEY    = os.getenv("PIXELCUT_API_KEY")
DEEPAI_KEY      = os.getenv("DEEPAI_API_KEY", "quickstart-QUdJIGlzIGNvbWluZy4uLi4K")  # Gerçek key'i secrets'e koy

# Eksik key varsa hemen çıksın
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","PIXELCUT_API_KEY"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')  # Güncel model
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → Flux/DeepAI için ultra detaylı prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", 8k, ultra detailed, high resolution 1024x1024, masterpiece"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "cyberpunk city night rain reflections, ultra detailed, 8k, high resolution"
        caption = "Neon rain vibes"
    return prompt, caption

# DEEPAI → HD NATİVE (Düzeltilmiş: Form data, error handling)
def deepai_image(prompt):
    print("DeepAI HD resim üretiyor...")
    url = "https://api.deepai.org/api/text2img"
    headers = {"api-key": DEEPAI_KEY}
    data = {"text": prompt}  # Form data olarak (JSON değil!)
    try:
        r = requests.post(url, headers=headers, data=data, timeout=90)
        print(f"DeepAI status: {r.status_code}")  # Debug için
        if r.status_code == 200:
            result = r.json()
            img_url = result.get("output_url")
            if img_url:
                img_bytes = requests.get(img_url, timeout=60).content
                if len(img_bytes) > 10000:  # Min boyut kontrolü
                    print("DeepAI resim hazır! (512x512 native, prompt HD optimizasyonlu)")
                    return img_bytes
            else:
                print("DeepAI: output_url yok")
        else:
            print(f"DeepAI hata ({r.status_code}): {r.text[:200]}")  # Kısa error log
    except Exception as e:
        print(f"DeepAI exception: {e}")
    return None

# FALLBACK: POLLİNATİONS (Eğer DeepAI patlarsa)
def pollinations_fallback(prompt):
    print("Fallback: Pollinations ile resim üretiliyor...")
    url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?model=flux-realism&width=768&height=1344&nologo=true&enhance=true&seed={random.randint(1,999999)}"
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 50000:
            print("Pollinations fallback başarılı!")
            return r.content
    except: pass
    return None

# PIXELCUT → 4K UPSCALE
def pixelcut_4k(img_bytes):
    print("Pixelcut 4x upscale → Gerçek 4K...")
    try:
        r = requests.post("https://api.pixelcut.ai/v1/image-upscaler/upscale",
            json={"image": base64.b64encode(img_bytes).decode(), "scale": 4},
            headers={"Authorization": f"Bearer {PIXELCUT_KEY}", "Content-Type": "application/json"},
            timeout=120
        )
        if r.status_code == 200:
            url = r.json().get("result_url")
            if url:
                return requests.get(url, timeout=60).content
        else:
            print(f"Pixelcut hata: {r.status_code}")
    except: pass
    return None

# TWEET
def tweet(img_bytes, text):
    fn = "wall.jpg"
    with open(fn, "wb") as f:
        f.write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=text + " #AIArt #4K #Wallpaper", media_ids=[media.media_id])
    print("TWEET ATILDI!")
    os.remove(fn)

# ANA
if __name__ == "__main__":
    print("\nDEEPAI + PIXELCUT 4K BOT ÇALIŞIYOR\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:120]}...")
    print(f"Caption: {caption}\n")

    img = deepai_image(prompt)
    if not img:
        img = pollinations_fallback(prompt)
        if not img:
            print("Tüm kaynaklar başarısız, çıkılıyor.")
            exit(1)

    final = pixelcut_4k(img) or img
    tweet(final, caption)
