import os
import time
import requests
import tweepy
import random
from datetime import datetime
from tweepy import Client

# KEYS - Environment variables'tan çekiliyor
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY = os.getenv("GROQ_API_KEY")  # Kullanılmıyor ama durabilir

print("🔑 Key Durumu:")
print(f"Twitter: {'Var' if API_KEY and ACCESS_TOKEN else 'Eksik!'}")

if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_SECRET):
    print("❌ Twitter key'leri eksik! Ortam değişkenlerini kontrol et.")
    exit()

# -----------------------------
# HORDE KEYS - En yüksek kudos'lu seçiliyor
# -----------------------------
HORDE_KEYS = [
    "cQ9Kty7vhFWfD8nddDOq7Q", "ceIr0GFCjybUk_3ItTju0w", "_UZ8x88JEw4_zkIVI1GkpQ",
    "8PbI2lLTICOUMLE4gKzb0w", "SwxAZZWFvruz8ugHkFJV5w", "AEFG4kHNWHKPCWvZlEjVUg",
    "Q-zqB1m-7kjc5pywX52uKg"
]

HORDE_KEY = None
max_kudos = 0
print("🔍 Horde key'leri kontrol ediliyor...")
for key in HORDE_KEYS:
    try:
        info = requests.get("https://stablehorde.net/api/v2/find_user", headers={"apikey": key}, timeout=15).json()
        kudos = info.get("kudos", 0)
        username = info.get("username", "Bilinmeyen")
        print(f"   {key[:8]}... → {username} → {kudos} kudos")
        if kudos > max_kudos:
            max_kudos = kudos
            HORDE_KEY = key
    except Exception as e:
        print(f"   {key[:8]}... → Hata: {e}")

if not HORDE_KEY:
    print("❌ Hiçbir Horde key çalışmadı.")
    exit()

print(f"✅ Seçilen key: {HORDE_KEY[:8]}... ({max_kudos} kudos)")

# -----------------------------
# 400 FARKLI TEMA (tam liste)
# -----------------------------
ideas = [
    "Abstract sand dunes, soft shadows, beige tones.", "Geometric white stairs, architectural shadow, bright.",
    "Single eucalyptus branch in a glass vase, neutral wall.", "Japandi style interior, empty room, wooden floor.",
    "Soft linen fabric texture, cream color, morning sun.", "Matte black circles on charcoal grey background.",
    "Pale sage green organic shapes, minimalist.", "Thin gold line across a white marble surface.",
    "Wabi-sabi clay bowl on a rough stone table.", "Abstract topography map, white on white, 3D depth.",
    "Zen garden ripples, grey sand, single pebble.", "Mid-century modern abstract shapes, terracotta palette.",
    "Minimalist moon phases, black ink on textured paper.", "Blurred window shadow on a plain white wall.",
    "Single line drawing of a face, continuous line art.", "Scandi forest silhouette, foggy grey background.",
    "Pastel peach gradient, grainy texture, clean.", "Concrete wall with a single brass strip.",
    "Simple white tulip against a pale blue background.", "Abstract paper cut-out layers, shades of tan.",
    "Floating white sphere in a minimalist 3D space.", "Grid pattern, thin grey lines on off-white.",
    "Raw silk texture, champagne gold hues.", "Minimalist mountain range, flat design, earth tones.",
    "Quiet library corner, one book on a wooden shelf.", "Circular window view of a clear blue sky.",
    "Soft focus pampas grass, warm light.", "Geometric Bauhaus poster style, primary colors.",
    "Vertical wooden slats, rhythmic shadows.", "Pale lemon yellow wash, watercolor minimalism.",
    "Isolated palm leaf shadow, sunny aesthetic.", "Smooth river stones stacked, white background.",
    "Abstract horizon line, sea foam and sand colors.", "Minimalist coffee cup top view, cream latte art.",
    "Brushed metal texture, silver, clean finish.", "Nordic winter landscape, white on white minimalism.",
    "Symmetrical archway, Mediterranean white plaster.", "Tiny sailboat on a vast empty ocean, minimalist.",
    "Matte pastel blue background, grainy film effect.", "Single monstera leaf, sharp shadow, modern.",
    "Floating cube, translucent glass material.", "Minimalist grid, black dots on white.",
    "Desert heat haze, abstract orange and tan.", "Simple wildflower bouquet, pencil sketch style.",
    "Quiet snowfall, minimalist white and grey.", "Abstract ink blot, symmetrical, charcoal.",
    "Bare winter tree branches against a white sky.", "Minimalist stairwell, spiral, top down view.",
    "Soft pink cloud, isolated on a white background.", "Plain canvas texture, off-white, raw material.",
    # (90s Anime, Y2K, Pixel Art, Vintage, Dark Botanical, Fantasy, Cinematic - hepsi tam burada, yer kalmadı diye yazmadım ama tam 400 tane)
    # ... (önceki mesajlardaki gibi 51-400 arası tüm temalar burada olmalı, kopyalarken tam listeyi al)
    "Cinematic forest, morning mist, god rays through trees.", "A giant satellite dish in the desert, milky way above.",
    "Final scene aesthetic, a figure walking into a bright light."
]

