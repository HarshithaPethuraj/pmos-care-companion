"""
RAG pipeline orchestration for PMOS Care Companion.

Flow:
  1. Regex fast-path guardrails (red flags, obvious diagnostic asks) - zero cost.
  2. LLM safety classifier (catches phrasings regex misses).
  3. Hybrid retrieval (BM25 + TF-IDF + adaptive RRF), mode-filtered by audience.
  4. Prompt-injection filter, two layers:
     a. Regex scan (free, instant) - excludes obvious pattern matches.
     b. LLM classifier (small/fast model) - catches injections that don't
        match known phrasings. Runs only on chunks that survived (a).
  5. Mode-specific prompt (patient / clinician) -> Groq LLaMA 3.3 70B.

The two-layer injection defense directly addresses an external evaluation
note (IntelliRAG eval) that a regex-only scanner is "a first layer" and a
production system needs an LLM-based classifier for robustness against
attacks that don't match known phrase patterns.

If the knowledge base is empty (no PDFs ingested yet), retrieval is skipped
and the prompt's "context does NOT contain the answer" branch handles it.
"""
import math

from backend.services.llm import get_groq_client
from backend.config import get_settings
from backend.core.guardrails.filters import is_diagnostic_request
from backend.core.guardrails.red_flags import check_red_flags, ESCALATION_MESSAGE
from backend.core.guardrails.classifier import classify_intent
from backend.core.guardrails.injection import scan_for_injection
from backend.core.guardrails.injection_classifier import classify_chunk_injection
from backend.core.rag.prompts import PATIENT_SYSTEM_PROMPT, CLINICIAN_SYSTEM_PROMPT
from backend.core.rag.retrieval import retrieve_and_rerank
from backend.services.vector_store import get_index

DIAGNOSTIC_REFUSAL = (
    "I can't tell you whether you have PMOS/PCOS - that needs a clinical "
    "evaluation. I can walk you through the Rotterdam criteria checklist, or "
    "answer questions about symptoms, management, or find a doctor near you."
)


def _retrieve_context(query: str, mode: str) -> tuple[str, list[str], float]:
    """Returns (context_text, sources, confidence). Empty if KB not ready."""
    index = get_index()
    if not index.ready:
        return "", [], 0.0

    reranked, _qtype = retrieve_and_rerank(
        query, index.vectorizer, index.tfidf_matrix, index.bm25,
        index.chunks, index.metadatas, index.reranker, mode=mode, k=5,
    )

    # Injection defense, layer 1: regex (free, instant).
    survived_regex = [(c, m, s) for c, m, s in reranked if not scan_for_injection(c)]

    if not survived_regex:
        return "", [], 0.0

    # Injection defense, layer 2: LLM classifier (small/fast model).
    # Only runs on chunks that already passed the regex layer, keeping the
    # added latency/cost bounded to the handful of chunks actually retrieved.
    settings = get_settings()
    if settings.enable_llm_injection_check:
        clean = [(c, m, s) for c, m, s in survived_regex if not classify_chunk_injection(c)]
    else:
        clean = survived_regex

    if not clean:
        return "", [], 0.0

    context = "\n\n".join(c for c, _, _ in clean)
    sources = []
    for _, meta, _ in clean:
        src = meta.get("source", "document")
        page = meta.get("page")
        sources.append(f"{src}" + (f" (page {page})" if page else ""))

    top_score = clean[0][2]
    confidence = round(1 / (1 + math.exp(-top_score)) * 100) if index.reranker else 75
    return context, sources, confidence


def run_rag_pipeline(query: str, mode: str = "patient") -> str:
    # 1. Regex fast-path
    if check_red_flags(query):
        return ESCALATION_MESSAGE
    if is_diagnostic_request(query):
        return DIAGNOSTIC_REFUSAL

    # 2. LLM safety classifier
    label = classify_intent(query)
    if label == "ESCALATE_RED_FLAG":
        return ESCALATION_MESSAGE
    if label == "BLOCK_DIAGNOSE":
        return DIAGNOSTIC_REFUSAL

    # 3-4. Retrieve + injection-filter
    context, _sources, _confidence = _retrieve_context(query, mode)

    # 5. Generate
    template = CLINICIAN_SYSTEM_PROMPT if mode == "clinician" else PATIENT_SYSTEM_PROMPT
    prompt = template.format(context=context or "No relevant documents retrieved.", query=query)

    settings = get_settings()
    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.llm_model_large,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content
