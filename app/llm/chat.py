from ollama import Client
from app.settings import AppSettings

config = AppSettings()

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + config.llm.api_key}
)

def build_messages(query: str, context: str, history: list = []) -> list:
    return [
        {"role": "system", "content": f"Answer using only the context below.\n\nContext:\n{context}"},
        *history,
        {"role": "user", "content": query},
    ]

def chat(messages: list) -> str:
    response = client.chat(model=config.llm.model_name, messages=messages)
    return response.message.content