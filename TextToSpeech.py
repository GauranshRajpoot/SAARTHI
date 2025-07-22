import pygame
import random
import asyncio
import edge_tts
import os
import re
from dotenv import dotenv_values

# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)

# Load voice config from .env
env_vars = dotenv_values(".env")
Assistantvoice = env_vars.get("Assistantvoice")

# Async function to convert text to audio file
async def TextToAudioFile(text, file_path) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, voice=Assistantvoice, pitch="+5Hz", rate="+13%")
    await communicate.save(file_path)

# Low-level TTS player
def TTS(Text, func=lambda r=None: True):
    file_path = r"Data\speech.mp3"
    try:
        asyncio.run(TextToAudioFile(Text, file_path))
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
        return True
    except Exception as e:
        print(f"Error in TTS: {e}")
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error Final TTS: {e}")

# High-level interface with long-text handling
def TextToSpeech(text, callback=lambda r=None: True):
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    Data = re.split(r'(?<=[.!?]) +', text.strip())

    if len(Data) > 5 and len(text) >= 250:
        intro = " ".join(Data[0:2])
        TTS(intro + " " + random.choice(responses), func=callback)
    else:
        TTS(text, func=callback)

# Demo mode
if __name__ == "__main__":
    while True:
        user_input = input("Enter The Text: ")
        TextToSpeech(user_input)
