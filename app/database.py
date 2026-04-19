import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

_db_url = settings.database_url
# Railway public Postgres requires SSL
if "railway" in _db_url and "localhost" not in _db_url and "sslmode" not in _db_url:
    _db_url += "?sslmode=require" if "?" not in _db_url else "&sslmode=require"

logger.info("Database host: %s", _db_url.split("@")[-1] if "@" in _db_url else "unknown")

engine = create_engine(
    _db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
