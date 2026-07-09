from functools import lru_cache
from groq import Groq

from backend.config import get_settings


@lru_cache()
def get_groq_client() -> Groq:
    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)
