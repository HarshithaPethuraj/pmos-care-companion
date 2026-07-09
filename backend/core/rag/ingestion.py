"""
Ingestion pipeline ported from IntelliRAG.

Loads PMOS knowledge-base documents from backend/knowledge_base/raw/,
chunks them (RecursiveCharacterTextSplitter, 600/100), embeds with
bge-base-en-v1.5, and builds a FAISS vector store + BM25 index.

Metadata carries a `mode` tag ("patient" | "clinician" | "both") so retrieval
can filter sources by audience, per the dual-mode design.
"""
from pathlib import Path

from backend.services.embedding import get_embeddings

# Maps KB subfolders to the audience mode their documents serve.
FOLDER_MODE = {
    "patient_faqs": "patient",   # ACOG / Mayo / NIH patient fact sheets
    "guidelines": "clinician",   # ESHRE/ASRM 2023
    "research": "both",          # PubMed abstracts
}


def _load_raw_documents(raw_dir: Path):
    from langchain_core.documents import Document
    from langchain_community.document_loaders import PyPDFLoader

    docs = []
    for subfolder, mode in FOLDER_MODE.items():
        folder = raw_dir / subfolder
        if not folder.exists():
            continue
        for path in folder.iterdir():
            suffix = path.suffix.lower()
            if suffix == ".pdf":
                pages = PyPDFLoader(str(path)).load()
                for i, p in enumerate(pages):
                    p.metadata["source"] = path.name
                    p.metadata["page"] = p.metadata.get("page", i) + 1
                    p.metadata["mode"] = mode
                docs.extend(pages)
            elif suffix in (".txt", ".md"):
                text = path.read_text(encoding="utf-8", errors="ignore")
                docs.append(Document(page_content=text, metadata={"source": path.name, "mode": mode}))
    return docs


def build_index(raw_dir: str = "backend/knowledge_base/raw"):
    """Returns (vectorstore, bm25, chunks, metadatas). Call once at startup."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from rank_bm25 import BM25Okapi

    docs = _load_raw_documents(Path(raw_dir))
    if not docs:
        return None, None, [], []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=100, separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunked = splitter.split_documents(docs)
    chunks = [c.page_content for c in chunked]
    metadatas = [c.metadata for c in chunked]

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunked, embeddings)
    bm25 = BM25Okapi([c.lower().split() for c in chunks])
    return vectorstore, bm25, chunks, metadatas
