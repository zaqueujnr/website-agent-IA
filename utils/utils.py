import os
from langchain.chat_models import init_chat_model


def load_fast_llm():
    model = os.getenv("NEXOS_FAST_MODEL")
    return init_chat_model(
        model=model,
        model_provider="openai",
        api_key=os.getenv("NEXOS_API_KEY"),
        base_url="https://api.nexos.ai/v1",
        temperature=0,
    )
def load_powerful_llm():
    return init_chat_model(
        model=os.getenv("NEXOS_POWERFUL_MODEL"),
        model_provider="openai",
        api_key=os.getenv("NEXOS_API_KEY"),
        base_url="https://api.nexos.ai/v1",
        temperature=0,
    )