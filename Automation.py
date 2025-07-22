# ─────────────────────────────
# SAARTHI Automation Engine
# ─────────────────────────────

# 📦 Imports
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from rich.logging import RichHandler
from groq import Groq
import subprocess
import os
import requests
import keyboard
import asyncio
import logging
import pyautogui
import time
import re
import psutil
from datetime import datetime

# 🧠 Logger Setup
logging.basicConfig(level="INFO", handlers=[RichHandler()])
logger = logging.getLogger("saarthi")

# 🔐 Environment Variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# 🌐 User Agent for Web Scraping Fallback
useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
)

# 🤖 Groq API Init
client = Groq(api_key=GroqAPIKey)
SystemChatBot = [
    {
        "role": "system",
        "content": (
            "Hello, I am your content writer. You have to write content like "
            "letters, songs, articles, codes, applications, essays, notes, poems etc. "
            "Write in a professional and neat format."
        ),
    }
]

messages: list[dict] = []

# ─────────────────────────────
# 🔍 Web & Content Functions
# ─────────────────────────────

def GoogleSearch(topic: str) -> bool:
    search(topic)
    return True

def YoutubeSearch(topic: str) -> None:
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)

def PlayYoutube(topic: str) -> bool:
    playonyt(topic)
    return True

def ContentWriterAI(prompt: str) -> str:
    messages.append({"role": "user", "content": prompt})
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        messages.append({"role": "assistant", "content": answer})
        return answer.strip()
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return "Sorry, I couldn't generate the content at this time."

def Content(topic: str) -> bool:
    def OpenNotePad(file_path: str | None = None) -> None:
        subprocess.Popen(["notepad.exe", file_path] if file_path else ["notepad.exe"])

    topic = topic.replace("Content", "").strip()
    content_by_ai = ContentWriterAI(topic)
    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{topic.lower().replace(' ', '_')}.txt")
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content_by_ai)
        OpenNotePad(file_path)
        return True
    except Exception as e:
        logger.error(f"Failed to write or open content file: {e}")
        return False

# ─────────────────────────────
# 🖥️ App Control Functions
# ─────────────────────────────

def OpenApp(app: str, sess=requests) -> bool:
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        def extract_links(html: str | None) -> list[str]:
            if html is None: return []
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", {"jsname": "UWckNb"})
            return [link.get("href") for link in links]
        def search_google(query: str) -> str | None:
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None
        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def CloseApp(app: str) -> bool:
    if "chrome" in app.lower():
        logger.info("Skipping Chrome auto-close for safety.")
        return True
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False

# ─────────────────────────────
# 🧩 System Commands
# ─────────────────────────────

def System(command: str):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume mute")
    def up(): keyboard.press_and_release("volume up")
    def down(): keyboard.press_and_release("volume down")
    def stats():
        batt = psutil.sensors_battery()
        battery_pct = batt.percent if batt else "N/A"
        cpu_pct = psutil.cpu_percent(interval=1)
        ram_pct = psutil.virtual_memory().percent
        info = (
            f"[System-Stats {datetime.now().strftime('%H:%M:%S')}] "
            f"Battery: {battery_pct}% | CPU: {cpu_pct}% | RAM: {ram_pct}%"
        )
        print(info)
        logger.info(info)
        return info

    match command:
        case "mute": mute()
        case "unmute": unmute()
        case "volume up": up()
        case "volume down": down()
        case "stats" | "system stats": return stats()
    return True

# ─────────────────────────────
# 📁 File / Folder Operations
# ─────────────────────────────

def CreateFile(filepath: str = "Data/newfile.txt") -> bool:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("")
        print(f"[green]File created:[/green] {filepath}")
        return True
    except Exception as e:
        logger.error(f"File creation failed: {e}")
        return False

def DeleteFile(filepath: str) -> bool:
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"[red]File deleted:[/red] {filepath}")
            return True
        else:
            logger.warning("File not found.")
            return False
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        return False

def CreateFolder(folderpath: str = "Data/NewFolder") -> bool:
    try:
        os.makedirs(folderpath, exist_ok=True)
        print(f"[green]Folder created:[/green] {folderpath}")
        return True
    except Exception as e:
        logger.error(f"Folder creation failed: {e}")
        return False

def DeleteFolder(folderpath: str) -> bool:
    try:
        if os.path.exists(folderpath) and os.path.isdir(folderpath):
            os.rmdir(folderpath)
            print(f"[red]Folder deleted:[/red] {folderpath}")
            return True
        else:
            logger.warning("Folder not found or not empty.")
            return False
    except Exception as e:
        logger.error(f"Folder deletion failed: {e}")
        return False

# ─────────────────────────────
# 🧠 Command Dispatcher
# ─────────────────────────────

async def TranslateAndExecute(commands: list[str]):
    tasks = []
    for command in commands:
        cmd = command.lower().strip()

        if cmd.startswith("open "):
            tasks.append(asyncio.to_thread(OpenApp, cmd.removeprefix("open ").strip()))

        elif cmd.startswith("close "):
            tasks.append(asyncio.to_thread(CloseApp, cmd.removeprefix("close ").strip()))

        elif cmd.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd.removeprefix("play ").strip()))

        elif cmd.startswith("content "):
            tasks.append(asyncio.to_thread(Content, cmd.removeprefix("content ").strip()))

        elif cmd.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search ").strip()))

        elif cmd.startswith("youtube search "):
            tasks.append(asyncio.to_thread(YoutubeSearch, cmd.removeprefix("youtube search ").strip()))

        elif cmd.startswith("system "):
            tasks.append(asyncio.to_thread(System, cmd.removeprefix("system ").strip()))

        elif cmd.startswith("create file"):
            path = cmd.removeprefix("create file").strip()
            tasks.append(asyncio.to_thread(CreateFile, path))

        elif cmd.startswith("delete file"):
            path = cmd.removeprefix("delete file").strip()
            tasks.append(asyncio.to_thread(DeleteFile, path))

        elif cmd.startswith("create folder"):
            path = cmd.removeprefix("create folder").strip()
            tasks.append(asyncio.to_thread(CreateFolder, path))

        elif cmd.startswith("delete folder"):
            path = cmd.removeprefix("delete folder").strip()
            tasks.append(asyncio.to_thread(DeleteFolder, path))

    results = await asyncio.gather(*tasks)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True
