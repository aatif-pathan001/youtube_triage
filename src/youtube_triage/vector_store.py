from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from youtube_triage.config import settings


def create_vector_store(
    chunks: list[Document], embedding: HuggingFaceEmbeddings
) -> Chroma:
    """Create a Chroma vector store from a list of Document chunks.

    Args:
        chunks: A list of Document chunks.
        embedding: The embedding function to use.

    Returns:
        Chroma: The created Chroma vector store.
    """
    vector_store_chroma = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
    )
    return vector_store_chroma


def get_retriever(vector_store: Chroma) -> VectorStoreRetriever:
    """Get a retriever from the Chroma vector store.

    Args:
        vector_store: The Chroma vector store.
    Returns:
        Chroma: The retriever for the vector store.
    """
    retriever = vector_store.as_retriever(
        search_type=settings.search_type, search_kwargs={"k": settings.top_k}
    )
    return retriever
