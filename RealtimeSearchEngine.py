from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from googlesearch import search

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Load existing chat log or create a new one
def load_chat_log():
    try:
        with open("Data/ChatLog.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        return []

messages = load_chat_log()

# System message template
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname} with real-time internet information.
*** Provide answers professionally, using proper grammar and punctuation. ***
*** Answer questions based on provided data professionally. ***"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to perform Google search
def google_search(query):
    results = list(search(query, advanced=True, num_results=5))
    return "\n".join([f"Title: {i.title}\nDescription: {i.description}" for i in results])

# Function to clean response formatting
def clean_answer(answer):
    return "\n".join([line for line in answer.split("\n") if line.strip()])

# Function to generate real-time system info
def real_time_info():
    now = datetime.datetime.now()
    return f"""Use This Real-time Information if needed:
Day: {now.strftime("%A")}
Date: {now.strftime("%d")}
Month: {now.strftime("%B")}
Year: {now.strftime("%Y")}
Time: {now.strftime("%H")} hours, {now.strftime("%M")} minutes, {now.strftime("%S")} seconds."""

# Function to generate chatbot response
def real_time_search_engine(prompt):
    messages.append({"role": "user", "content": prompt})
    SystemChatBot.append({"role": "system", "content": google_search(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": real_time_info()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = clean_answer(answer.strip().replace("</s>", ""))
    
    with open("Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
    
    SystemChatBot.pop()
    return answer

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(real_time_search_engine(prompt))