from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPEN_ROUTER_API_KEY,
)

print("Welcome to LLM chat! (Type 'exit' to quit)")
messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ("exit", "quit"):
        print("Conversation ended.")
        break
    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=messages
        )
        assistant_message = completion.choices[0].message.content
        print("AI:", assistant_message)
        messages.append({"role": "assistant", "content": assistant_message})
    except Exception as e:
        print("Error communicating with LLM:", e)
