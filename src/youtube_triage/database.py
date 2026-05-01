from sqlalchemy import create_engine
from youtube_triage.config import settings
from sqlalchemy.orm import sessionmaker


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
