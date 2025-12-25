import os
import time
import json
import random
import requests
from datetime import datetime

from tweepy import OAuthHandler, API, Client

try:
    import google.genai as genai
except ImportError:
    genai = None

# =============================
# ENV
# =============================

API_KEY       = os.getenv("API_KEY")
API_SECRET    = os.getenv("API_SECRET")
ACCESS_TOKEN  = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

MEMORY_FILE = "memory.json"

# =============================
# MEMORY SYSTEM
# =============================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_to_memory(prompt, caption):
    memory = load_memory()
    memory.append({
        "time": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "caption": caption
    })
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory[-50:], f, indent=2)  # son 50 işi tut

def summarize_memory(memory):
    if not memory:
        return "No previous works yet."
    return "\n".join(
        f"- {m['prompt'][:120]}" for m in memory[-10:]
    )

# =============================
# AUTONOMOUS IDEA GENERATOR
# =============================

def get_autonomous_idea():
    memory = load_memory()
    memory_summary = summarize_memory(memory)

    instruction_prompt = f"""
You are an autonomous digital artist.

You design mobile phone wallpapers.
No one tells you what to create.
You decide entirely on your own.

You remember what you created before.
You actively avoid repeating ideas, moods, compositions, or concepts.

Previous works (summarized):
{memory_summary}

Think like a real artist:
- Ask yourself what you have NOT explored yet
- Choose a new direction, mood, or concept
- Create something original and different from your past work

Rules:
- Safe for all audiences
- No sexual content
- No explicit violence
- Original concepts only

Output EXACTLY two lines:

PROMPT: <A detailed English image description for a vertical phone wallpaper (9:21)>
CAPTION: <A short thoughtful English caption>
"""

    # GROQ
    if GROQ_KEY:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": instruction_prompt}],
                "temperature": 1.4,
                "max_tokens": 600
            },
            timeout=30
        )
        text = r.json()["choices"][0]["message"]["content"]
    elif GEMINI_KEY and genai:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        text = model.generate_content(instruction_prompt).text
    else:
        raise RuntimeError("No AI provider available")

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    prompt = next(l for l in lines if l.startswith("PROMPT:"))[7:].strip()
    caption = next(l for l in lines if l.startswith("CAPTION:"))[8:].strip()

    save_to_memory(prompt, caption)
    return prompt, caption

# =============================
# IMAGE GENERATION (AI HORDE)
# =============================

def generate_image(prompt):
    payload = {
        "prompt": f"{prompt}, vertical phone wallpaper, 9:21",
        "params": {"width": 640, "height": 1408, "steps": 25},
        "nsfw": False,
        "models": ["Juggernaut XL"]
    }

    r = requests.post(
        "https://stablehorde.net/api/v2/generate/async",
        headers={"Client-Agent": "AutonomousArtistBot"},
        json=payload
    )
    task_id = r.json()["id"]

    while True:
        time.sleep(20)
        s = requests.get(
            f"https://stablehorde.net/api/v2/generate/status/{task_id}"
        ).json()
        if s["done"] and s["generations"]:
            return requests.get(s["generations"][0]["img"]).content

# =============================
# POST TO TWITTER
# =============================

def post_to_twitter(image, caption):
    with open("wallpaper.png", "wb") as f:
        f.write(image)

    auth = OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = API(auth)
    media = api.media_upload("wallpaper.png")

    client = Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    client.create_tweet(
        text=caption[:280],
        media_ids=[media.media_id]
    )

    os.remove("wallpaper.png")

# =============================
# MAIN LOOP (2 HOURS)
# =============================

if __name__ == "__main__":
    print("🎨 Autonomous Artist Bot started", flush=True)

    while True:
        try:
            prompt, caption = get_autonomous_idea()
            image = generate_image(prompt)
            post_to_twitter(image, caption)
            print("✅ Posted. Sleeping 2 hours.", flush=True)
        except Exception as e:
            print(f"⚠️ Error: {e}", flush=True)

        time.sleep(7200)
