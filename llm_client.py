from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE

def get_llm():
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=2048
    )
    return llm
