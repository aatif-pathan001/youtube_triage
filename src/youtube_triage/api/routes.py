from fastapi import FastAPI, Depends, APIRouter
from pydantic import BaseModel
from youtube_triage.database import get_db
from youtube_triage.models import Session as SessionModel
from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException
from youtube_triage.services.pubsub import publish_job
from youtube_triage.vector_store import search_chunks
from contextlib import asynccontextmanager
from youtube_triage.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import Request
from langchain_core.documents import Document
from youtube_triage.pipeline import get_llm, get_prompt, format_docs
from langchain_core.output_parsers import StrOutputParser


# ------ Request/ Response Models ------
class SessionRequest(BaseModel):
    url: str


class SessionResponse(BaseModel):
    session_id: uuid.UUID
    status: str


class Timestamp(BaseModel):
    sec: int
    text: str


class MessageRequest(BaseModel):
    question: str


class MessageResponse(BaseModel):
    answer: str
    timestamps: list[Timestamp]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    app.state.llm = get_llm()
    yield


app = FastAPI(lifespan=lifespan)

# ------ Routers ------
router_v1 = APIRouter(prefix="/v1")


@router_v1.post("/sessions", status_code=202, response_model=SessionResponse)
async def create_session(
    session_request: SessionRequest, db: Session = Depends(get_db)
) -> SessionResponse:
    new_session = SessionModel(url=session_request.url)
    db.add(new_session)
    db.commit()
    publish_job(new_session.session_id, new_session.url)
    db.refresh(new_session)
    return SessionResponse(session_id=new_session.session_id, status=new_session.status)


@router_v1.get(
    "/sessions/{session_id}/status", response_model=SessionResponse, status_code=200
)
async def get_session_status(
    session_id: uuid.UUID, db: Session = Depends(get_db)
) -> SessionResponse:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(session_id=session_id, status=session.status)


@router_v1.post(
    "/sessions/{session_id}/messages", response_model=MessageResponse, status_code=200
)
async def ask_question(
    session_id: uuid.UUID,
    question: MessageRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> MessageResponse:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    context_chunk = search_chunks(
        session_id, question.question, request.app.state.embedding, db
    )
    context_document = [
        Document(
            page_content=chunk[0], metadata={"start_sec": chunk[1], "end_sec": chunk[2]}
        )
        for chunk in context_chunk
    ]
    llm = request.app.state.llm
    context_str = format_docs(context_document)
    prompt = get_prompt()
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"context": context_str, "query": question.question})

    return MessageResponse(
        answer=result,
        timestamps=[
            Timestamp(sec=chunk[1], text=chunk[0][:100]) for chunk in context_chunk
        ],
    )


app.include_router(router_v1)
