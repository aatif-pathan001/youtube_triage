from langchain_community.document_loaders import YoutubeLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.youtube import TranscriptFormat


def load_and_chunk(
    url: str,
) -> list[Document]:
    """Load transcript from a YouTube URL and split into chunks.

    Args:
        url: Full YouTube video URL
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of Document objects containing transcript chunks
    """
    loader = YoutubeLoader.from_youtube_url(
        url, transcript_format=TranscriptFormat.CHUNKS, chunk_size_seconds=30
    )
    transcript_doc = loader.load()
    # No need for additional text splitting since the loader already chunks the transcript
    return transcript_doc
