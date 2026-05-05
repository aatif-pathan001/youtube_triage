from fastapi.testclient import TestClient
from youtube_triage.api.routes import app
from unittest.mock import patch, MagicMock
from youtube_triage.database import get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from youtube_triage.config import settings
from youtube_triage.models import Base
import pytest


# Setup a test database
test_engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency override
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_session_return_202():
    with patch(
        "youtube_triage.api.routes.publish_job"
    ):  # the publish_job function doesn't return any value so we don't care for it in test
        response = client.post(
            "/v1/sessions", json={"url": "https://www.youtube.com/watch"}
        )
    assert response.status_code == 202
    assert "session_id" in response.json()
    assert response.json()["status"] == "processing"


def test_get_session_status():
    # Arrange a session first
    with patch("youtube_triage.api.routes.publish_job"):
        create_response = client.post(
            "/v1/sessions", json={"url": "https://www.youtube.com/watch"}
        )
    session_id = create_response.json()["session_id"]

    # Act: now check the status
    response = client.get(f"/v1/sessions/{session_id}/status")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"


def test_ask_question():
    # Arrange a session first
    with patch("youtube_triage.api.routes.publish_job"):
        create_response = client.post(
            "/v1/sessions", json={"url": "https://www.youtube.com/watch"}
        )
    session_id = create_response.json()["session_id"]

    # Act: ask a question
    with (
        patch("youtube_triage.api.routes.search_chunks") as mock_chunks,
        patch("youtube_triage.api.routes.get_prompt") as mock_get_prompt,
    ):
        mock_chunks.return_value = [
            ("text of chunk 1", 30, 60),
            ("text of chunk 2", 90, 120),
        ]

        app.state.embedding = MagicMock()
        app.state.llm = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "This is the answer to your question."
        mock_get_prompt.return_value.__or__.return_value.__or__.return_value = (
            mock_chain
        )

        response = client.post(
            f"/v1/sessions/{session_id}/messages",
            json={"question": "What is the video about?"},
        )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert len(response.json()["timestamps"]) == 2
