from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from youtube_triage.config import settings


def load_and_chunk(
        url:str,
        chunk_size:int = settings.chunk_size,
        chunk_overlap:int = settings.chunk_overlap
) -> list[Document]:
    """Load transcript from a YouTube URL and split into chunks.

Args:
    url: Full YouTube video URL
    chunk_size: Maximum tokens per chunk
    chunk_overlap: Overlap between consecutive chunks

Returns:
    List of Document objects containing transcript chunks
"""
    loader = YoutubeLoader.from_youtube_url(url)
    transcript_doc = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    transcript_chunks = text_splitter.split_documents(transcript_doc)
    return transcript_chunks