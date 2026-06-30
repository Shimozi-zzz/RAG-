from app.config import settings
from app.core.vector_store import get_vector_store


def get_retriever():
    store = get_vector_store()
    return store.as_retriever(
        search_kwargs={"k": settings.TOP_K}
    )