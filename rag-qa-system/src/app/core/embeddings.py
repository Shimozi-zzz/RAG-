import os
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings


def get_embeddings() -> HuggingFaceEmbeddings:
    if settings.HF_ENDPOINT:
        os.environ["HF_ENDPOINT"] = settings.HF_ENDPOINT

    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )