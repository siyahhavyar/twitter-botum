import os
import time
import requests
import tweepy
import random
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

ETSY_LINK = "https://siyahhavyarart.etsy.com"

# -----------------------------
# 220 ADET PROMPT LİSTESİ (22 x 10 Konu)
# -----------------------------
ALL_PROMPTS = [
    # --- 1. Cyber-Zen Cityscapes ---
    "Cyberpunk Tokyo street with cherry blossoms falling, 9:22", "Rain-slicked futuristic alleyway with neon signs reflecting in puddles, 9:22",
    "A greenhouse inside a spaceship looking out at a nebula, 9:22", "Holographic bonsai tree in a dark high-tech apartment, 9:22",
    "Cybernetic forest with glowing blue roots and metallic leaves, 9:22", "A girl sitting on a skyscraper edge overlooking a glowing megacity, 9:22",
    "Future Seoul with traditional Hanok roofs and floating cars, 9:22", "Neon pink waterfall flowing through a dark chrome canyon, 9:22",
    "Floating islands with high-tech villas and digital clouds, 9:22", "A robot gardener tending to a vertical garden on a skyscraper, 9:22",
    "Cyberpunk shrine with laser-gate torii, 9:22", "Underwater neon city with bioluminescent sea life, 9:22",
    "Futuristic library with floating digital scrolls, 9:22", "A train cabin traveling through a tunnel of light, 9:22",
    "Neon-lit marketplace in a desert oasis of the future, 9:22", "Glass bridge over a neon abyss, minimal design, 9:22",
    "A futuristic bedroom with a massive window showing Saturn, 9:22", "Digital rain falling on a metallic lotus flower, 9:22",
    "High-tech tea house on a floating cloud, 9:22", "Cyberpunk street food stall with steam and purple lighting, 9:22",
    "Abandoned robot overgrown with glowing moss, 9:22", "Future Paris with a neon Eiffel Tower and flying drones, 9:22",

    # --- 2. Dreamcore & Surreal ---
    "Endless marble stairs leading into a pink sunset sky, 9:22", "A single door standing in the middle of a flower field, 9:22",
    "Giant floating bubbles containing miniature worlds, 9:22", "A white bed floating on a calm turquoise ocean, 9:22",
    "Soft clouds shaped like whales swimming in the sky, 9:22", "A library where books are flying like birds, 9:22",
    "Pastel desert with giant crystalline structures, 9:22", "Mirror-like lake reflecting a galaxy instead of the sky, 9:22",
    "A lighthouse casting light into a nebula, 9:22", "Giant mushrooms in a misty, lavender-colored forest, 9:22",
    "An hourglass with stars instead of sand, 9:22", "A floating golden staircase in a void, 9:22",
    "Moon hanging low over a field of glowing sunflowers, 9:22", "A train track made of water through a candy-colored forest, 9:22",
    "Surreal floating mountains with waterfalls flowing upwards, 9:22", "A giant clock face under the ocean ripples, 9:22",
    "Paper planes flying towards a giant golden sun, 9:22", "A cozy cottage inside a giant glass jar, 9:22",
    "Abstract waves of liquid silk in pastel colors, 9:22", "A girl swinging from a crescent moon, 9:22",
    "Giant chess pieces on a checkered desert, 9:22", "A path of glowing stones through a dark misty valley, 9:22",

    # --- 3. Aesthetic Anime Girls ---
    "Anime girl drinking tea by a rainy window, lo-fi style, 9:22", "Girl with headphones sitting on a train, sunset lighting, 9:22",
    "Anime girl reading a book in a sunlit garden, Ghibli style, 9:22", "A girl standing under a cherry blossom tree, petals flying, 9:22",
    "Anime girl looking at the starry night sky from a balcony, 9:22", "Street fashion anime girl in a neon Tokyo district, 9:22",
    "Girl walking a cat in a quiet suburban street, soft colors, 9:22", "Anime girl playing guitar in a cozy bedroom, 9:22",
    "A girl with glowing eyes in a dark fantasy forest, 9:22", "Anime girl painting on a canvas in an art studio, 9:22",
    "Girl waiting at a bus stop under a giant umbrella, 9:22", "Anime girl in a white dress standing in a sunflower field, 9:22",
    "Tech-wear anime girl with a futuristic visor, 9:22", "Girl eating ramen at a night market, cinematic lighting, 9:22",
    "Anime girl sleeping on a pile of fluffy clouds, 9:22", "Girl on a bicycle riding through a seaside town, 9:22",
    "Cyber-hacker anime girl in front of many screens, 9:22", "Anime girl with fox ears in a traditional Japanese shrine, 9:22",
    "Girl watching a summer festival with fireworks, 9:22", "Anime girl in a library with floating magical books, 9:22",
    "A girl sitting on a rooftop with a panoramic city view, 9:22", "Anime girl walking through a futuristic mall, 9:22",

    # --- 4. Dark Fantasy & Gothic ---
    "A gothic cathedral under a blood red moon, 9:22", "Dark knight in obsidian armor standing in a blizzard, 9:22",
    "Abandoned throne room overgrown with black roses, 9:22", "A mysterious figure in a cloak holding a blue flame, 9:22",
    "Crows flying over a misty graveyard at twilight, 9:22", "A silver dragon perched on a jagged mountain peak, 9:22",
    "Ghostly ship sailing on a sea of shadows, 9:22", "Dark palace with glowing purple windows, 9:22",
    "A vampire countess in a red velvet gown, 9:22", "Enchanted forest with black trees and silver mist, 9:22",
    "A crown of thorns sitting on a stone altar, 9:22", "Dark angel with tattered wings looking at a ruined city, 9:22",
    "Ancient library with candles and dusty scrolls, 9:22", "A black panther with glowing green eyes in the dark, 9:22",
    "Gothic iron gates leading to a mysterious mansion, 9:22", "A magical ritual with glowing runes on the floor, 9:22",
    "Dark knight fighting a giant shadow monster, 9:22", "Moonlit balcony with a view of a dark abyss, 9:22",
    "Skeletal hands holding a glowing crystal ball, 9:22", "A dark lake with a submerged stone castle, 9:22",
    "Raven perched on a skull in a foggy forest, 9:22", "Dark queen with a crown of obsidian, 9:22",
    "Ruined bridge over a river of liquid gold, 9:22",

    # --- 5. Liquid Abstract ---
    "Iridescent liquid metal ripples, 3D render, 9:22", "Abstract glass spheres floating in a void, 9:22",
    "Swirling patterns of gold and black silk, 9:22", "Translucent colorful crystals stacked vertically, 9:22",
    "Abstract waves of neon liquid light, 9:22", "Multi-colored smoke frozen in time, 9:22",
    "Molten silver flowing over matte black rocks, 9:22", "Dynamic abstract shards of blue glass, 9:22",
    "Bubbles of oil in water, macro photography, 9:22", "Abstract geometric shapes in 3D, pastel colors, 9:22",
    "Liquid holograph reflecting a rainbow, 9:22", "Soft fabric-like waves in a minimalist room, 9:22",
    "Glowing fiber optic strands in the dark, 9:22", "Fractal patterns in deep purple and gold, 9:22",
    "Abstract explosion of colorful sand, 9:22", "Glass prisms refracting light into rainbows, 9:22",
    "Liquid marble texture in emerald and white, 9:22", "3D rendered twisted metallic tubes, 9:22",
    "Abstract flow of glowing magma under ice, 9:22", "Soft focus bokeh of neon lights, 9:22",
    "Abstract layers of colored paper, 9:22", "Digital glitches on a dark background, 9:22",
    "Transparent 3D heart made of glass, 9:22",

    # --- 6. Nature Minimalism ---
    "Single pine tree on a snowy hill, minimalist white background, 9:22", "Calm lake reflection of a crescent moon, 9:22",
    "Macro shot of a single green leaf with a water drop, 9:22", "Misty mountain peaks in the early morning, 9:22",
    "Golden wheat field under a clear blue sky, 9:22", "A single white flower in a vast dark field, 9:22",
    "Abstract desert dunes with sharp shadows, 9:22", "Silhouette of a bird flying over a calm ocean at dusk, 9:22",
    "Close-up of bamboo stalks, soft green lighting, 9:22", "Zen stones stacked perfectly by a small stream, 9:22",
    "Frozen bubbles on a dark ice surface, 9:22", "Top down view of a lonely forest path, 9:22",
    "Minimalist sea waves hitting white sand, 9:22", "A single red tulip in a black and white world, 9:22",
    "Foggy forest with light rays piercing through trees, 9:22", "Geometric ice crystals on a window pane, 9:22",
    "Soft pink cherry blossoms against a minimalist grey wall, 9:22", "Underwater view of sunlight rays in blue water, 9:22",
    "A small wooden boat on a mirror-like lake, 9:22", "Abstract pattern of palm leaf shadows on a white wall, 9:22",
    "Lavender field stretching to the horizon, 9:22", "Dark stormy clouds over a golden meadow, 9:22",

    # --- 7. Retro Future ---
    "Retro sports car driving into a digital sunset, 9:22", "Synthwave grid landscape with neon mountains, 9:22",
    "A futuristic walkman floating in space with neon tapes, 9:22", "Cyberpunk arcade room with glowing screens, 9:22",
    "Retro astronaut sitting on a neon moon, 9:22", "A palm tree silhouette against a giant retro sun, 9:22",
    "Neon-lit city street with 80s aesthetic and rain, 9:22", "VHS glitch effect on a futuristic skyline, 9:22",
    "Floating geometric shapes in a pink and cyan void, 9:22", "A cassette tape unraveling into a nebula, 9:22",
    "Cyber-pink motorcycle parked under a neon billboard, 9:22", "Retro-futuristic computer terminal with green code, 9:22",
    "A pair of neon roller skates on a glowing grid floor, 9:22", "Digital sunset reflected in a space helmet, 9:22",
    "Vaporwave statue of David with neon sunglasses, 9:22", "Electric blue lightning over a purple desert, 9:22",
    "80s style robot dancing in a disco light setting, 9:22", "A futuristic boombox blasting neon soundwaves, 9:22",
    "Retro highway with infinite light trails, 9:22", "A neon-lit dolphin jumping over a digital ocean, 9:22",
    "Cyberpunk pizza shop with flickering pink signs, 9:22", "Abstract 3D pyramids in a retro-space environment, 9:22",
    "A glowing heart made of neon tubes on a brick wall, 9:22",

    # --- 8. Space Odyssey ---
    "A massive black hole bending light around it, 9:22", "Astronaut floating lonely in a colorful nebula, 9:22",
    "Two planets colliding in a slow-motion explosion, 9:22", "A futuristic space station orbiting a ringed planet, 9:22",
    "Close-up of the moon's surface with Earth in the back, 9:22", "A galaxy shaped like a giant eye, 9:22",
    "Cosmic dust forming the shape of a phoenix, 9:22", "A futuristic rover on a red Martian desert, 9:22",
    "Alien forest with glowing plants under two moons, 9:22", "Starship entering a wormhole, light-speed, 9:22",
    "A clear view of the Milky Way from a mountain top, 9:22", "Astronaut standing on an asteroid looking at a supernova, 9:22",
    "Giant gas giant planet with storm swirls, 9:22", "A cosmic lighthouse on the edge of the universe, 9:22",
    "Rain of diamonds on a dark icy planet, 9:22", "A futuristic city built inside a moon crater, 9:22",
    "Satellite floating over a glowing blue Earth at night, 9:22", "Abstract cosmic ocean with liquid stars, 9:22",
    "A staircase made of light leading into a nebula, 9:22", "Space whale swimming through a sea of stars, 9:22",
    "Abandoned spaceship overgrown with alien moss, 9:22", "A glowing portal on a desolate dark planet, 9:22",
    "Close-up of a sun flare, intense orange and yellow, 9:22",

    # --- 9. Cute & Kawaii Anime ---
    "Tiny anime girl sleeping on a giant fluffy cat, 9:22", "A group of chibi characters having a tea party, 9:22",
    "Anime girl with bunny ears eating a strawberry crepe, 9:22", "Cute magical girl with a star wand, 9:22",
    "Little anime witch flying on a broom with a cat, 9:22", "A room full of plushies and fairy lights, 9:22",
    "Anime girl in a dinosaur onesie drinking milk, 9:22", "Kawaii fox girl playing in autumn leaves, 9:22",
    "Chibi knight protecting a tiny dragon, 9:22", "Anime girl making a heart with her hands, 9:22",
    "Pastel colored candy shop with a cute anime cashier, 9:22", "A girl floating with dozens of colorful balloons, 9:22",
    "Cute anime girl hiding in a giant sunflower, 9:22", "Chibi girl sitting on a slice of watermelon, 9:22",
    "Anime girl with blue hair and a penguin hoodie, 9:22", "A magical forest with tiny glowing anime fairies, 9:22",
    "Kawaii girl painting pink clouds on a blue sky, 9:22", "Chibi angel sitting on a rainbow, 9:22",
    "Anime girl and her Shiba Inu dog at a park, 9:22", "Cute mermaid girl in an aquarium with bubbles, 9:22",
    "Anime girl with bear ears holding a giant honey jar, 9:22", "Tiny anime girl living in a teapot house, 9:22",
    "Kawaii girl under a rain of falling stars, 9:22",

    # --- 10. Dark Tech & Hardware ---
    "Close-up of a glowing CPU with liquid cooling pipes, 9:22", "Transparent smartphone showing internal circuit boards, 9:22",
    "Cybernetic hand reaching out from a dark screen, 9:22", "Matrix-style green code falling over black, 9:22",
    "A futuristic laboratory with a humanoid robot, 9:22", "Mechanical heart made of gears and blue wires, 9:22",
    "Close-up of a high-tech camera lens reflecting a city, 9:22", "Glowing fiber optic cables in a dark server room, 9:22",
    "Abstract 3D motherboard with neon light paths, 9:22", "A futuristic drone flying through a dark rainy city, 9:22",
    "Cyberpunk visor with a digital HUD display, 9:22", "Microchip landscape that looks like a tiny city, 9:22",
    "A robotic eye with a red glowing iris, macro, 9:22", "Dark hardware texture with orange glowing accents, 9:22",
    "Futuristic keyboard with neon RGB lighting, 9:22", "A hacker desk with multiple monitors, dark vibes, 9:22",
    "Mechanical wings made of chrome and carbon fiber, 9:22", "Liquid metal forming a 3D skull, 9:22",
    "High-tech jet engine with glowing blue plasma, 9:22", "Circuit board patterns etched into dark glass, 9:22",
    "A robotic cat with metallic fur and glowing eyes, 9:22", "Futuristic data center with rows of lights, 9:22"
]