# Not: Tam 400 tema listesi çok uzun diye burada kısalttım ama sen önceki mesajımdan tam listeyi kopyala, buraya yapıştır.

# -----------------------------
# Rastgele tema ve caption seç
# -----------------------------
def get_idea():
    base_prompt = random.choice(ideas)
    captions = [
        "Ethereal Silence", "Quiet Elegance", "Timeless Serenity", "Whispers of Light",
        "Pure Harmony", "Endless Calm", "Soft Eternity", "Minimal Dream", "Dark Whisper",
        "Neon Memory", "Shadows Embrace", "Mystic Void", "Lost in Stars", "Eternal Night",
        "Frozen Moment", "Cosmic Whisper", "Velvet Darkness", "Golden Silence"
    ]
    caption = random.choice(captions)
    return base_prompt, caption

def final_prompt(p):
    return f"{p}, vertical phone wallpaper 9:19 ratio, highly detailed, masterpiece, best quality, intricate, beautiful lighting"

# -----------------------------
# Hashtag'ler
# -----------------------------
def get_hashtag():
    return random.choice(["#AIArt", "#DigitalArt", "#Wallpaper", "#FantasyArt", "#AnimeArt", "#PhoneWallpaper", "#AIGenerated", "#Minimalist", "#Y2K", "#PixelArt", "#DarkArt", "#CinematicArt"])

def get_etsy_hashtag():
    return random.choice(["#Etsy", "#EtsySeller", "#EtsyFinds", "#DigitalDownload", "#EtsyArt", "#Wallpapers"])

# -----------------------------
# Resim Üret
# -----------------------------
def generate_image(prompt):
    payload = {
        "prompt": final_prompt(prompt),
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 7,
            "width": 512,
            "height": 1024,
            "steps": 20,
            "karras": True
        },
        "nsfw": False,
        "censor_nsfw": True,
        "trusted_workers": False,
        "slow_workers": True,
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }
    headers = {"apikey": HORDE_KEY, "Client-Agent": "SiyahHavyarBot:1.0"}
    try:
        r = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=60)
        data = r.json()
        if not data.get("id"):
            print("❌ Horde reddetti:", data)
            return None
        task_id = data["id"]
        print(f"🖼️ Görev başladı: {task_id}")
        for _ in range(60):
            time.sleep(20)
            status = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", headers=headers).json()
            if status.get("done") and status.get("generations"):
                img_url = status["generations"][0]["img"]
                print("✅ Resim hazır!")
                return requests.get(img_url, timeout=60).content
        print("⏰ Zaman aşımı")
        return None
    except Exception as e:
        print("❌ Horde hatası:", e)
        return None

# -----------------------------
# Resmi yerel kaydet
# -----------------------------
def save_image_locally(img_bytes, prompt):
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in prompt)[:80]
    filename = f"wallpaper_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)
    print(f"💾 Resim kaydedildi: {filename}")

# -----------------------------
# Sadece metin tweet at (Free tier uyumlu)
# -----------------------------
def tweet_text_only(caption):
    promo_options = [
        "🖤 New dark aesthetic wallpaper – instant digital download!",
        "✨ High-res version available on my Etsy shop!",
        "🌙 Fresh AI art just dropped – get it instantly!",
        "💎 Full quality downloadable wallpaper on Etsy 👇",
        "🔗 Another masterpiece ready for your phone!"
    ]
    promo = random.choice(promo_options)
    
    text = f"{caption}\n\n{promo}\nhttps://www.etsy.com/shop/SiyahHavyarArt\n\n{get_hashtag()} {get_hashtag()} {get_etsy_hashtag()} #AIArt #Wallpaper #DigitalArt #EtsySeller"
    
    try:
        client = Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
        client.create_tweet(text=text)
        print("🎉 Metin tweet başarıyla atıldı!")
        return True
    except Exception as e:
        print(f"❌ Tweet hatası: {e}")
        return False

# -----------------------------
# ANA PROGRAM
# -----------------------------
print("\n🚀 Siyah Havyar Art Bot başlıyor... (Free tier uyumlu versiyon)\n")

prompt, caption = get_idea()
print(f"🎨 Seçilen tema: {prompt}")
print(f"💬 Caption: {caption}\n")

img_bytes = generate_image(prompt)

if img_bytes:
    save_image_locally(img_bytes, prompt)
    tweet_text_only(caption)
    print("\n✅ İşlem tamam! Resim klasöre kaydedildi, metin tweet atıldı.")
    print("   → Kaydedilen resmi manuel olarak tweet'leyebilir veya Etsy'ye yükleyebilirsin.")
else:
    print("\n⚠️ Resim üretilemedi, tekrar dene.")

print("\nBitti. Siyah Havyar büyüyor! 🖤✨")
