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

    completion = client.chat.completions.create(
        extra_body={},
        model=model,
        messages=[
            {
                "role": "user",
                "content": "What is the meaning of life?"
            }
        ]
    )
    print(completion.choices[0].message.content)


if __name__ == "__main__":
    main()
