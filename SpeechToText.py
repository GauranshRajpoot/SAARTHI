from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get('InputLanguage', 'en')

# HTML for browser-based speech recognition
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head><title>Speech Recognition</title></head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "{InputLanguage}";
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
            output.innerHTML = "";
        }}
    </script>
</body>
</html>
"""

# Save HTML file
current_dir = os.getcwd()
voice_html_path = os.path.join(current_dir, "Data", "Voice.html")
os.makedirs(os.path.dirname(voice_html_path), exist_ok=True)
with open(voice_html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("headless=new")
chrome_options.add_argument("user-agent=Mozilla/5.0")

# Launch driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Restart driver if needed
def restart_driver():
    global driver
    print("🔁 Restarting Chrome driver...")
    try:
        driver.quit()
    except Exception:
        pass
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

# Path to store assistant state
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(status: str):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(status)

def QueryModifier(query: str) -> str:
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    query = query.strip().lower()
    is_question = any(query.startswith(word) for word in question_words)

    if query:
        if is_question:
            query = query.rstrip(".?!") + "?"
        else:
            query = query.rstrip(".?!") + "."
        return query.capitalize()
    return ""

def UniversalTranslator(text: str) -> str:
    translated = mt.translate(text, "en", "auto")
    return translated.capitalize()

def SpeechRecognition() -> str:
    try:
        driver.get("file:///" + voice_html_path.replace("\\", "/"))
    except (InvalidSessionIdException, WebDriverException):
        print("⚠️ Chrome session invalid or closed. Restarting driver...")
        restart_driver()
        try:
            driver.get("file:///" + voice_html_path.replace("\\", "/"))
        except Exception as e:
            print(f"❌ Failed after restart: {e}")
            return "ERROR: Chrome failure"

    try:
        driver.find_element(By.ID, "start").click()
        time.sleep(2)  # Allow mic permission and speech recognition init
    except Exception as e:
        print(f"[ERROR] Could not start recognition: {e}")
        return "ERROR: Recognition init"

    while True:
        try:
            text = driver.find_element(By.ID, "output").text.strip()
            if not text:
                continue

            # ✅ SNAP DETECTION
            if "snap" in text.lower():
                print("👆 Snap Triggered")
                from Frontend.GUI import snap_image_changer
                snap_image_changer()
                driver.execute_script("document.getElementById('output').innerHTML = ''")  # clear output
                continue  # skip returning snap as command

            if InputLanguage.lower().startswith("en"):
                return QueryModifier(text)
            else:
                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(text))
        except Exception as e:
            print(f"[SpeechRecognition Error] {e}")
            continue

# Run as main
if __name__ == "__main__":
    try:
        while True:
            result = SpeechRecognition()
            if result:
                print(result)
    except KeyboardInterrupt:
        driver.quit()
        print("\n[INFO] Assistant stopped and browser closed.")
