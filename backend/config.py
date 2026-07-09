"""
Central configuration for PMOS Care Companion.
Reads from environment variables / .env via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "PMOS Care Companion"
    app_env: str = "development"
    log_level: str = "INFO"

    # LLM
    groq_api_key: str = ""
    llm_model_large: str = "llama-3.3-70b-versatile"
    llm_model_small: str = "llama-3.1-8b-instant"

    # Embeddings / retrieval
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    enable_reranker: bool = False  # set True only on hosts with >1GB RAM
    enable_llm_injection_check: bool = True  # second-layer defense beyond regex (small model, low cost)

    # Doctor directory - dynamic fallback
    google_places_api_key: str = ""
    google_cse_api_key: str = ""
    google_cse_engine_id: str = ""

    # Paths
    doctors_data_path: str = "data/doctors.json"
    faiss_index_path: str = "backend/knowledge_base/processed/faiss_index"
    bm25_index_path: str = "backend/knowledge_base/processed/bm25_index.pkl"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
