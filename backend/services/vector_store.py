"""
Index singleton (torch-free). Builds the TF-IDF + BM25 index once and serves
it to the RAG pipeline. Lazy: built on first access.

If the knowledge base is empty, `ready` is False and the pipeline answers
without retrieved context.
"""
from backend.core.rag.ingestion import build_index


class _IndexState:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.bm25 = None
        self.chunks = []
        self.metadatas = []
        self.reranker = None  # not used on the lightweight tier
        self.ready = False
        self._built = False

    def build(self):
        if self._built:
            return
        (self.vectorizer, self.tfidf_matrix, self.bm25,
         self.chunks, self.metadatas) = build_index()
        self.ready = self.vectorizer is not None and len(self.chunks) > 0
        self._built = True


_state = _IndexState()


def get_index() -> _IndexState:
    _state.build()
    return _state
