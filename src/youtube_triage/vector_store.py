from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from youtube_triage.config import settings
from sqlalchemy import text
import uuid


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


def search_chunks(
    session_id: uuid.UUID,
    question: str,
    embedding: HuggingFaceEmbeddings,
    db,
    k: int = settings.top_k,
) -> list:
    query_embedding = embedding.embed_query(question)

    results = db.execute(
        text("""
        SELECT text, start_sec, end_sec FROM chunks
        WHERE session_id = :session_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :k
"""),
        {"session_id": str(session_id), "embedding": str(query_embedding), "k": k},
    ).fetchall()
    return results
