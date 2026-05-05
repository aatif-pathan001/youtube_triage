from unittest.mock import patch, MagicMock
from worker import callback
import json
import uuid


def test_callback_processes_new_session():
    session_id = str(uuid.uuid4())
    mock_message = MagicMock()
    mock_message.data = json.dumps(
        {"session_id": session_id, "url": "http://example.com/video"}
    ).encode("utf-8")

    mock_embedding = MagicMock()
    mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]

    with (
        patch("worker.SessionLocal") as MockSessionLocal,
        patch("worker.load_and_chunk") as mock_load,
    ):
        # Set mock session
        mock_session = MagicMock()
        mock_session.status = "processing"
        MockSessionLocal.return_value.__enter__.return_value.get.return_value = (
            mock_session
        )

        # Set mock chunks
        mock_load.return_value = [
            MagicMock(page_content="chunk1", metadata={"start_timestamp": 0}),
            MagicMock(page_content="chunk2", metadata={"start_timestamp": 30}),
        ]

        callback(mock_message, mock_embedding)

        # Assertions
        assert mock_session.status == "ready"
        MockSessionLocal.return_value.__enter__.return_value.get.assert_called_once()
        mock_load.assert_called_once()
