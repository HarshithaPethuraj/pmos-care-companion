---
title: PMOS Care Companion
emoji: hospital
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🩺 PMOS Care Companion

**A dual-mode medical RAG assistant for PMOS (Polyendocrine Metabolic Ovarian Syndrome, formerly PCOS) — combining retrieval-augmented generation with a transparent, rule-based diagnostic-criteria engine.**

Built to serve two audiences from one system: patients (plain, empathetic language) and clinicians (technical, guideline-cited detail), with safety guardrails and a curated doctor directory throughout.

### 🔗 Live demo: **https://pmos-care-companion.onrender.com**

> Note: the demo runs on a free tier that sleeps after inactivity, so the first load may take 30–60 seconds to wake up.

---

## Why this project is different

Most PCOS/PMOS projects on GitHub are **black-box ML classifiers** — a model predicts "PCOS: yes/no" from a dataset, with no explanation a user or doctor can inspect. This project deliberately takes a different route:

1. **Transparent over black-box.** The diagnostic-criteria checker is a **rule engine implementing the Rotterdam criteria (2-of-3)**, not a trained model. Every result shows exactly *which* criteria were met and why. No opaque probability score.
2. **Knows when *not* to use ML.** RAG is used for open-ended medical Q&A where it adds value; a simple deterministic rule engine is used for criteria evaluation where correctness and explainability matter more than prediction. Choosing the right tool per task is a core design principle here.
3. **Dual-mode from one pipeline.** A single retrieval stack serves both patients and clinicians — the *source filtering, prompt, and tone* change by audience, not the infrastructure.
4. **Safety-first by construction.** The system refuses diagnostic requests ("Do I have PMOS?"), escalates red-flag symptoms to urgent care, and never diagnoses.

---

## Features

### 🗣️ Patient Mode
Plain-language, empathetic answers about symptoms, lifestyle, and diet. Every response cites its source document and ends with a "consult your doctor" disclaimer. Retrieval is filtered to patient-appropriate sources (ACOG / Mayo Clinic / NIH fact sheets).

