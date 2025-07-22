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

# Ensure output folder exists
OUTPUT_FOLDER = "Data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def open_image(prompt):
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.png" for i in range(1, 5)]

    for file_name in files:
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        try:
            img = Image.open(file_path)
            print(f"🖼️ Opening image: {file_path}")
            img.show()
            sleep(1)  # Allow viewer to load
        except IOError as e:
            print(f"❌ Error opening image {file_path}: {e}")

async def query(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None

async def generate_image(prompt: str):
    tasks = []
    prompt_clean = prompt.replace(" ", "_")

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Only save valid images
            file_path = os.path.join(OUTPUT_FOLDER, f"{prompt_clean}{i + 1}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

def GenerateImages(prompt: str):
    asyncio.run(generate_image(prompt))
    open_image(prompt)
    print(f"✅ Images generated for prompt: {prompt}")

# 🔁 Main loop (polls trigger file)
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data: str = f.read()
        Prompt, Status = data.strip().split(",")

        if Status == "True":
            print("🧠 Generating Images...")
            GenerateImages(prompt=Prompt)
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            # remove 'break' to keep listening in loop
        else:
            sleep(1)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        sleep(1)
