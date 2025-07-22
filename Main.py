from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetAssistantStatus,
    GetMicrophoneStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import real_time_search_engine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import threading
import json
import subprocess
import logging
import os
import sys

# ────────────────────────
# 🔧 Initial Setup
# ────────────────────────
logging.getLogger("WDM").setLevel(logging.CRITICAL)
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f"""{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?"""

SupportedFunctions = [
    "exit", "open", "close", "play", "generate image", "reminder", "system",
    "content", "google search", "youtube search",
    "create file", "delete file", "create folder", "delete folder", "whatsapp"
]

# ────────────────────────
# 📁 Chat Log Handling
# ────────────────────────
def ShowChatsIfNoChats():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as File:
        if len(File.read()) < 5:
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username} {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as File:
        Data = File.read()
    if len(Data) > 0:
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as File:
            File.write(Data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowChatsIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# ────────────────────────
# 🧠 Main Assistant Logic
# ────────────────────────
def MainExecution():
    try:
        task_executed = False
        image_requested = False
        image_query = ""

        SetAssistantStatus("Listening...")
        query = SpeechRecognition()
        ShowTextToScreen(f'{Username}: {query}')
        SetAssistantStatus("Thinking...")

        decision = FirstLayerDMM(query)
        print(f"\nDecision: {decision}\n")

        is_general = any(d.startswith("general") for d in decision)
        is_realtime = any(d.startswith("realtime") for d in decision)

        merged_query = " and ".join(
            [" ".join(d.split()[1:]) for d in decision if d.startswith("general") or d.startswith("realtime")]
        )

        # 🖼️ Detect image generation
        for d in decision:
            if 'generate' in d:
                image_query = query
                image_requested = True

        # ⚙️ Execute automation task
        for d in decision:
            if not task_executed and any(d.startswith(func) for func in SupportedFunctions):
                try:
                    run(Automation(list(decision)))
                    task_executed = True
                except Exception as e:
                    print(f"Automation Error: {e}")

        # 🧠 Generate image
        if image_requested:
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{image_query},True")
            try:
                subprocess.run(
                    ['python', r"Backend\Image_Generation.py"],
                    timeout=60  # ⏱️ Increased timeout
                )
                # Or use non-blocking: subprocess.Popen([...])
            except subprocess.TimeoutExpired:
                msg = "Image generation timed out. Please try a simpler prompt."
                print(msg)
                ShowTextToScreen(f"{Assistantname}: {msg}")
                TextToSpeech(msg)
            except Exception as e:
                msg = f"Image Generation Error: {e}"
                print(msg)
                ShowTextToScreen(f"{Assistantname}: Failed to generate the image.")
                TextToSpeech("Sorry, something went wrong with image generation.")

        # 🔍 Real-time search
        if is_realtime:
            try:
                SetAssistantStatus("Searching...")
                answer = real_time_search_engine(QueryModifier(merged_query))
                ShowTextToScreen(f"{Assistantname}: {answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(answer)
            except Exception as e:
                print(f"Real-time Search Error: {e}")
                ShowTextToScreen(f"{Assistantname}: Sorry, I couldn't fetch the info.")
                TextToSpeech("Sorry, I couldn't fetch the info.")
            return True

        # 💬 General response
        for d in decision:
            if d.startswith("general"):
                query_final = d.replace("general", "").strip()
                answer = Chatbot(QueryModifier(query_final))
                ShowTextToScreen(f"{Assistantname}: {answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(answer)
                return True

            elif d.startswith("realtime"):
                query_final = d.replace("realtime", "").strip()
                try:
                    answer = real_time_search_engine(QueryModifier(query_final))
                    ShowTextToScreen(f"{Assistantname}: {answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(answer)
                except Exception as e:
                    print(f"Realtime Subquery Error: {e}")
                return True

            elif d == "exit":
                answer = Chatbot(QueryModifier("Okay Bye!"))
                ShowTextToScreen(f"{Assistantname}: {answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(answer)
                sys.exit()

    except Exception as e:
        print(f"⚠️ Fatal Error in MainExecution: {e}")
        ShowTextToScreen(f"{Assistantname}: Something went wrong.")
        SetAssistantStatus("Available...")

# ────────────────────────
# 🎙️ Continuous Listening
# ────────────────────────
def FirstThread():
    while True:
        mic_status = GetMicrophoneStatus()
        if mic_status == "True" or mic_status is True:
            if GetAssistantStatus() != "Listening...":
                SetAssistantStatus("Listening...")
            MainExecution()
        else:
            if GetAssistantStatus() != "Available...":
                SetAssistantStatus("Available...")
        sleep(0.1)

# ────────────────────────
# 🖼️ Launch GUI
# ────────────────────────
def SecondThread():
    GraphicalUserInterface()

# ────────────────────────
# 🚀 Entry Point
# ────────────────────────
if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()