def get_smart_caption(selected_prompt):
    instruction = f"""
    Act as a creative social media expert. A wallpaper was generated with this prompt: "{selected_prompt}".
    
    TASK:
    1. Write a short, poetic, and engaging Twitter caption.
    2. Ensure it reflects the theme of the image (e.g., mysterious for dark fantasy, cozy for anime).
    3. Include 3-5 trending and relevant hashtags.
    
    RULES: Return ONLY the caption and hashtags. Do not include any meta-talk.
    """
    
    # PLAN A: GROQ
    if GROQ_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": instruction}], "temperature": 0.8}
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
        except: pass
    
    # PLAN B: GEMINI (Kütüphanesiz)
    if GEMINI_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": instruction}]}]}
            
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Gemini API Hata: {e}")

    return "Transform your phone with this unique artistic piece! ✨ #DigitalArt #Art #Wallpaper"

def try_generate_image(prompt_text):
    final_prompt = f"{prompt_text}, high-quality digital art, 8k resolution, cinematic lighting, masterpiece"
    generate_url = "https://stablehorde.net/api/v2/generate/async"
    headers = {"apikey": HORDE_KEY if HORDE_KEY else "0000000000", "Client-Agent": "SiyahHavyarBot:1.0"}
    
    payload = {
        "prompt": final_prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 7.5, "width": 640, "height": 1408, "steps": 30,
            "post_processing": ["RealESRGAN_x4plus"]
        },
        "models": ["AlbedoBase XL (SDXL)", "Juggernaut XL"]
    }

    try:
        req = requests.post(generate_url, json=payload, headers=headers, timeout=40)
        if req.status_code == 202:
            task_id = req.json()['id']
            while True:
                time.sleep(15)
                check = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}")
                status = check.json()
                if status['done']:
                    return requests.get(status['generations'][0]['img']).content
                print(f"⌛ Sıra: {status.get('queue_position', '?')} | Hazırlanıyor...")
    except: return None

def post_to_twitter(img_bytes, caption_text):
    final_text = f"{caption_text}\n\n🎨 Get high quality prints: {ETSY_LINK}"
    filename = "wallpaper.png"
    with open(filename, "wb") as f: f.write(img_bytes)

    try:
        # 1. Medya Yükleme (V1.1 - Burası Erişim Jetonu ister)
        auth = OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = API(auth)
        media = api.media_upload(filename)
        
        # 2. Tweet Atma (V2 - Burası da Erişim Jetonu ister)
        client = Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        client.create_tweet(text=final_text, media_ids=[media.media_id])
        print("🐦 Paylaşım başarıyla tamamlandı!")
        return True
    except Exception as e:
        print(f"❌ Twitter hatası: {e}")
        return False
    finally:
        if os.path.exists(filename): os.remove(filename)

if __name__ == "__main__":
    print(f"--- GITHUB ACTION BAŞLADI: {datetime.now()} ---")
    
    # 220'den rastgele seç
    picked = random.choice(ALL_PROMPTS)
    
    # Açıklama ve Görsel
    caption = get_smart_caption(picked)
    image = try_generate_image(picked)
    
    if image:
        post_to_twitter(image, caption)
    else:
        print("🚨 HATA: Görsel oluşturulamadı.")