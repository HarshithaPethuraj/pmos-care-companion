"""
Retained for import compatibility. The lightweight retrieval tier uses TF-IDF
(scikit-learn) built in ingestion.py, so no embedding/reranker models load here.
"""


def get_embeddings():
    return None


def get_reranker():
    return None
