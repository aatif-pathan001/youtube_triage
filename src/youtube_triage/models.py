import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="processing")
    video_title = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False
    )
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    start_sec = Column(Integer, nullable=False)
    end_sec = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("sessions.session_id"), nullable=False
    )
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_chunk_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)  # type: ignore[var-annotated]
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
