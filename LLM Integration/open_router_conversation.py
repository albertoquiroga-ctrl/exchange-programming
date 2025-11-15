import os

from open_router_client import build_open_router_client

DEFAULT_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"


def main() -> None:
    try:
        client = build_open_router_client()
    except RuntimeError as err:
        print(f"Configuration error: {err}")
        return

    model = os.getenv("OPEN_ROUTER_MODEL") or DEFAULT_MODEL

    print("Welcome to LLM chat! (Type 'exit' to quit)")
    messages: list[dict[str, str]] = []

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nConversation ended.")
            break

        if user_input.lower() in ("exit", "quit"):
            print("Conversation ended.")
            break
        messages.append({"role": "user", "content": user_input})

        try:
            completion = client.chat.completions.create(model=model, messages=messages)
            assistant_message = completion.choices[0].message.content
            print("AI:", assistant_message)
            messages.append({"role": "assistant", "content": assistant_message})
        except Exception as exc:  # pragma: no cover - network failures are runtime issues
            print("Error communicating with LLM:", exc)


if __name__ == "__main__":
    main()
