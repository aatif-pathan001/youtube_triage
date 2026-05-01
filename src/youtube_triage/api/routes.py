from fastapi import FastAPI, Depends, APIRouter
from pydantic import BaseModel
from youtube_triage.database import get_db
from youtube_triage.models import Session as SessionModel
from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException


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


app = FastAPI()

# ------ Routers ------
router_v1 = APIRouter(prefix="/v1")


@router_v1.post("/sessions", status_code=202, response_model=SessionResponse)
async def create_session(
    session_request: SessionRequest, db: Session = Depends(get_db)
) -> SessionResponse:
    new_session = SessionModel(url=session_request.url)
    db.add(new_session)
    db.commit()
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
    session_id: uuid.UUID, question: MessageRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return MessageResponse(
        answer="result", timestamps=[Timestamp(sec=0, text="Sample timestamp")]
    )


app.include_router(router_v1)
