from fastapi import FastAPI
from fastapi import APIRouter
from pydantic import BaseModel


# ------ Request/ Response Models ------
class SessionRequest(BaseModel):
    url: str


class SessionResponse(BaseModel):
    session_id: str
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
async def create_session(session_request: SessionRequest) -> SessionResponse:
    return SessionResponse(session_id="abc123", status="processing")


@router_v1.get(
    "/sessions/{session_id}/status", response_model=SessionResponse, status_code=200
)
async def get_session_status(session_id: str) -> SessionResponse:
    current_status = "processing"
    return SessionResponse(session_id=session_id, status=current_status)


@router_v1.post(
    "/sessions/{session_id}/messages", response_model=MessageResponse, status_code=200
)
async def ask_question(question: MessageRequest) -> MessageResponse:
    pass
    return MessageResponse(
        answer="result", timestamps=[Timestamp(sec=0, text="Sample timestamp")]
    )


app.include_router(router_v1)
