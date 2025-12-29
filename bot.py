import os
import time
import requests
import tweepy
import random
from datetime import datetime
from tweepy import OAuth1UserHandler, API, Client

# KEYS
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GROQ_KEY = os.getenv("GROQ_API_KEY")

print("🔑 Key Durumu:")
print(f"Twitter: {'Var' if API_KEY and ACCESS_TOKEN else 'Eksik!'}")
print(f"Groq: {'Var' if GROQ_KEY else 'Yok'}")

if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_SECRET):
    print("❌ Twitter key'leri eksik!")
    exit()

# -----------------------------
# HORDE KEYS - EN YÜKSEK KUDOS'LU SEÇ
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
# TÜM TEMALAR - 400 FİKİR (tam liste, hiçbir şey silinmedi)
# -----------------------------
ideas = [
    # 1-50 Minimalist ve Fonksiyonel
    "Abstract sand dunes, soft shadows, beige tones.",
    "Geometric white stairs, architectural shadow, bright.",
    "Single eucalyptus branch in a glass vase, neutral wall.",
    "Japandi style interior, empty room, wooden floor.",
    "Soft linen fabric texture, cream color, morning sun.",
    "Matte black circles on charcoal grey background.",
    "Pale sage green organic shapes, minimalist.",
    "Thin gold line across a white marble surface.",
    "Wabi-sabi clay bowl on a rough stone table.",
    "Abstract topography map, white on white, 3D depth.",
    "Zen garden ripples, grey sand, single pebble.",
    "Mid-century modern abstract shapes, terracotta palette.",
    "Minimalist moon phases, black ink on textured paper.",
    "Blurred window shadow on a plain white wall.",
    "Single line drawing of a face, continuous line art.",
    "Scandi forest silhouette, foggy grey background.",
    "Pastel peach gradient, grainy texture, clean.",
    "Concrete wall with a single brass strip.",
    "Simple white tulip against a pale blue background.",
    "Abstract paper cut-out layers, shades of tan.",
    "Floating white sphere in a minimalist 3D space.",
    "Grid pattern, thin grey lines on off-white.",
    "Raw silk texture, champagne gold hues.",
    "Minimalist mountain range, flat design, earth tones.",
    "Quiet library corner, one book on a wooden shelf.",
    "Circular window view of a clear blue sky.",
    "Soft focus pampas grass, warm light.",
    "Geometric Bauhaus poster style, primary colors.",
    "Vertical wooden slats, rhythmic shadows.",
    "Pale lemon yellow wash, watercolor minimalism.",
    "Isolated palm leaf shadow, sunny aesthetic.",
    "Smooth river stones stacked, white background.",
    "Abstract horizon line, sea foam and sand colors.",
    "Minimalist coffee cup top view, cream latte art.",
    "Brushed metal texture, silver, clean finish.",
    "Nordic winter landscape, white on white minimalism.",
    "Symmetrical archway, Mediterranean white plaster.",
    "Tiny sailboat on a vast empty ocean, minimalist.",
    "Matte pastel blue background, grainy film effect.",
    "Single monstera leaf, sharp shadow, modern.",
    "Floating cube, translucent glass material.",
    "Minimalist grid, black dots on white.",
    "Desert heat haze, abstract orange and tan.",
    "Simple wildflower bouquet, pencil sketch style.",
    "Quiet snowfall, minimalist white and grey.",
    "Abstract ink blot, symmetrical, charcoal.",
    "Bare winter tree branches against a white sky.",
    "Minimalist stairwell, spiral, top down view.",
    "Soft pink cloud, isolated on a white background.",
    "Plain canvas texture, off-white, raw material.",
    # 51-100 90s Anime Aesthetic
    "90s anime Tokyo street, sunset, purple sky.",
    "Lo-fi anime bedroom, messy desk, CRT monitor.",
    "Retro anime train window, moving landscape, grain.",
    "Vending machine in the rain, neon glow, anime style.",
    "Sailor Moon inspired crescent moon and stars.",
    "90s anime convenience store, night time, aesthetic.",
    "Summer clouds, Ghibli style, bright blue sky.",
    "Retro anime girl with headphones, bus stop.",
    "Aesthetic anime cafe, steaming coffee, pastel.",
    "90s anime balcony, laundry hanging, sunset view.",
    "VHS glitch, anime city skyline, 1990s style.",
    "Retro anime car interior, night drive, city lights.",
    "School rooftop, anime aesthetic, wind blowing.",
    "Nostalgic anime kitchen, breakfast, soft sunlight.",
    "90s anime park, falling cherry blossoms.",
    "Retro computer screen, pixelated windows, 90s style.",
    "Anime beach, sparkling water, retro film grain.",
    "Lonely telephone booth, 90s anime night scene.",
    "Pastel purple ocean waves, retro anime aesthetic.",
    "Lo-fi anime library, dust motes in sunbeams.",
    "90s anime power lines, orange sunset gradient.",
    "Retro anime sneaker, aesthetic colors, lo-fi.",
    "90s anime basketball court, golden hour.",
    "Aesthetic anime rain on a window pane, city lights.",
    "90s anime bookstore, cozy, nostalgic vibe.",
    "Retro anime cat sleeping on a windowsill.",
    "Suburban Japan street, 90s anime style, summer.",
    "Vintage anime cassette player, pastel colors.",
    "90s anime flower shop, aesthetic blossoms.",
    "Retro anime ice cream shop, neon signs.",
    "Anime style starry night over a quiet lake.",
    "90s anime subway station, empty, nostalgic.",
    "Aesthetic anime piano, music sheets, soft light.",
    "Retro anime bicycle parked under a tree.",
    "90s anime laundry mat, pastel blue and pink.",
    "Aesthetic anime clouds, rainbow at dusk.",
    "Retro anime video game arcade, neon glow.",
    "90s anime bridge, river, evening glow.",
    "Lo-fi anime study desk, plant, lamp light.",
    "90s anime skyscraper, moon in the background.",
    "Retro anime breakfast tray, miso soup, aesthetics.",
    "90s anime rainy day, umbrella, street puddle.",
    "Aesthetic anime forest path, fireflies.",
    "Retro anime sunglasses on a beach towel.",
    "90s anime clock tower, sunset clouds.",
    "Aesthetic anime greenhouse, tropical plants.",
    "90s anime rooftop view, water tank, dusk.",
    "Retro anime bedroom, fairy lights, cozy night.",
    "90s anime harbor, boats, pastel sky.",
    "Lo-fi anime ramen shop, steam, warm glow.",
    # 101-150 Y2K Cyber
    "Y2K aesthetic, glossy pink butterfly, chrome edges.",
    "Iridescent CD stack, metallic blue lighting.",
    "Motorola Razr style flip phone, glitter texture.",
    "Cyber Y2K background, liquid metal, neon pink.",
    "2000s tech aesthetic, translucent plastic iMac.",
    "Floating 3D hearts, chrome finish, purple glow.",
    "Y2K cyber grid, bright blue lines, dark background.",
    "Furry pink boots, 2000s fashion aesthetic.",
    "Holographic star pattern, Y2K dreamcore.",
    "Retro digital camera, flash effect, Y2K style.",
    "Cyberpunk bubble font, \"2000\" text, metallic.",
    "Y2K futuristic tunnel, neon lights, glossy.",
    "Blue glitter background, star stickers, Y2K.",
    "Metallic silver puffy jacket, fashion editorial.",
    "Y2K butterfly clips, pastel hair, close-up.",
    "Cyber rave aesthetic, neon green and pink.",
    "Translucent electronics, Y2K gadget, blue LED.",
    "Glossy lip gloss aesthetic, Y2K pink mood.",
    "2000s web design aesthetic, pop-ups, glitter.",
    "Y2K heart locket, chrome metal, wings.",
    "Liquid chrome shapes, iridescent rainbow glow.",
    "Y2K gaming console, transparent purple plastic.",
    "Cyber core wallpaper, matrix code, neon blue.",
    "2000s mall aesthetic, neon lights, pastel floors.",
    "Y2K platform sneakers, chunky, glittery.",
    "Holographic stickers, aliens and stars, Y2K.",
    "Cyber girl avatar, 2000s graphics, low poly.",
    "Y2K baby blue camo pattern, metallic finish.",
    "Glossy 3D flowers, chrome stems, Y2K vibe.",
    "Retro MP3 player, wired earbuds, neon glow.",
    "Y2K sky aesthetic, pink clouds, pixel stars.",
    "Metallic blue dolphin, water ripples, Y2K.",
    "Cyber world map, digital grid, 2000s tech.",
    "Y2K cherry aesthetic, glossy red, chrome leaf.",
    "Furry steering wheel, Y2K car interior.",
    "2000s fashion magazine collage, Y2K fonts.",
    "Iridescent soap bubbles, metallic background.",
    "Y2K tech hardware, circuit board, neon pink.",
    "Cyber flame pattern, blue and silver.",
    "Y2K headphones, chunky, pastel pink.",
    "Liquid mercury droplets, Y2K futuristic.",
    "2000s internet aesthetic, loading bar, glitter.",
    "Y2K heart sunglasses, pink tint, chrome frame.",
    "Digital pet device, pixel screen, Y2K toy.",
    "Cyber nebula, purple and teal, metallic dust.",
    "Y2K boombox, silver and neon green.",
    "Glossy starburst shapes, Y2K background.",
    "Retro laptop, stickers, Y2K bedroom vibe.",
    "Cyber jewelry, chunky chains, chrome hearts.",
    "Y2K lava lamp, neon blue liquid, metallic base.",
    # 151-200 Pixel Art
    "Pixel art forest, morning mist, 16-bit.",
    "Cozy pixel art kitchen, steaming pie.",
    "Pixel art cyberpunk street, rain, neon signs.",
    "Undersea pixel art, coral reef, colorful fish.",
    "Pixel art mountain cabin, snow falling.",
    "Space station pixel art, stars in window.",
    "Pixel art beach, sunset, low-res waves.",
    "Isometric pixel art room, gamer setup.",
    "Pixel art cat sitting on a fence, moon.",
    "Retro pixel art RPG shop, potions and swords.",
    "Pixel art clouds, pastel sky, 8-bit aesthetic.",
    "Haunted pixel art castle, lightning, spooky.",
    "Pixel art waterfall, lush green jungle.",
    "16-bit pixel art campfire, night forest.",
    "Pixel art train station, rural Japan.",
    "Desert oasis pixel art, palm trees, sun.",
    "Pixel art library, floating magical books.",
    "Retro pixel art car, driving on a highway.",
    "Pixel art floating island, crystals, sky.",
    "Cozy pixel art fireplace, flickering light.",
    "Pixel art flowers, garden, bumblebee.",
    "16-bit pixel art bakery, cakes, cute.",
    "Pixel art lighthouse, stormy sea, night.",
    "Isometric pixel art garden, fountain.",
    "Pixel art coffee shop, lo-fi vibes.",
    "Pixel art winter village, glowing windows.",
    "8-bit pixel art heart, retro game style.",
    "Pixel art meadow, butterflies, sunny day.",
    "Pixel art wizard tower, purple sky.",
    "Retro pixel art cinema, popcorn, neon.",
    "Pixel art bridge over a lily pond.",
    "16-bit pixel art laboratory, green liquid.",
    "Pixel art spaceship interior, buttons, lights.",
    "Pixel art autumn park, orange leaves.",
    "Cozy pixel art attic, telescope, stars.",
    "Pixel art marketplace, fruit stalls.",
    "Retro pixel art pirate ship, ocean.",
    "Pixel art greenhouse, exotic plants.",
    "16-bit pixel art clock tower, evening.",
    "Pixel art farm, sheep, morning sun.",
    "Pixel art cityscape, skyscrapers, night.",
    "Pixel art campfire under the aurora borealis.",
    "Retro pixel art arcade machine, glowing.",
    "Pixel art hot air balloon, colorful sky.",
    "16-bit pixel art sushi bar, aesthetic.",
    "Pixel art rainy window view, blurry street.",
    "Pixel art bamboo forest, panda.",
    "Retro pixel art computer, diskettes.",
    "Pixel art volcanic landscape, lava, dark.",
    "Cozy pixel art bedroom, cat on bed.",
    # 201-250 Vintage Magazine Covers
    "Vintage fashion magazine cover, 1950s style, elegant woman.",
    "Retro travel poster, Italy, mid-century illustration.",
    "1970s vogue aesthetic, grain, warm film colors.",
    "Magazine collage, botanical sketches and vintage text.",
    "Retro 1960s perfume ad, floral background.",
    "Vintage magazine cover, \"Summer in Paris\", chic.",
    "1940s film noir aesthetic magazine, black and white.",
    "Retro \"Science Fiction\" magazine cover, 1950s space.",
    "Vintage botanical magazine, detailed flower sketches.",
    "1980s fitness magazine aesthetic, neon colors.",
    "Retro \"Home & Garden\" cover, mid-century interior.",
    "Vintage fashion sketch magazine, pencil and ink.",
    "1920s Art Deco magazine cover, gold and black.",
    "Retro travel magazine, \"Visit Tokyo\", vintage illustration.",
    "Vintage music magazine, 1970s rock band style.",
    "Magazine collage, old polaroids and handwritten notes.",
    "1950s car advertisement magazine, retro colors.",
    "Vintage \"Lifestyle\" cover, picnic in the park.",
    "Retro holiday magazine, vintage Christmas illustration.",
    "1960s psychedelic magazine cover, vibrant swirls.",
    "Vintage cookbook cover, retro kitchen illustration.",
    "Retro \"Adventure\" magazine, mountain climbing, grainy.",
    "1930s fashion magazine, elegant silhouettes.",
    "Vintage \"Cinema\" magazine cover, classic movie star.",
    "Magazine collage, vintage stamps and maps.",
    "1970s disco magazine aesthetic, glitter, warm tones.",
    "Retro magazine cover, \"Spring Fashion\", pastel colors.",
    "Vintage nature magazine, bird illustrations.",
    "1950s beauty magazine, vintage makeup ad.",
    "Retro \"Future Tech\" magazine, 1960s predictions.",
    "Vintage magazine cover, \"Autumn Styles\", grainy film.",
    "1940s travel magazine, tropical island, vintage.",
    "Retro magazine collage, newspaper clippings, art.",
    "Vintage \"Architecture\" cover, Bauhaus style.",
    "1980s pop culture magazine, vibrant graphics.",
    "Retro magazine cover, \"Winter in Alps\", skiing.",
    "Vintage jewelry ad, 1950s luxury aesthetic.",
    "1970s interior design magazine, retro furniture.",
    "Vintage \"Space Age\" magazine cover, retro rockets.",
    "Magazine collage, pressed flowers and old letters.",
    "1960s youth culture magazine, mod style.",
    "Retro magazine cover, \"City Life\", New York 1950s.",
    "Vintage \"Wild West\" magazine, sepia tones.",
    "1920s jazz magazine cover, art deco motifs.",
    "Retro magazine cover, \"Beach Vibes\", vintage swimsuits.",
    "Vintage coffee ad magazine, 1950s illustration.",
    "1970s photography magazine cover, film grain.",
    "Retro \"Modern Art\" magazine, abstract cover.",
    "Vintage magazine cover, \"Garden Party\", florals.",
    "1950s detective magazine cover, pulp fiction style.",
    # 251-300 Dark Botanical
    "Dark botanical, neon glowing vines on black.",
    "Midnight garden, deep purple roses, moody lighting.",
    "Bioluminescent forest plants, glowing blue and green.",
    "Dark velvet background, gold leaf monstera.",
    "Exotic jungle floor at night, glowing mushrooms.",
    "Deep red dahlias on charcoal background, dramatic.",
    "Neon tropical leaves, pink and teal, dark backdrop.",
    "Dark botanical wallpaper, silver ferns, moody.",
    "Glowing thorns and black roses, gothic aesthetic.",
    "Deep forest moss, bioluminescent spores, dark.",
    "Night blooming jasmine, neon white glow, dark green.",
    "Abstract dark botanical, oil painting, thick texture.",
    "Electric blue ivy on a black stone wall.",
    "Dark moody floral, peonies in shadows, dramatic light.",
    "Neon lotus flower, dark pond, glowing ripples.",
    "Tropical palm leaves, dark purple and gold.",
    "Dark botanical, Victorian gothic style, dried flowers.",
    "Glowing venus flytrap, neon green, dark background.",
    "Deep emerald leaves with neon orange veins.",
    "Dark mystical forest flowers, glowing petals.",
    "Black background, vibrant neon wildflowers.",
    "Dark botanical, macro dragonfly wings and ferns.",
    "Moody dark blue orchids, silver accents.",
    "Neon purple vines wrapping around a dark tree.",
    "Dark botanical, firefly lights in deep bushes.",
    "Crimson lilies, dark background, cinematic lighting.",
    "Glowing forest floor, neon roots, dark.",
    "Dark botanical, gold and black leaf pattern.",
    "Neon hibiscus, dark jungle background, vibrant.",
    "Moody botanical, rainy night, glowing leaves.",
    "Dark background, white neon lilies, sharp contrast.",
    "Bioluminescent underwater plants, dark deep sea.",
    "Dark botanical, copper leaves on black velvet.",
    "Neon cactus garden at night, desert aesthetic.",
    "Moody dark forest, glowing berries, mysterious.",
    "Dark botanical, butterfly with glowing wings on leaf.",
    "Deep teal leaves, neon pink flowers, dark.",
    "Dark gothic garden, black tulips, purple glow.",
    "Neon ferns, dark cave background, glowing.",
    "Dark botanical, silver moonlight on black leaves.",
    "Moody tropical wallpaper, dark shadows, neon pops.",
    "Glowing nectar, dark flowers, bioluminescent bees.",
    "Dark background, rainbow neon vines, abstract.",
    "Deep plum leaves, gold veins, moody botanical.",
    "Dark botanical, neon spider lily, dramatic.",
    "Glowing forest canopy from below, dark night.",
    "Dark background, vibrant neon poppy flowers.",
    "Moody botanical, frost on dark leaves, glowing.",
    "Dark jungle, neon leopard spots through leaves.",
    "Final dark botanical, glowing seeds, black void.",
    # 301-350 Fantasy
    "Floating crystal islands over a sea of clouds, golden hour.",
    "Ancient dragon sleeping inside a glowing gold cavern.",
    "Hidden waterfall city carved into a giant mountain.",
    "Mystical library with floating glowing books and stardust.",
    "Giant world-tree with bioluminescent leaves at midnight.",
    "A portal opening in a desert, showing a lush jungle inside.",
    "Phoenix rising from blue flames, cinematic fantasy art.",
    "Underwater palace made of coral and glowing pearls.",
    "Knight standing before a colossal stone golem in the fog.",
    "Enchanted forest with giant mushrooms and floating spores.",
    "Celestial goddess made of stars holding a small planet.",
    "Gothic castle perched on a floating jagged rock, lightning.",
    "Secret garden with silver grass and glass-petal flowers.",
    "Steampunk airship sailing through a canyon of crystals.",
    "Ancient ruins with glowing blue runes, overgrown with vines.",
    "Wizard's tower on a cliff, aurora borealis in the sky.",
    "Path of glowing lotuses leading to a moonlit temple.",
    "Giant turtle carrying a miniature village on its back.",
    "Frozen kingdom with ice sculptures and diamond dust air.",
    "A bridge made of rainbows over a misty abyss.",
    "Dark elf city illuminated by purple fungi, subterranean.",
    "Fire and ice dragons clashing in a dramatic sky.",
    "Floating jellyfish-like creatures in a purple alien sky.",
    "Abandoned throne room with sunlight hitting a dusty crown.",
    "Sacred grove with a white stag glowing in the shadows.",
    "Volcanic forge with flowing lava and obsidian anvils.",
    "Clockwork forest with metal trees and golden gears.",
    "Dreamlike valley with giant floating bubbles and soft light.",
    "Samurai duel on a lake of mirrors, cherry blossom rain.",
    "Colossal skeleton of a titan overgrown with red flowers.",
    "Pegasus flying over a field of lavender and silver clouds.",
    "Alchemy lab with bubbling neon potions and smoke.",
    "A stairway to heaven made of glowing white light.",
    "Mystical oasis with liquid gold water in a dark desert.",
    "Forest of giant sunflowers taller than houses, fantasy style.",
    "Dark warlock's lair with green soul-fire and skulls.",
    "Celestial map painted on a night sky, glowing constellations.",
    "Underground lake with glowing blue fish and stalactites.",
    "Fairy circle in a dark woods, glowing mushrooms, magic dust.",
    "Ancient stone gate leading to a dimension of pure light.",
    "Flying whales over a sunset ocean, dreamcore fantasy.",
    "Valkyrie on a white horse riding through a golden cloud.",
    "Mirror lake reflecting a city that doesn't exist above.",
    "Cursed forest with black trees and glowing red eyes.",
    "Throne of swords in a ruined hall, cinematic lighting.",
    "Floating lanterns over a mystical river, night festival.",
    "Giant hourglass in the desert with stars falling instead of sand.",
    "Ice phoenix perched on a frozen spire, blue glow.",
    "Hidden valley of dragons, lush green and ancient.",
    "Cosmic nebula shaped like a giant eye, fantasy space art.",
    # 351-400 Cinematic
    "Rain-slicked cyberpunk street, neon reflection, 35mm film.",
    "Lone astronaut standing on a red desert planet, wide shot.",
    "Dramatic portrait of a hooded figure, side lighting, shadows.",
    "Foggy harbor at dawn, vintage ship silhouette, cinematic.",
    "High-speed car chase in a futuristic tunnel, motion blur.",
    "Abandoned diner in the middle of nowhere, sunset, moody.",
    "Noir detective office, smoke, venetian blind shadows.",
    "Astronaut sitting on a moon rock looking at Earth, epic scale.",
    "Overgrown post-apocalyptic city, sunlight hitting skyscrapers.",
    "Intense close-up of a human eye reflecting a galaxy.",
    "Cold mountain pass, lone traveler with a lantern, blizzard.",
    "Retro 1970s film aesthetic, a convertible on a coastal road.",
    "Cyberpunk alleyway, steam rising from vents, blue and red.",
    "Cinematic wide shot of a futuristic mega-city at night.",
    "Empty theater hall, single spotlight on center stage.",
    "Dusty library, sunlight beams through high windows, 8k.",
    "Space station window view, Saturn's rings, cinematic lighting.",
    "Forest fire at night, silhouette of a deer, dramatic embers.",
    "Underwater diver discovering a glowing sunken city.",
    "Desert dunes at night, moonlight, deep shadows, cinematic.",
    "A lone lighthouse in a massive storm, crashing waves.",
    "Futuristic cockpit view, hyperspace stars, cinematic.",
    "Vintage train station, steam, travelers in long coats, 1940s.",
    "Minimalist cinematic landscape, black sand beach, white sky.",
    "Cyberpunk hacker room, multiple screens, green code glow.",
    "Cinematic sunset over a canyon, warm orange and deep teal.",
    "Abandoned space shuttle in a jungle, vines, cinematic grain.",
    "Macro shot of a circuit board, neon pulses, futuristic.",
    "Samurai standing in a bamboo forest, fog, cinematic mood.",
    "High-fashion model in a desert, dramatic flowing fabric.",
    "Rain hitting a window, city lights blurred (bokeh), cinematic.",
    "A lonely robot sitting on a cliff looking at the sunset.",
    "Dramatic volcano eruption, dark ash clouds, red lava glow.",
    "1950s suburbia aesthetic, cinematic lighting, perfect lawn.",
    "Underwater view looking up at a boat, cinematic sun rays.",
    "A secret bunker with vintage computers and maps, moody.",
    "Futuristic bridge over a misty valley, blue hour.",
    "Intense lightning strike over a dark ocean, cinematic.",
    "Grand ballroom with a crystal chandelier, dark shadows.",
    "Close-up of a hand touching a holographic interface.",
    "Cinematic winter, a cabin with smoke from the chimney.",
    "Neon-lit boxing ring in a dark warehouse, smoke.",
    "A field of wheat under a storm sky, cinematic contrast.",
    "Futuristic gladiator arena, holographic crowd, sand.",
    "Steaming ramen shop in a rainy alley, cinematic warmth.",
    "A lone biker on an endless desert highway, golden hour.",
    "High-tech laboratory, liquid nitrogen vapor, blue LEDs.",
    "Cinematic forest, morning mist, god rays through trees.",
    "A giant satellite dish in the desert, milky way above.",
    "Final scene aesthetic, a figure walking into a bright light."
]

