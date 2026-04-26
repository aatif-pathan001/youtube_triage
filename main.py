from youtube_triage.config import settings
from youtube_triage.pipeline import get_llm, get_prompt, create_rag_chain
from youtube_triage.transcriber import load_and_chunk
from youtube_triage.vector_store import create_vector_store, get_retriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


def main(url: str, question: str):
    embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    chunks = load_and_chunk(url)
    vector_store = create_vector_store(chunks, embedding)
    retriever = get_retriever(vector_store)
    llm = get_llm()
    prompt = get_prompt()
    rag_chain = create_rag_chain(retriever, prompt, llm)
    response = rag_chain.invoke(question)
    return response


if __name__ == "__main__":
    url = "https://youtu.be/ONgECvZNI3o"
    question = "What is automation?"
    answer = main(url, question)
    print(f"Answer: {answer}")
