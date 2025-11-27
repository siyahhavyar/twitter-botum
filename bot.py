import tweepy
import os
import random
from huggingface_hub import InferenceClient

# --- ŞİFRELERİ KASADAN ÇEKİYORUZ ---
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']
HF_TOKEN = os.environ['HF_TOKEN']

repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

# --- GENİŞLETİLMİŞ İÇERİK HAVUZU ---
pool_minimalist = [
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
    {"subj": "glowing jellyfish in deep dark ocean", "tag": "#Jellyfish #Ocean #Neon"},
    {"subj": "silhouette of a wolf howling at moon", "tag": "#Wolf #Moon #Wild"},
    {"subj": "flying whale in the clouds dreamlike", "tag": "#Whale #Surreal #Dreams"},
    {"subj": "geometric fox orange and white", "tag": "#Fox #Geometry #Art"},
    {"subj": "black cat silhouette looking at city", "tag": "#Cat #City #Night"},
    {"subj": "koi fish swimming in yin yang shape", "tag": "#Koi #Zen #Balance"},
    {"subj": "cyberpunk city street raining neon lights", "tag": "#Cyberpunk #Neon #SciFi"},
    {"subj": "retro synthwave sun grid landscape 80s style", "tag": "#Synthwave #Retro #80s"},
    {"subj": "lonely astronaut waiting at bus stop in space", "tag": "#Astronaut #Space #Vibe"},
    {"subj": "neon sign saying hope on brick wall", "tag": "#Neon #Hope #Vibe"},
    {"subj": "futuristic car flying in rain", "tag": "#Future #Car #SciFi"},
    {"subj": "single coffee cup steam rising", "tag": "#Coffee #Morning #Cozy"},
    {"subj": "minimalist japanese torii gate red", "tag": "#Japan #Torii #Zen"},
    {"subj": "floating island in the sky with a house", "tag": "#Fantasy #DreamHouse"},
    {"subj": "hourglass with sand flowing up", "tag": "#Time #Surreal #Art"},
    {"subj": "abstract fluid colorful gradients", "tag": "#Abstract #Colors #Design"}
]

pool_pop_culture = [
    {"subj": "Spiderman mask silhouette spider web", "tag": "#Spiderman #Marvel #Hero"},
    {"subj": "Batman watching gotham from gargoyle", "tag": "#Batman #DC #Gotham"},
    {"subj": "Iron Man arc reactor glowing blue", "tag": "#IronMan #Marvel #Tech"},
    {"subj": "Captain America shield vibranium", "tag": "#CaptainAmerica #Marvel"},
    {"subj": "Joker playing card minimalist", "tag": "#Joker #DC #Villain"},
    {"subj": "Wolverine claws scratch mark", "tag": "#Wolverine #XMen #Marvel"},
    {"subj": "Deadpool mask minimal", "tag": "#Deadpool #Marvel #Fun"},
    {"subj": "Star Wars darth vader helmet silhouette", "tag": "#StarWars #DarthVader #Sith"},
    {"subj": "Harry Potter glasses and lightning scar", "tag": "#HarryPotter #Hogwarts #Magic"},
    {"subj": "Lord of the Rings The One Ring glowing", "tag": "#LOTR #Ring #Fantasy"},
    {"subj": "Matrix digital rain green code", "tag": "#Matrix #Code #Hacker"},
    {"subj": "Totoro silhouette in rain with umbrella", "tag": "#Totoro #Ghibli #Anime"},
    {"subj": "One Piece straw hat skull flag", "tag": "#OnePiece #Anime #Pirate"},
    {"subj": "Super Mario red hat and mustache", "tag": "#Mario #Nintendo #Gaming"},
    {"subj": "Pikachu silhouette yellow lightning", "tag": "#Pokemon #Pikachu #Anime"},
    {"subj": "Minecraft grass block minimalist", "tag": "#Minecraft #Gaming #Block"},
    {"subj": "Zelda Triforce glowing gold", "tag": "#Zelda #Gaming #Legend"},
    {"subj": "Pacman chasing ghosts minimal", "tag": "#Pacman #Retro #Gaming"},
    {"subj": "Among Us crewmate red sus", "tag": "#AmongUs #Gaming #Sus"}
]

questions = [
    "Rate this 1-10 ✨", "Wallpaper material? 📱", "Tag your duo 👇", "Clean and simple.", 
    "Left or Right? 🤔", "Save for later 🔒", "Describe this in one word.", 
    "Your daily aesthetic dose ✨", "Download or Pass? 👇", "Pure visual therapy 🧘‍♂️", 
    "Make your screen happy.", "Is this your style? Yes/No", "Dark mode or Light mode? 🌗",
    "What song plays in your head seeing this? 🎵", "Imagine being here.", "Simplicity is elegance."
]

def generate_image_safe():
    zar = random.randint(1, 100)
    # %85 Minimalist, %15 Pop Kültür
    if zar <= 85:
        selection = random.choice(pool_minimalist)
        prompt_style = "minimalist phone wallpaper, pastel colors, soft lighting, serene, aesthetic, highly detailed"
    else:
        selection = random.choice(pool_pop_culture)
        prompt_style = "minimalist vector art, flat design, icon style, solid background, clean lines"

    subject = selection["subj"]
    tags = selection["tag"]
    
    # TELEFON BOYUTU (DİKEY)
    prompt = f"{prompt_style}, {subject}, vertical, aspect ratio 2:3, 8k resolution, masterpiece, sharp focus, clean composition, --no text, --no blur"
    
    print(f"🎨 Konu Seçildi: {subject}")
    
    try:
        client = InferenceClient(model=repo_id, token=HF_TOKEN)
        # 768x1344 = En iyi dikey oran
        image = client.text_to_image(prompt, width=768, height=1344)
        image.save("art_post.jpg")
        return True, subject, tags
    except Exception as e:
        print(f"❌ Resim Hatası: {e}")
        return False, None, None

def post_tweet():
    # Yetkilendirme
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
            print(f"✅ BULUTTAN BAŞARIYLA ATILDI! ({theme_name})")
        else:
            print("❌ Resim üretilemedi.")
    except Exception as e:
        print(f"❌ Twitter Hatası: {e}")

if __name__ == "__main__":
    post_tweet()
