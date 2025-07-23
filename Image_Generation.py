import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv, get_key
import os
from time import sleep

# Load .env and API Key
load_dotenv()
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {'Authorization': f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Output folder
OUTPUT_FOLDER = "Data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🚫 NSFW keyword list
NSFW_KEYWORDS = [[
    "nude", "nudity", "naked", "sex", "sexual", "erotic", "fetish", "porn", "pornographic",
    "boobs", "breasts", "nipples", "cleavage", "panties", "thong", "underwear", "bikini",
    "lingerie", "strip", "stripping", "orgasm", "cum", "ejaculation", "masturbate", "masturbation",
    "genitals", "penis", "vagina", "dildo", "anal", "butt", "ass", "buttocks", "tits", "fuck",
    "fucking", "suck", "sucking", "blowjob", "bdsm", "bondage", "incest", "hentai", "xxx", "nsfw"
]
]  # You can add keywords like ["nude", "explicit", "nsfw"] here

# ⚠️ Prompt filter function
def is_safe_prompt(prompt: str) -> bool:
    lowered = prompt.lower()
    for keyword in NSFW_KEYWORDS:
        if keyword in lowered:
            return False
    return True

# 🖼️ Open generated images
def open_image():
    files = [f"{i}.png" for i in range(1, 5)]
    for file_name in files:
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        try:
            img = Image.open(file_path)
            print(f"🖼️ Opening image: {file_path}")
            img.show()
            sleep(1)
        except IOError as e:
            print(f"❌ Error opening image {file_path}: {e}")

# 📤 Query API
async def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None

# 🧠 Generate images using HuggingFace SDXL
async def generate_image(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(OUTPUT_FOLDER, f"{i + 1}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

# 🔁 High-level generator
def GenerateImages(prompt: str):
    if not is_safe_prompt(prompt):
        print(f"🚫 Unsafe prompt detected: '{prompt}' — Image generation blocked.")
        return
    asyncio.run(generate_image(prompt))
    open_image()
    print(f"✅ Images generated for prompt: {prompt}")

# 🔄 Main polling loop
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) >= 2:
            Prompt = "".join(lines[:-1]).strip()
            Status = lines[-1].strip()
        else:
            sleep(1)
            continue

        if Status == "True":
            print("🧠 Generating Images...")
            GenerateImages(prompt=Prompt)
            with open(r"Frontend\Files\ImageGeneration.data", "w", encoding="utf-8") as f:
                f.write("False\nFalse")
        else:
            sleep(1)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        sleep(1)
