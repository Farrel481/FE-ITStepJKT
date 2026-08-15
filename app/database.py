from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Induk bagi setiap model/tabel SQLAlchemy."""


def get_db():
    """Memberikan satu session database untuk setiap request API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
