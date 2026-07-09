"""
Lightweight ingestion pipeline (torch-free, fits 512MB).

Loads PMOS knowledge-base documents, chunks them, and builds:
  - a TF-IDF matrix (scikit-learn) for semantic-ish similarity
  - a BM25 index for lexical matching

Replaces the previous FAISS + sentence-transformers stack, which needed
torch (~800MB) and exceeded free-tier memory. TF-IDF + BM25 keeps genuine
hybrid retrieval at a fraction of the memory.

Metadata carries a `mode` tag ("patient" | "clinician" | "both") so retrieval
can filter sources by audience.
"""
from pathlib import Path
import re

FOLDER_MODE = {
    "patient_faqs": "patient",
    "guidelines": "clinician",
    "research": "both",
}


def _split_text(text: str, chunk_size: int = 600, overlap: int = 100):
    """Simple recursive-ish splitter on paragraph/sentence boundaries."""
    paras = re.split(r"\n\s*\n", text)
    chunks, buf = [], ""
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if len(buf) + len(p) + 2 <= chunk_size:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf:
                chunks.append(buf)
            if len(p) <= chunk_size:
                buf = p
            else:
                # hard-wrap long paragraph
                for i in range(0, len(p), chunk_size - overlap):
                    chunks.append(p[i:i + chunk_size])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks


def _load_raw_documents(raw_dir: Path):
    docs = []
    for subfolder, mode in FOLDER_MODE.items():
        folder = raw_dir / subfolder
        if not folder.exists():
            continue
        for path in folder.iterdir():
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(str(path))
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text() or ""
                        if text.strip():
                            docs.append((text, {"source": path.name, "page": i + 1, "mode": mode}))
                except Exception:
                    continue
            elif suffix in (".txt", ".md"):
                text = path.read_text(encoding="utf-8", errors="ignore")
                docs.append((text, {"source": path.name, "mode": mode}))
    return docs


def build_index(raw_dir: str = "backend/knowledge_base/raw"):
    """Returns (tfidf_vectorizer, tfidf_matrix, bm25, chunks, metadatas)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from rank_bm25 import BM25Okapi

    raw = _load_raw_documents(Path(raw_dir))
    if not raw:
        return None, None, None, [], []

    chunks, metadatas = [], []
    for text, meta in raw:
        for c in _split_text(text):
            chunks.append(c)
            metadatas.append(meta)

    if not chunks:
        return None, None, None, [], []

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=20000)
    tfidf_matrix = vectorizer.fit_transform(chunks)
    bm25 = BM25Okapi([c.lower().split() for c in chunks])
    return vectorizer, tfidf_matrix, bm25, chunks, metadatas
