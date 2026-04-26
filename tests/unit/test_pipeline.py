from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_triage.pipeline import format_docs

def test_format_docs():
    doc1 = Document(page_content="Hellow ")
    doc2 = Document(page_content="World")
    docs = [doc1, doc2]
    result = format_docs(docs)
    assert result == "Hellow World"

def test_document_chunking():
    transcript = Document(page_content="This is a test transcript for the YouTube video. It contains multiple sentences to test the chunking functionality.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10, chunk_overlap = 0)
    transcript_chunks = text_splitter.split_documents([transcript])
    for chunk in transcript_chunks:
        assert len(chunk.page_content) <= 10