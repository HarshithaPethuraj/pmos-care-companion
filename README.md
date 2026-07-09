---
title: PMOS Care Companion
emoji: 🩺
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# PMOS Care Companion

Dual-mode RAG + rule-based reference tool for PMOS (formerly PCOS - Polyendocrine
Metabolic Ovarian Syndrome, renamed per the May 2026 Lancet global consensus).

## Features
- **Patient mode** - plain-language Q&A with citations
- **Clinician mode** - Rotterdam criteria / ESHRE-ASRM 2023 guideline detail
- **Symptom checklist** - transparent, rule-based Rotterdam criteria engine (no ML, no diagnosis)
- **Find a Doctor** - curated directory for 7 major Indian metros (Chennai, Bengaluru,
  Mumbai, Delhi, NCR, Hyderabad, Kolkata) with live API fallback for any other city

## Stack
FastAPI + Jinja2 (server-rendered), LangChain + Groq (LLaMA 3.3 70B / 3.1 8B),
FAISS + BM25 hybrid retrieval, cross-encoder reranker, BAAI/bge-base-en-v1.5 embeddings.

## Local development
```bash
cp .env.example .env   # fill in GROQ_API_KEY etc.
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 7860
```
or
```bash
docker-compose up --build
```

## Deployment (HF Spaces)
This repo uses the Docker SDK (see `sdk: docker` above). Set `GROQ_API_KEY` and
(optionally) `GOOGLE_PLACES_API_KEY` / `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ENGINE_ID`
as Space secrets.

## Disclaimer
This tool is for informational purposes only and is not a substitute for
professional medical advice, diagnosis, or treatment.
