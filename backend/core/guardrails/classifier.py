"""
LLM-based safety classifier. Routes a query to one of:
  [BLOCK_DIAGNOSE], [ESCALATE_RED_FLAG], [ALLOW_SAFE]

Uses the fast/cheap 8B model. The regex filters in filters.py / red_flags.py
still run first as a zero-cost pre-filter; this LLM pass catches phrasings the
regex misses. Fails open to ALLOW_SAFE if the model call errors, since the
downstream RAG prompt also enforces refusal rules.
"""
from backend.services.llm import get_groq_client
from backend.config import get_settings
from backend.core.rag.prompts import GUARDRAIL_CLASSIFICATION_PROMPT

VALID_LABELS = {"BLOCK_DIAGNOSE", "ESCALATE_RED_FLAG", "ALLOW_SAFE"}


def classify_intent(query: str) -> str:
    settings = get_settings()
    client = get_groq_client()
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model_small,
            messages=[{"role": "user", "content": GUARDRAIL_CLASSIFICATION_PROMPT.format(query=query)}],
            temperature=0,
            max_tokens=12,
        )
        raw = resp.choices[0].message.content.strip().strip("[]").upper()
    except Exception:
        return "ALLOW_SAFE"

    for label in VALID_LABELS:
        if label in raw:
            return label
    return "ALLOW_SAFE"
