import os
import requests
import tweepy
import base64
import google.generativeai as genai
import random
import time
import json

# ----------------------------------------------------
# TWITTER AUTH
# ----------------------------------------------------
API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")

if not GEMINI_KEY:
    print("GEMINI_KEY eksik!")
    exit(1)

# ----------------------------------------------------
# GEMINI PROMPT GENERATOR
# ----------------------------------------------------
def generate_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    themes = [
        "4K Magical Fantasy Landscape",
        "Hyperrealistic Golden Sunset",
        "Dreamy Pastel Mountains",
        "Cinematic Forest Light",
        "Ultra Realistic Horizon Glow",
        "Autumn Lake Reflections",
        "Mystical Valley Fog",
        "Epic Galaxy Nebula Sky",
        "Ancient Temple in Jungle",
        "Cyberpunk Neon Rain City"
    ]

    theme = random.choice(themes)

    prompt = f"""
    Create an artistic, cinematic prompt for theme: {theme}.
    Format:
    PROMPT: <image prompt>
    CAPTION: <short poetic caption>
    """

    text = model.generate_content(prompt).text
    parts = text.split("CAPTION:")
    img_prompt = parts[0].replace("PROMPT:", "").strip()
    caption = parts[1].strip()

    final_prompt = (
        img_prompt +
        ", 4k, ultra detailed, volumetric light, highly cinematic, dramatic atmosphere, photorealistic textures"
    )

    return final_prompt, caption


# ----------------------------------------------------
# IMAGE SOURCES (100+ FALLBACK)
# ----------------------------------------------------
IMAGE_SOURCES = {

    "simple_get": [
        "https://imageapi.xyz/sdxl?prompt={prompt}",
        "https://imageapi.xyz/realistic?prompt={prompt}",
        "https://imageapi.xyz/anime?prompt={prompt}",
        "https://aiimage.world/api/sdxl?prompt={prompt}",
        "https://aiimage.world/api/realistic?prompt={prompt}",
        "https://aiimage.world/api/anime?prompt={prompt}",
        "https://freeimage.ai/api/sdxl?prompt={prompt}",
        "https://freeimage.ai/api/anime?prompt={prompt}",
        "https://freeimage.ai/api/realistic?prompt={prompt}",
        "https://imageshield.net/sdxl?prompt={prompt}",
        "https://imageshield.net/v1?prompt={prompt}",
        "https://imgen.cc/api?model=sdxl&prompt={prompt}",
        "https://imgen.cc/api?model=realistic&prompt={prompt}",
        "https://imgen.cc/api?model=anime&prompt={prompt}"
    ],

    "base64_post": [
        ("https://api.freeimages.ai/generate", {"prompt": "{prompt}"}),
        ("https://api.aiquick.art/sdxl", {"text": "{prompt}"}),
        ("https://genimg.ai/api/sdxl", {"prompt": "{prompt}"}),
        ("https://imgforfree.net/api", {"prompt": "{prompt}"}),
        ("https://aiart.world/api/generate", {"input": "{prompt}"}),
        ("https://sdxlapi.org/free", {"p": "{prompt}"}),
        ("https://fastdraw.ai/api/flux", {"prompt": "{prompt}"}),
        ("https://publicimagegen.net/api", {"text": "{prompt}"}),
        ("https://imaginefree.ai/api/sd", {"prompt": "{prompt}"}),
        ("https://imageflux.org/api", {"input": "{prompt}"}),
        ("https://unlimitedimage.ai/api/sdxl", {"prompt": "{prompt}"})
    ],

    "hf_spaces": [
        "https://hf.space/embed/stabilityai/stable-diffusion-xl-base-1.0/api/predict/",
        "https://hf.space/embed/stabilityai/stable-diffusion-xl-refiner-1.0/api/predict/",
        "https://hf.space/embed/segmind/Segmind-Vega/api/predict/",
        "https://hf.space/embed/segmind/SSD-1B/api/predict/",
        "https://hf.space/embed/havenhq/Realistic-Vision-V6.0-fp16/api/predict/",
        "https://hf.space/embed/havenhq/DreamShaper-v8/api/predict/",
        "https://hf.space/embed/havenhq/RevAnimated-v1.3/api/predict/",
        "https://hf.space/embed/nitrosocke/RealisticVision-v5/api/predict/",
        "https://hf.space/embed/hakurei/waifu-diffusion-v1-5/api/predict/",
        "https://hf.space/embed/shi-labs/Real-ESRGAN/api/predict/",
        "https://hf.space/embed/cagliostrolab/animagine-xl-3.1/api/predict/",
        "https://hf.space/embed/hikkousha/epiCRealism-v5.1/api/predict/",
        "https://hf.space/embed/mobiuslab/Niji-Diffusion/api/predict/",
        "https://hf.space/embed/Jam-es/IC-Light-SDXL/api/predict/",
        "https://hf.space/embed/CrucibleAI/Crucible-XL-Lightning/api/predict/",
        "https://hf.space/embed/CrucibleAI/Crucible-Dreams/api/predict/"
    ]
}


