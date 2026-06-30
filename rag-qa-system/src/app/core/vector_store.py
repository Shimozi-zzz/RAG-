import os
from langchain_chroma import Chroma
from app.config import settings
from app.core.embeddings import get_embeddings

_vector_store: Chroma | None = None


def _get_collection_name() -> str:
    return "rag_knowledge_base"


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIR)
        _vector_store = Chroma(
            collection_name=_get_collection_name(),
            embedding_function=get_embeddings(),
            persist_directory=persist_dir,
        )
    return _vector_store


def add_documents_to_store(documents: list):
    store = get_vector_store()
    store.add_documents(documents)


def similarity_search(query: str, k: int | None = None) -> list:
    store = get_vector_store()
    top_k = k or settings.TOP_K
    return store.similarity_search(query, k=top_k)