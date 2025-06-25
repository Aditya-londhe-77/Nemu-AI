import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
from io import BytesIO

def open_image(prompt):
    folder_path = "Data"
    prompt_clean = prompt.replace(" ", "_")
    file_name = f"{prompt_clean}1.jpg"
    image_path = os.path.join(folder_path, file_name)

    try:
        img = Image.open(image_path)
        print(f"Opening image: {image_path}")
        img.show()
    except IOError:
        print(f"Unable to open {image_path}")


API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = get_key('.env', 'HuggingFaceAPIKey')
print(f"Using Hugging Face API Key: {API_KEY[:6]}********")  
headers = {"Authorization": f"Bearer {API_KEY}"}


async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text}")
        return None

    return response.content


async def generate_image(prompt: str):
    prompt_clean = prompt.replace(" ", "_")
    seed = randint(0, 1000000)
    print(f"Generating image with seed: {seed}")
    
    payload = {
        "inputs": f"{prompt}, 4K, ultra detailed, high resolution, seed={seed}"
    }

    image_bytes = await query(payload)

    if not image_bytes:
        print("Image generation failed.")
        return

    try:
        Image.open(BytesIO(image_bytes)).verify()
    except Exception as e:
        print(f"Image verification failed: {e}")
        return

    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{prompt_clean}1.jpg")

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    print(f"Image saved at: {file_path}")


def GenerateImage(prompt: str):
    asyncio.run(generate_image(prompt))
    open_image(prompt)


def main_loop():
    image_data_path = os.path.join("Frontend", "Files", "ImageGeneration.data")

    while True:
        try:
            with open(image_data_path, "r") as f:
                data = f.read().strip()

            print(f"Read from file: '{data}'")
            if not data:
                sleep(1)
                continue

            Prompt, Status = map(str.strip, data.split(","))

            if Status == "True":
                print("Trigger detected: Generating image ...")
                GenerateImage(prompt=Prompt)

                with open(image_data_path, "w") as f:
                    f.write("False,False")

                break

            sleep(1)

        except Exception as e:
            print(f"Error in main loop: {e}")
            sleep(1)

if __name__ == "__main__":
    main_loop()
