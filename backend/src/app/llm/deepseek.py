from langchain_openai import ChatOpenAI

from app.agent.config import llm_settings


def create_deepseek():
    return ChatOpenAI(
        model=llm_settings.deepseek_model,
        api_key=llm_settings.deepseek_api_key,
        base_url=llm_settings.deepseek_base_url,
    )