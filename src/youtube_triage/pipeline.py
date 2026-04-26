from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_core.documents import Document
from youtube_triage.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    """ Initialize the llm model"""
    return ChatGoogleGenerativeAI(model=settings.model, temperature=settings.temperature)

def get_prompt() -> ChatPromptTemplate:
    """ Create the prompt template for the LLM"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a Youtube triage assistant, that tells user wheter the video is relevant to their query or not based on the retrieved chunks from the video transcript: {context}"),
            ("human", "{query}"),
        ]
    )
    return prompt

def format_docs(docs: list[Document]) -> str:
    """ Covert the document object into string to attach with the input propmt to model."""

    return "".join([doc.page_content for doc in docs])

def create_rag_chain(retriever, prompt, llm) -> Runnable:
    """ Create the RAG chain by connecting retriever, prompt and llm."""

    ragchain = ({"context": retriever | format_docs,
                 "query": RunnablePassthrough()} | prompt | llm | StrOutputParser()
                )
    return ragchain