# -----------------------------
# Fikir Seç
# -----------------------------
def get_idea():
    base_prompt = random.choice(ideas)
    captions = ["Ethereal Silence", "Quiet Elegance", "Timeless Serenity", "Whispers of Light", "Pure Harmony", "Endless Calm", "Soft Eternity", "Minimal Dream", "Dark Whisper", "Neon Memory", "Shadows Embrace", "Mystic Void", "Lost in Stars", "Frozen Moment", "Eternal Night"]
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
# Tweet At - 100 KEZ DENE (403 dahil pes etme!)
# -----------------------------
def tweet_image(img_bytes, caption):
    promo_options = [
        "🖤 Instant digital download on Etsy!",
        "✨ Grab the high-res version on my shop!",
        "🌙 Available now – instant download!",
        "💎 Full quality wallpaper on Etsy 👇",
        "🔗 Download this beauty instantly!"
    ]
    promo_text = random.choice(promo_options)
    
    text = f"{caption}\n\n{promo_text}\nhttps://www.etsy.com/shop/SiyahHavyarArt\n\n{get_hashtag()} {get_hashtag()} {get_etsy_hashtag()} #AIArt #Wallpaper #DigitalArt #EtsySeller"
    
    filename = "siyahhavyar_wallpaper.png"
    
    try:
        with open(filename, "wb") as f:
            f.write(img_bytes)

        max_attempts = 100
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"📤 Tweet denemesi {attempt}/100...")
                
                auth_v1 = OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
                api_v1 = API(auth_v1)
                media = api_v1.media_upload(filename)
                
                client = Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                                access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
                client.create_tweet(text=text, media_ids=[media.media_id_string])
                
                print("🎉 TWEET BAŞARIYLA ATILDI! (Deneme {}'de başarılı) 🖤✨".format(attempt))
                return True
                
            except Exception as e:
                print(f"❌ Deneme {attempt} başarısız: {e}")
                if attempt < max_attempts:
                    print("⏳ 15 saniye bekleniyor, yeniden denenecek...\n")
                    time.sleep(15)
                else:
                    print("💔 100 deneme tamamlandı, tweet atılamadı. (Free tier medya kısıtlaması olabilir)")
        
        return False
        
    except Exception as e:
        print(f"❌ Dosya yazma hatası: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# -----------------------------
# ANA
# -----------------------------
print("\n🚀 Siyah Havyar Art Bot başlıyor... (400 tema + 100 deneme modu)\n")

prompt, caption = get_idea()
print(f"🎨 Seçilen tema: {prompt}")
print(f"💬 Caption: {caption}\n")

img = generate_image(prompt)

if img:
    print("\n🖼️ Resim üretildi! Tweet için maksimum 100 kez denenecek...\n")
    if tweet_image(img, caption):
        print("\n✅ Başarı! Resimli tweet atıldı.")
    else:
        print("\n❌ Tüm denemelere rağmen tweet atılamadı.")
else:
    print("\n⚠️ Resim üretilemedi.")

print("\nBitti. Siyah Havyar pes etmez! 🖤🔥")