### 🩻 Clinician Mode
Technical, evidence-based summaries grounded in the ESHRE/ASRM 2023 International Guideline. Includes differential-diagnosis notes (thyroid dysfunction, hyperprolactinemia, Cushing's syndrome) and precise guideline references. Retrieval is filtered to clinician-appropriate sources.

### ✅ Rotterdam Criteria Checklist
A transparent rule engine (no ML) evaluating the 3 Rotterdam criteria — irregular cycles, hyperandrogenism, polycystic ovarian morphology. Shows which criteria are met and whether the 2-of-3 threshold is reached. Explicitly **not a diagnosis**; recommends clinical confirmation. Includes an optional "Other Symptoms" tracker to bring to a doctor's appointment.

### 🧪 Understand Your Blood Test
An educational explainer for PMOS-relevant blood markers (testosterone, SHBG, LH, FSH, AMH, prolactin, TSH, 17-OHP, fasting insulin, HbA1c, lipid panel). Explains what each marker means and what to ask a doctor — grounded in the knowledge base. **Deliberately does not accept file uploads or interpret personal values**, avoiding the privacy and misdiagnosis risks of reading real reports.

### 🛡️ Safety Guardrails
A layered defense: fast regex pre-filters, an LLM safety classifier that routes each query to `ALLOW_SAFE` / `BLOCK_DIAGNOSE` / `ESCALATE_RED_FLAG`, and a **two-layer prompt-injection defense** (regex scan + LLM classifier) that excludes malicious retrieved chunks from the context before they reach the LLM.

### 📍 Find a Doctor
A curated directory of 100+ gynecologists across **7 Indian metros** (Chennai, Bengaluru, Mumbai, Delhi, NCR, Hyderabad, Kolkata), with PCOS/PMOS-focused specialists flagged. Falls back to a live API search for any city not in the curated list. Includes an explicit "not a referral or endorsement" disclaimer.

---

## Architecture

```
User query
    │
    ▼
┌─────────────────────────────┐
│ 1. Guardrails               │
│   • regex fast-path          │  ← red flags, obvious diagnostic asks
│   • LLM safety classifier    │  ← BLOCK / ESCALATE / ALLOW
└─────────────┬───────────────┘
              │ (if ALLOW)
              ▼
┌─────────────────────────────┐
│ 2. Hybrid Retrieval         │
│   • BM25 (lexical)           │
│   • TF-IDF (semantic)        │
│   • Adaptive RRF fusion      │  ← weights shift by query type
│   • Mode filter              │  ← patient vs clinician sources
│   • Injection scan (2 layer) │  ← regex + LLM classifier
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 3. Generation               │
│   • Mode-specific prompt     │  ← patient / clinician tone
│   • Groq LLaMA 3.3 70B       │
│   • Source citations         │
└─────────────────────────────┘

Separate deterministic path:
  Symptom checklist → Rotterdam rule engine → criteria met (no ML, no LLM)
```

The rule engine and the RAG pipeline are **independent subsystems**. The checklist never touches the LLM; the chat never touches the rule engine — except that the chat's guardrails can *redirect* a user to the checklist or doctor directory when appropriate.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI + Jinja2 (server-rendered, single app) |
| LLM | Groq-hosted LLaMA 3.3 70B (generation) + 3.1 8B (fast classification) |
| Embeddings / retrieval | TF-IDF (scikit-learn) + BM25, fused with Reciprocal Rank Fusion |
| Deployment | Docker (Render / Hugging Face Spaces) |

> **Note on retrieval:** the project originally used neural embeddings (BAAI/bge-base-en-v1.5) + FAISS + a cross-encoder reranker via LangChain. It was re-engineered to a lightweight TF-IDF + BM25 stack to fit within a 512MB free-tier memory limit — a deliberate tradeoff of some semantic nuance for zero-cost, GPU-free hosting. The full neural implementation remains in the git history.

---

## Project Structure

```
pmos-care-companion/
├── Dockerfile
├── requirements.txt
├── README.md
├── data/
│   └── doctors.json              # curated doctor directory (7 metros)
└── backend/
    ├── main.py                   # FastAPI entry point
    ├── config.py                 # Pydantic settings
    ├── api/
    │   ├── routes/               # health, checklist, chat, doctors, modes, markers
    │   └── schemas/              # request/response models
    ├── core/
    │   ├── rule_engine/          # Rotterdam criteria (no ML)
    │   ├── rag/                  # retrieval, rerank, prompts, pipeline
    │   ├── guardrails/           # filters, classifier, red flags, two-layer injection defense
    │   └── doctors/              # curated + dynamic directory service
    ├── knowledge_base/           # source documents (patient / clinician / research)
    ├── services/                 # LLM, embedding, vector-store clients
    ├── templates/                # Jinja2 HTML
    └── tests/                    # unit tests (rule engine, guardrails, retrieval, injection)
```

---

## Installation & Local Development

```bash
# 1. Clone
git clone https://github.com/HarshithaPethuraj/pmos-care-companion.git
cd pmos-care-companion

# 2. Configure secrets
cp .env.example .env
# edit .env and set GROQ_API_KEY (get a free key at console.groq.com)

# 3. Install
pip install -r requirements.txt

# 4. Run
uvicorn backend.main:app --reload --port 7860
```

Open http://localhost:7860

Or with Docker:
```bash
docker build -t pmos-care-companion .
docker run -p 7860:7860 --env-file .env pmos-care-companion
```

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GROQ_API_KEY` | Yes | LLM inference (generation + classification) |
| `GOOGLE_PLACES_API_KEY` | No | Live doctor search for non-curated cities |
| `GOOGLE_CSE_API_KEY` | No | Practo-scoped fallback search |
| `GOOGLE_CSE_ENGINE_ID` | No | Custom Search Engine ID |

The curated 7-metro doctor directory works without any Google keys.

---

## ⚠️ Ethical & Legal Disclaimer

This tool is for **informational and educational purposes only**. It is **not a medical device, not a diagnostic tool, and not a substitute for professional medical advice, diagnosis, or treatment.**

- It does **not** diagnose PMOS/PCOS or any condition.
- The Rotterdam checklist is a reference aid, not a clinical determination.
- The blood-test explainer describes markers in general and does **not** interpret personal results.
- The doctor directory is compiled from public listings and is **not** a referral or endorsement; verify credentials independently.
- Always consult a qualified healthcare provider for any medical concern. Seek urgent care for severe symptoms.

---

## A Note on the PMOS / PCOS Naming

In May 2026, an international consensus published in *The Lancet* renamed Polycystic Ovary Syndrome (PCOS) to **Polyendocrine Metabolic Ovarian Syndrome (PMOS)**, to better reflect its multi-system, metabolic nature. The diagnostic criteria are unchanged. This project uses "PMOS" as the primary term while recognizing "PCOS" throughout, since both will coexist in the literature during the multi-year transition.

---

## License

Released under the MIT License. See `LICENSE` for details.

---

*Built as a portfolio project demonstrating RAG architecture, safety-conscious medical AI design, and the deliberate choice of transparent rule-based logic where explainability matters most.*
