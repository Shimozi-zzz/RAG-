from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_API_BASE,
        temperature=0.3,
    )