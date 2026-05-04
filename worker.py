from google.cloud import pubsub_v1
from langchain_huggingface import HuggingFaceEmbeddings
from youtube_triage.transcriber import load_and_chunk
from youtube_triage.models import Session as SessionModel
from youtube_triage.models import Chunk
from youtube_triage.config import settings
from youtube_triage.database import SessionLocal
import json


def callback(message, embedding):
    # Process the Pub/Sub message
    data = json.loads(message.data)
    session_id = data["session_id"]
    url = data["url"]

    # Idempotency check
    with SessionLocal() as db:
        session = db.get(SessionModel, session_id)
        if session.status == "ready":
            message.ack()
            return

        # Pipeline
        chunks = load_and_chunk(url)
        for chunk in chunks:
            db_chunk = Chunk(
                session_id=session_id,
                text=chunk.page_content,
                start_sec=0,
                end_sec=0,
                embedding=embedding.embed_query(chunk.page_content),
            )
            db.add(db_chunk)

        session.status = "ready"
        db.commit()

    message.ack()


def worker_1(embedding):
    # Initialize the Pub/Sub subscriber
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(
        settings.gcp_project_id, "transcript-jobs-worker"
    )
    streaming_pull_future = subscriber.subscribe(
        sub_path, callback=lambda message: callback(message, embedding)
    )
    return streaming_pull_future


if __name__ == "__main__":
    embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    streaming_pull_future = worker_1(embedding)
    streaming_pull_future.result()
