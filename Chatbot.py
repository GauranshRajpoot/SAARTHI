from groq import Groq
from json import load, dump, JSONDecodeError
from datetime import datetime
from dotenv import dotenv_values
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot")

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Setup system prompt
System = (
    f"Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} "
    f"which also has real-time up-to-date information from the internet.\n"
    f"*** Do not tell time until I ask, do not talk too much, just answer the question.***\n"
    f"*** Reply in only English, even if the question is in Hindi.***\n"
    f"*** Do not provide notes, just answer the question and never mention your training data. ***"
)

SystemChatBot = [{"role": "system", "content": System}]

# Path for persistent chat log
file_path = os.path.join("Data", "ChatLog.json")

def load_messages():
    """Load chat history from local JSON log."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return load(f)
    except (FileNotFoundError, JSONDecodeError) as e:
        logger.warning(f"Chat log loading failed: {e}")
        return []

def save_messages(messages):
    """Save messages back to file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        dump(messages, f, indent=4)

def RealtimeInformation():
    """Returns real-world time string (optional)."""
    now = datetime.now()
    return (
        "Please use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )

def AnswerModifier(answer):
    """Removes empty lines or bad formatting."""
    return '\n'.join(line for line in answer.split("\n") if line.strip())

def Chatbot(query: str) -> str:
    """Main chatbot function — passes query to Groq and returns answer."""
    try:
        messages = load_messages()
        messages.append({"role": "user", "content": query})

        # Dynamically add real-time context if needed
        system_context = SystemChatBot.copy()
        if "time" in query.lower():
            system_context.append({"role": "system", "content": RealtimeInformation()})

        full_prompt = system_context + messages

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=full_prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                answer += delta

        answer = answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": answer})
        save_messages(messages)

        return AnswerModifier(answer)

    except Exception as e:
        logger.error(f"Error: {e}")
        save_messages([])  # Clear bad file if corrupted
        return Chatbot(query)  # Retry once

# ─────────────────────────────
# 🧪 CLI Testing
# ─────────────────────────────
if __name__ == "__main__":
    while True:
        user_input = input("Enter the query: ")
        print(Chatbot(user_input))
