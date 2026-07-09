"""
Hybrid retrieval (torch-free): TF-IDF cosine + BM25, fused with RRF.

Same architecture as the original (adaptive weighting, mode filtering) but the
semantic half is TF-IDF cosine similarity instead of FAISS/embeddings, so it
runs without torch. Cross-encoder rerank is dropped on this tier.
"""
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity


def classify_query(query: str) -> str:
    has_quotes = bool(re.search(r'"[^"]+"', query))
    has_code = bool(re.search(r"\b[A-Z]{2,}\d+\b|\b\d{3,}\b", query))
    has_caps_term = bool(re.search(r"\b[A-Z]{2,}\b", query))
    return "lexical" if sum([has_quotes, has_code, has_caps_term]) >= 1 else "semantic"


def _mode_allows(meta_mode: str, mode: str) -> bool:
    if meta_mode == "both":
        return True
    return meta_mode == mode


def hybrid_retrieve(query, vectorizer, tfidf_matrix, bm25, chunks, metadatas,
                    mode="patient", pool=20, rrf_k=60, bm_weight=1.0, vec_weight=1.0):
    # Lexical (BM25)
    bm_scores = bm25.get_scores(query.lower().split())
    bm_rank = list(np.argsort(bm_scores)[::-1][:pool])

    # Semantic-ish (TF-IDF cosine)
    q_vec = vectorizer.transform([query])
    cos = cosine_similarity(q_vec, tfidf_matrix)[0]
    v_rank = list(np.argsort(cos)[::-1][:pool])

    scores = {}
    for rank, idx in enumerate(bm_rank):
        scores[idx] = scores.get(idx, 0) + bm_weight * (1 / (rrf_k + rank))
    for rank, idx in enumerate(v_rank):
        scores[idx] = scores.get(idx, 0) + vec_weight * (1 / (rrf_k + rank))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    out = []
    for idx, _ in ranked:
        meta_mode = metadatas[idx].get("mode", "both")
        if _mode_allows(meta_mode, mode):
            out.append((chunks[idx], metadatas[idx]))
        if len(out) >= pool:
            break
    return out


def retrieve_and_rerank(query, vectorizer, tfidf_matrix, bm25, chunks, metadatas,
                        reranker=None, mode="patient", k=5, adaptive=True):
    qtype = classify_query(query)
    if adaptive:
        bm_w, vec_w = (1.5, 0.7) if qtype == "lexical" else (0.7, 1.5)
    else:
        bm_w, vec_w = 1.0, 1.0

    candidates = hybrid_retrieve(query, vectorizer, tfidf_matrix, bm25, chunks, metadatas,
                                 mode=mode, pool=20, bm_weight=bm_w, vec_weight=vec_w)
    # No cross-encoder on this tier; return top-k fused results.
    return [(c, m, 0.0) for c, m in candidates[:k]], qtype
