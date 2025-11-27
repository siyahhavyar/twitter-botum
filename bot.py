import tweepy
import random
import time
import os
from datetime import datetime
from huggingface_hub import InferenceClient

# ==============================================================================
# 1. TWITTER ANAHTARLARI (BUNLARI DOLDUR)
# ==============================================================================
api_key = ""
api_secret = ""
access_token = ""
access_secret = ""

# ==============================================================================
# 2. HUGGING FACE AYARLARI
# ==============================================================================
HF_TOKEN = "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"
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

# ==============================================================================
# 3. GENİŞLETİLMİŞ İÇERİK HAVUZLARI (MİNİMAL + ESTETİK + POPÜLER)
# ==============================================================================

# HAVUZ 1: MİNİMALİST / DOĞA / ESTETİK / FÜTÜRİSTİK (%85 İhtimal)
pool_minimalist = [
    # --- Doğa & Manzara ---
    {"subj": "lone tree on a hill under starry sky", "tag": "#Nature #Tree #Night"},
    {"subj": "paper boat on calm water reflecting moon", "tag": "#Origami #Ocean #Dreamy"},
    {"subj": "crescent moon and hanging stars", "tag": "#Moon #Night #Space"},
    {"subj": "distant lighthouse in purple fog", "tag": "#Lighthouse #Ocean #Vibe"},
    {"subj": "geometric mountains pastel colors", "tag": "#Mountains #Design #Art"},
    {"subj": "foggy pine forest mysterious", "tag": "#Forest #Nature #Fog"},
    {"subj": "raindrops on window city lights blur", "tag": "#Rain #Cozy #City"},
    {"subj": "sand dunes desert sunset", "tag": "#Desert #Nature #GoldenHour"},
    {"subj": "northern lights aurora borealis over snowy mountain", "tag": "#Aurora #NorthernLights #Winter"},
    {"subj": "cherry blossom sakura tree falling petals", "tag": "#Sakura #Japan #Pink"},
    {"subj": "autumn road with orange leaves", "tag": "#Autumn #Season #Cozy"},
    
    # --- Hayvanlar (Estetik) ---
    {"subj": "glowing jellyfish in deep dark ocean", "tag": "#Jellyfish #Ocean #Neon"},
    {"subj": "silhouette of a wolf howling at moon", "tag": "#Wolf #Moon #Wild"},
    {"subj": "flying whale in the clouds dreamlike", "tag": "#Whale #Surreal #Dreams"},
    {"subj": "geometric fox orange and white", "tag": "#Fox #Geometry #Art"},
    {"subj": "black cat silhouette looking at city", "tag": "#Cat #City #Night"},
    {"subj": "koi fish swimming in yin yang shape", "tag": "#Koi #Zen #Balance"},
    
    # --- Cyberpunk & Neon & Retro ---
    {"subj": "cyberpunk city street raining neon lights", "tag": "#Cyberpunk #Neon #SciFi"},
    {"subj": "retro synthwave sun grid landscape 80s style", "tag": "#Synthwave #Retro #80s"},
    {"subj": "lonely astronaut waiting at bus stop in space", "tag": "#Astronaut #Space #Vibe"},
    {"subj": "neon sign saying hope on brick wall", "tag": "#Neon #Hope #Vibe"},
    {"subj": "futuristic car flying in rain", "tag": "#Future #Car #SciFi"},
    
    # --- Obje & Soyut ---
    {"subj": "single coffee cup steam rising", "tag": "#Coffee #Morning #Cozy"},
    {"subj": "minimalist japanese torii gate red", "tag": "#Japan #Torii #Zen"},
    {"subj": "floating island in the sky with a house", "tag": "#Fantasy #DreamHouse"},
    {"subj": "hourglass with sand flowing up", "tag": "#Time #Surreal #Art"},
    {"subj": "abstract fluid colorful gradients", "tag": "#Abstract #Colors #Design"}
]

# HAVUZ 2: POPÜLER KÜLTÜR / SÜPER KAHRAMAN / OYUN (%15 İhtimal)
pool_pop_culture = [
    # --- Süper Kahramanlar ---
    {"subj": "Spiderman mask silhouette spider web", "tag": "#Spiderman #Marvel #Hero"},
    {"subj": "Batman watching gotham from gargoyle", "tag": "#Batman #DC #Gotham"},
    {"subj": "Iron Man arc reactor glowing blue", "tag": "#IronMan #Marvel #Tech"},
    {"subj": "Captain America shield vibranium", "tag": "#CaptainAmerica #Marvel"},
    {"subj": "Joker playing card minimalist", "tag": "#Joker #DC #Villain"},
    {"subj": "Wolverine claws scratch mark", "tag": "#Wolverine #XMen #Marvel"},
    {"subj": "Deadpool mask minimal", "tag": "#Deadpool #Marvel #Fun"},
    
    # --- Filmler & Diziler ---
    {"subj": "Star Wars darth vader helmet silhouette", "tag": "#StarWars #DarthVader #Sith"},
    {"subj": "Harry Potter glasses and lightning scar", "tag": "#HarryPotter #Hogwarts #Magic"},
    {"subj": "Lord of the Rings The One Ring glowing", "tag": "#LOTR #Ring #Fantasy"},
    {"subj": "Matrix digital rain green code", "tag": "#Matrix #Code #Hacker"},
    {"subj": "Totoro silhouette in rain with umbrella", "tag": "#Totoro #Ghibli #Anime"},
    {"subj": "One Piece straw hat skull flag", "tag": "#OnePiece #Anime #Pirate"},
    
    # --- Oyunlar ---
    {"subj": "Super Mario red hat and mustache", "tag": "#Mario #Nintendo #Gaming"},
    {"subj": "Pikachu silhouette yellow lightning", "tag": "#Pokemon #Pikachu #Anime"},
    {"subj": "Minecraft grass block minimalist", "tag": "#Minecraft #Gaming #Block"},
    {"subj": "Zelda Triforce glowing gold", "tag": "#Zelda #Gaming #Legend"},
    {"subj": "Pacman chasing ghosts minimal", "tag": "#Pacman #Retro #Gaming"},
    {"subj": "Among Us crewmate red sus", "tag": "#AmongUs #Gaming #Sus"}
]

