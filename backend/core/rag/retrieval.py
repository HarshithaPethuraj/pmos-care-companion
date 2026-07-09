"""
Hybrid retrieval + rerank, ported from IntelliRAG.

- hybrid_retrieve: BM25 + FAISS fused with Reciprocal Rank Fusion (RRF).
- classify_query: lexical vs semantic, drives adaptive BM25/vector weighting.
- retrieve_and_rerank: cross-encoder rerank of the fused pool.

Extension for PMOS: mode filtering. Patient mode retrieves only patient/both
sources; clinician mode retrieves only clinician/both sources.
"""
import numpy as np
import re


def classify_query(query: str) -> str:
    has_quotes = bool(re.search(r'"[^"]+"', query))
    has_code = bool(re.search(r"\b[A-Z]{2,}\d+\b|\b\d{3,}\b", query))
    has_caps_term = bool(re.search(r"\b[A-Z]{2,}\b", query))
    return "lexical" if sum([has_quotes, has_code, has_caps_term]) >= 1 else "semantic"


def _mode_allows(meta_mode: str, mode: str) -> bool:
    if meta_mode == "both":
        return True
    return meta_mode == mode


def hybrid_retrieve(query, vectorstore, bm25, chunks, metadatas, mode="patient",
                    pool=20, rrf_k=60, bm_weight=1.0, vec_weight=1.0):
    bm_scores = bm25.get_scores(query.lower().split())
    bm_rank = list(np.argsort(bm_scores)[::-1][:pool])
    vdocs = vectorstore.similarity_search(query, k=pool)
    v_rank = []
    for d in vdocs:
        try:
            v_rank.append(chunks.index(d.page_content))
        except ValueError:
            pass

    scores = {}
    for rank, idx in enumerate(bm_rank):
        scores[idx] = scores.get(idx, 0) + bm_weight * (1 / (rrf_k + rank))
    for rank, idx in enumerate(v_rank):
        scores[idx] = scores.get(idx, 0) + vec_weight * (1 / (rrf_k + rank))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    # Mode-filter: drop chunks whose source audience doesn't match.
    out = []
    for idx, _ in ranked:
        meta_mode = metadatas[idx].get("mode", "both")
        if _mode_allows(meta_mode, mode):
            out.append((chunks[idx], metadatas[idx]))
        if len(out) >= pool:
            break
    return out


def retrieve_and_rerank(query, vectorstore, bm25, chunks, metadatas, reranker,
                        mode="patient", k=5, adaptive=True):
    qtype = classify_query(query)
    if adaptive:
        bm_w, vec_w = (1.5, 0.7) if qtype == "lexical" else (0.7, 1.5)
    else:
        bm_w, vec_w = 1.0, 1.0

    candidates = hybrid_retrieve(query, vectorstore, bm25, chunks, metadatas,
                                 mode=mode, pool=20, bm_weight=bm_w, vec_weight=vec_w)
    if reranker is None or not candidates:
        return [(c, m, 0.0) for c, m in candidates[:k]], qtype

    pairs = [[query, c] for c, _ in candidates]
    scores = reranker.predict(pairs)
    order = np.argsort(scores)[::-1][:k]
    return [(candidates[i][0], candidates[i][1], float(scores[i])) for i in order], qtype
