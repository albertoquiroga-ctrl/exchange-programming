from open_router_client import chat_completion_text, MODEL

print("Welcome to LLM chat! (Type 'exit' to quit)")
messages: list[dict[str, str]] = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ("exit", "quit"):
        print("Conversation ended.")
        break

    messages.append({"role": "user", "content": user_input})

    try:
        assistant_message = chat_completion_text(messages, model=MODEL)
        print("AI:", assistant_message)
        messages.append({"role": "assistant", "content": assistant_message})
    except Exception as e:  # noqa: BLE001 - keep the REPL usable
        print("Error communicating with LLM:", e)