questions = [
    "Rate this 1-10 ✨", 
    "Wallpaper material? 📱", 
    "Tag your duo 👇",
    "Clean and simple.", 
    "Left or Right? 🤔", 
    "Save for later 🔒",
    "Describe this in one word.", 
    "Your daily aesthetic dose ✨",
    "Download or Pass? 👇", 
    "Pure visual therapy 🧘‍♂️", 
    "Make your screen happy.",
    "Is this your style? Yes/No", 
    "Dark mode or Light mode? 🌗",
    "What song plays in your head seeing this? 🎵",
    "Imagine being here.",
    "Simplicity is elegance."
]

# ==============================================================================
# 4. KAYIT SİSTEMİ
# ==============================================================================
LOG_FILE = "gecmis.txt"

def kontrol_et_ve_kaydet(hedef_saat):
    bugun = datetime.now().strftime("%Y-%m-%d")
    imza = f"{bugun}|{hedef_saat}"
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            if imza in f.read():
                return True
    return False

def kayit_dus(hedef_saat):
    bugun = datetime.now().strftime("%Y-%m-%d")
    with open(LOG_FILE, "a") as f:
        f.write(f"{bugun}|{hedef_saat}\n")

# ==============================================================================
# 5. RESİM ÜRETİM VE TWEETLEME
# ==============================================================================
def generate_image_safe():
    zar = random.randint(1, 100)
    # %85 ihtimalle Minimalist/Doğa, %15 ihtimalle Pop Kültür
    if zar <= 85:
        selection = random.choice(pool_minimalist)
        prompt_style = "minimalist phone wallpaper, pastel colors, soft lighting, serene, aesthetic, highly detailed"
    else:
        selection = random.choice(pool_pop_culture)
        prompt_style = "minimalist vector art, flat design, icon style, solid background, clean lines"

    subject = selection["subj"]
    tags = selection["tag"]
    # DİKEY FORMAT (TELEFON DUVAR KAĞIDI) + 8K KALİTE
    prompt = f"{prompt_style}, {subject}, vertical, aspect ratio 2:3, 8k resolution, masterpiece, sharp focus, clean composition, --no text, --no blur"
    
    print(f"\n🎨 Çizim Hazırlanıyor: {subject}")
    try:
        client = InferenceClient(model=repo_id, token=HF_TOKEN)
        # 768x1344 -> Telefon ekranı için en ideal boyut
        image = client.text_to_image(prompt, width=768, height=1344)
        image.save("art_post.jpg")
        return True, subject, tags
    except Exception as e:
        print(f"Hata: {e}")
        return False, None, None

def post_tweet(saat_etiketi):
    print(f"🚀 Tweet Gönderiliyor... ({saat_etiketi})")
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

    try:
        success, theme_name, tags = generate_image_safe()
        if success:
            media = api.media_upload(filename="art_post.jpg")
            question = random.choice(questions)
            caption = f"Daily Wallpaper 📱\nTheme: {theme_name}\n\n{question}\n\n{tags} #Minimalist #AIArt #PhoneWallpaper"
            client.create_tweet(text=caption, media_ids=[media.media_id])
            print(f"✅ BAŞARILI! ({saat_etiketi} postu atıldı.)")
            kayit_dus(saat_etiketi)
            return True
        else:
            print("❌ Resim üretilemedi.")
            return False
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")
        return False

# ==============================================================================
# 6. ANA KONTROL DÖNGÜSÜ (06, 07, 15, 19, 21:21, 00)
# ==============================================================================
print("🤖 GENİŞLETİLMİŞ BOT DEVREDE (6 POST)")
print("Hedef Saatler: 06:00, 07:00, 15:00, 19:00, 21:21, 00:00")
print("Pencereyi kapatma, aşağı indir...")
print("-" * 50)

HEDEFLER = ["06:00", "07:00", "15:00", "19:00", "21:21", "00:00"]

while True:
    simdi = datetime.now()
    
    for hedef in HEDEFLER:
        # Hedef saati bugüne uyarla
        hedef_zamani = datetime.strptime(f"{simdi.strftime('%Y-%m-%d')} {hedef}", "%Y-%m-%d %H:%M")
        
        # Eğer şu anki saat hedefi geçtiyse VE daha önce atılmadıysa
        if simdi >= hedef_zamani:
            if not kontrol_et_ve_kaydet(hedef):
                print(f"🔔 SAAT GELDİ: {hedef} postu atılıyor...")
                post_tweet(hedef)
                print("☕ Spam koruması: 1 dakika dinleniyorum...")
                time.sleep(60) 
            else:
                pass
    
    time.sleep(30)
