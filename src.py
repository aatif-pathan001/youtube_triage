from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_core.runnables import RunnablePassthrough

from dotenv import load_dotenv
load_dotenv()

model = 'gemini-2.5-flash'


test_link = "https://youtu.be/ONgECvZNI3o?si=7wN_M0ZG9jEpHoYH"

# 1. Extract transcript from YouTube Link and COnvert to Document Object
loader = YoutubeLoader.from_youtube_url(test_link)
tr1_doc = loader.load()

print("=="*60)
print(f'Loaded Document: {tr1_doc[0].page_content[:500]}')

# 2. Split the script into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 512, chunk_overlap = 50)
tr1_chunks = text_splitter.split_documents(tr1_doc)
print("=="*60)
print(f'Split Chunks: {len(tr1_chunks)}')
print(f'Chunk 1: {tr1_chunks[0].page_content[:200]}...')
# 3. Embedding the chunks and storing in vector store
embedding1 = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2') 

vector_store_dir = './vector_store'
if os.path.exists(vector_store_dir) and os.listdir(vector_store_dir):
    # Load existing persisted database
    vector_store_chroma = Chroma(
        persist_directory=vector_store_dir,
        embedding_function=embedding1,
    )
    print("vectore store loaded successfully !!")
    vector_store_chroma.add_documents(tr1_chunks)
    print("New transcript added to the existing vector store !!")
else:
    # Create and persist the database once
    vector_store_chroma = Chroma.from_documents(
        documents=tr1_chunks,
        embedding_function=embedding1,
        persist_directory=vector_store_dir,
    )
    print("vectore store created successfully !!")




# 4. Retrieval

retriever = vector_store_chroma.as_retriever(
    search_type="similarity",
    search_kwargs={"k":3}
    )
# 5. Chat LLM
llm = ChatGoogleGenerativeAI(model=model, temperature=0.5)

# 6. Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ('system','You are a YouTube Q&A bot, that answers the question based on the context from the video.{context}'),
        ('human', '{question}')
    ]
)


def format_docs(docs):
    """ Covert the document object into string to attach with the input propmt to model."""
    return "".join([doc.page_content for doc in docs])

ragchain = ( {"context": retriever | format_docs,
              "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
)

question = "What is automation?"

docs = retriever.invoke(question)

print("=="*60)
print("Retrieved Docs: ")
for i, doc in enumerate(docs):
    print(f"Doc {i+1}: {doc.page_content[:200]}...")

answer = ragchain.invoke(question)

print("=="*60)
print(f'Question: {question}')
print("Answer: ", answer)

