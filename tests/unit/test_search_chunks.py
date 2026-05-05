from unittest.mock import MagicMock
from youtube_triage.vector_store import search_chunks
import uuid


def test_search_chunks():
    # Arrange
    session_id = uuid.uuid4()
    mock_embedding = MagicMock()
    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = [
        ("This is automation text", 30, 60),
        ("N8N is an automation tool", 90, 120),
    ]

    # Act
    results = search_chunks(session_id, "What is automation?", mock_embedding, mock_db)

    # Assert
    assert len(results) == 2
    mock_db.execute.assert_called_once()
