"""
Index singleton. Builds the FAISS + BM25 index and loads models once,
then serves them to the RAG pipeline. Lazy: built on first access.

If the knowledge base is empty (no PDFs added yet), `ready` is False and
the pipeline falls back to answering without retrieved context.
"""
from backend.core.rag.ingestion import build_index
from backend.services.embedding import get_reranker


class _IndexState:
    def __init__(self):
        self.vectorstore = None
        self.bm25 = None
        self.chunks = []
        self.metadatas = []
        self.reranker = None
        self.ready = False
        self._built = False

    def build(self):
        if self._built:
            return
        self.vectorstore, self.bm25, self.chunks, self.metadatas = build_index()
        self.reranker = get_reranker()
        self.ready = self.vectorstore is not None and len(self.chunks) > 0
        self._built = True


_state = _IndexState()


def get_index() -> _IndexState:
    _state.build()
    return _state