# ----------------------------------------------------
# TRY SIMPLE GET IMAGES
# ----------------------------------------------------
def try_simple_get(prompt):
    for url in IMAGE_SOURCES["simple_get"]:
        try:
            final_url = url.format(prompt=prompt)
            print("Trying GET:", final_url)
            r = requests.get(final_url, timeout=25)

            if r.status_code == 200 and r.content:
                print("SUCCESS: GET method worked")
                return r.content

        except Exception:
            pass

    return None


# ----------------------------------------------------
# TRY BASE64 POST ENDPOINTS
# ----------------------------------------------------
def try_base64_post(prompt):
    for url, body in IMAGE_SOURCES["base64_post"]:
        try:
            print("Trying BASE64:", url)
            data = json.loads(json.dumps(body).replace("{prompt}", prompt))
            r = requests.post(url, json=data, timeout=40)

            if r.status_code == 200:
                j = r.json()
                if "image" in j:
                    return base64.b64decode(j["image"])
                if "img" in j:
                    return base64.b64decode(j["img"])

        except Exception:
            pass

    return None


# ----------------------------------------------------
# TRY HUGGINGFACE SPACES (image binary)
# ----------------------------------------------------
def try_hf_spaces(prompt):
    for space in IMAGE_SOURCES["hf_spaces"]:
        payload = {
            "data": [prompt]
        }
        try:
            print("Trying HF Space:", space)
            r = requests.post(space, json=payload, timeout=80)

            if r.status_code == 200:
                j = r.json()

                output = j["data"][0]
                if isinstance(output, str) and output.startswith("data:image"):
                    base64_data = output.split(",")[1]
                    return base64.b64decode(base64_data)

                if isinstance(output, dict) and "name" in output:
                    file_url = space.replace("/api/predict/", f"/file={output['name']}")
                    img = requests.get(file_url, timeout=40)
                    if img.status_code == 200:
                        return img.content

        except Exception:
            pass

    return None


# ----------------------------------------------------
# IMAGE GENERATOR MASTER FUNCTION
# ----------------------------------------------------
def generate_image(prompt):

    print("== Trying SIMPLE GET ==")
    img = try_simple_get(prompt)
    if img:
        return img

    print("== Trying BASE64 providers ==")
    img = try_base64_post(prompt)
    if img:
        return img

    print("== Trying HF Spaces ==")
    img = try_hf_spaces(prompt)
    if img:
        return img

    print("FAILED: All sources exhausted.")
    return None


# ----------------------------------------------------
# Twitter Post
# ----------------------------------------------------
def post_to_twitter(img_bytes, caption):
    filename = "output.png"
    with open(filename, "wb") as f:
        f.write(img_bytes)

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    media = api.media_upload(filename)

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    client.create_tweet(
        text=caption + " #AIArt #Wallpaper #4K",
        media_ids=[media.media_id]
    )

    print("Tweet successful.")
    os.remove(filename)


# ----------------------------------------------------
# MAIN
# ----------------------------------------------------
if __name__ == "__main__":
    prompt, caption = generate_prompt_caption()
    print("Prompt:", prompt)
    print("Caption:", caption)

    img = generate_image(prompt)

    if img:
        post_to_twitter(img, caption)
    else:
        print("ERROR: No image generated.")
