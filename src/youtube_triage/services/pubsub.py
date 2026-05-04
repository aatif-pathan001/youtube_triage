from google.cloud import pubsub_v1
import json
from youtube_triage.config import settings
import uuid


def publish_job(session_id: uuid.UUID, url: str):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings.gcp_project_id, "transcript-jobs")
    message = json.dumps({"session_id": str(session_id), "url": url}).encode("utf-8")
    publisher.publish(topic_path, data=message)
