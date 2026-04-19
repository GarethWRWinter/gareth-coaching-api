import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

_db_url = settings.database_url

# Quick connectivity test — if the configured URL fails, try the public URL
def _try_connect(url: str, timeout: int = 3) -> bool:
    """Test if a database URL is reachable."""
    try:
        test_engine = create_engine(url, connect_args={"connect_timeout": timeout})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
        return True
    except Exception:
        return False

# Ensure sslmode for Railway URLs
def _ensure_ssl(url: str) -> str:
    if "railway" in url and "localhost" not in url and "sslmode" not in url:
        return url + ("?sslmode=require" if "?" not in url else "&sslmode=require")
    return url

_db_url = _ensure_ssl(_db_url)
logger.info("Database URL target: %s", _db_url.split("@")[-1] if "@" in _db_url else "unknown")

# Test primary URL, fall back to public URL if internal networking is broken
if not _try_connect(_db_url):
    _public = os.environ.get("DATABASE_PUBLIC_URL", "")
    if _public:
        _public = _ensure_ssl(_public)
        logger.warning("Primary DB URL failed, trying DATABASE_PUBLIC_URL...")
        if _try_connect(_public):
            _db_url = _public
            logger.info("Using DATABASE_PUBLIC_URL fallback")
    if not _try_connect(_db_url):
        logger.error("Cannot connect to database at startup! URL: %s",
                      _db_url.split("@")[-1] if "@" in _db_url else "unknown")

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
