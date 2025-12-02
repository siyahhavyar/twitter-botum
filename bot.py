import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy

# TÜM KEYLER GİTHUB SECRETS'TEN
GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")
PIXELCUT_KEY    = os.getenv("PIXELCUT_API_KEY")
DEEPAI_KEY      = os.getenv("DEEPAI_API_KEY", "quickstart-QUdJIGlzIGNvbWluZy4uLi4K")  # Gerçek key’in varsa secrets’e koy

# Eksik key kontrolü
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET","PIXELCUT_API_KEY"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert","Steampunk City","Aurora Mountains"]
    theme = random.choice(themes)
    resp = model.generate_content(
        f"Tema: {theme}\n"
        "Ultra detaylı, photorealistic bir AI sanat prompt’u yaz + kısa etkileyici tweet caption.\n"
        "Format: PROMPT: [prompt burada] ||| CAPTION: [caption burada]"
    ).text.strip()

    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", ultra detailed, sharp focus, 8k, masterpiece, cinematic lighting"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "futuristic cyberpunk city at night, neon lights, rain reflections, ultra detailed, 8k, masterpiece"
        caption = "Lost in the neon"
    return prompt, caption

# DEEPAI – SADECE BU VAR, PATLARSA TWEET YOK
def deepai_image(prompt):
    print("DeepAI ile HD resim üretiliyor...")
    try:
        r = requests.post(
            "https://api.deepai.org/api/text2img",
            headers={"api-key": DEEPAI_KEY},
            data={"text": prompt},           # Form-data zorunlu!
            timeout=120
        )
        if r.status_code != 200:
            print(f"DeepAI hata kodu: {r.status_code} → {r.text[:200]}")
            return None

        url = r.json().get("output_url")
        if not url:
            print("DeepAI output_url vermedi.")
            return None

        img = requests.get(url, timeout=60).content
        if len(img) < 20000:
            print("DeepAI bozuk/resim çok küçük.")
            return None

        print("DeepAI resim başarıyla alındı! (512x512 → Pixelcut ile 4K olacak)")
        return img

    except Exception as e:
        print(f"DeepAI exception: {e}")
        return None

# PIXELCUT 4K UPSCALE
def pixelcut_4k(img_bytes):
    print("Pixelcut ile 4x upscale → Gerçek 4K yapılıyor...")
    try:
        r = requests.post(
            "https://api.pixelcut.ai/v1/image-upscaler/upscale",
            json={"image": base64.b64encode(img_bytes).decode("utf-8"), "scale": 4},
            headers={"Authorization": f"Bearer {PIXELCUT_KEY}"},
            timeout=120
        )
        if r.status_code == 200:
            result_url = r.json().get("result_url")
            if result_url:
                final = requests.get(result_url, timeout=60).content
                print("4K RESİM HAZIR!")
                return final
        else:
            print(f"Pixelcut hata: {r.status_code}")
    except Exception as e:
        print(f"Pixelcut exception: {e}")
    return None

# TWEET
def tweet(img_bytes, caption):
    fn = "4k_wallpaper.jpg"
    with open(fn, "wb") as f:
        f.write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    client.create_tweet(text=caption + " #AIArt #4K #Wallpaper", media_ids=[media.media_id])
    print("TWEET BAŞARIYLA ATILDI!")
    os.remove(fn)

# ANA PROGRAM – POLLİNATİONS YOK!
if __name__ == "__main__":
    print("\nDEEPAI + PIXELCUT 4K BOT ÇALIŞIYOR (Pollinations yasaklandı!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt[:150]}...")
    print(f"Caption: {caption}\n")

    img = deepai_image(prompt)
    if not img:
        print("DeepAI resim üretemedi → Tweet atılmadı (kalite düşürmek yok!)")
        exit(1)

    final_img = pixelcut_4k(img) or img  # Pixelcut patlarsa bile DeepAI’nin temiz HD’si gider
    tweet(final_img, caption)
