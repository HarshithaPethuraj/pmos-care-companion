"""
Model loaders ported from IntelliRAG app.py.
Uses lru_cache (FastAPI) instead of @st.cache_resource (Streamlit).
"""
from functools import lru_cache

from backend.config import get_settings


@lru_cache()
def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    settings = get_settings()
    try:
        return HuggingFaceEmbeddings(
            model_name=settings.embedding_model,  # BAAI/bge-base-en-v1.5
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception:
        # Fallback to a lighter model if bge fails to download
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )


@lru_cache()
def get_reranker():
    settings = get_settings()
    try:
        from sentence_transformers import CrossEncoder
        return CrossEncoder(settings.reranker_model)  # ms-marco-MiniLM-L-6-v2
    except Exception:
        return None
