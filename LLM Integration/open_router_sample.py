from open_router_client import chat_completion_text

response = chat_completion_text(
    [{"role": "user", "content": "What is the meaning of life?"}]
)
print(response)
