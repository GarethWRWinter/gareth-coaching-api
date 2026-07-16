"""Idempotent backfill: encrypt any plaintext integration tokens at rest.

Run once after TOKEN_ENCRYPTION_KEY is set (locally, and on prod after the
Railway var is added). Safe to re-run — rows already encrypted are skipped.
New token writes encrypt automatically via EncryptedString, so this only
mops up rows written before encryption shipped.

Usage:  python -m scripts.encrypt_integration_tokens
"""
import logging

from sqlalchemy import text

from app.config import settings
from app.core.crypto import encrypt_str, looks_encrypted
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("encrypt_tokens")

# (table, columns) — raw SQL so we bypass the ORM's transparent decrypt/encrypt
# and see the actual stored bytes.
TARGETS = [
    ("strava_tokens", ("access_token", "refresh_token")),
    ("trainingpeaks_tokens", ("access_token", "refresh_token")),
    ("dropbox_tokens", ("access_token", "refresh_token")),
]


def main() -> None:
    if not settings.token_encryption_key:
        raise SystemExit("TOKEN_ENCRYPTION_KEY is not set — nothing to do.")

    db = SessionLocal()
    encrypted = skipped = 0
    try:
        for table, cols in TARGETS:
            rows = db.execute(text(f"SELECT id, {', '.join(cols)} FROM {table}")).fetchall()
            for row in rows:
                updates = {}
                for col in cols:
                    val = getattr(row, col)
                    if val is None or looks_encrypted(val):
                        skipped += 1
                        continue
                    updates[col] = encrypt_str(val)
                    encrypted += 1
                if updates:
                    set_clause = ", ".join(f"{c} = :{c}" for c in updates)
                    db.execute(
                        text(f"UPDATE {table} SET {set_clause} WHERE id = :id"),
                        {**updates, "id": row.id},
                    )
        db.commit()
        logger.info("Done: %d values encrypted, %d already encrypted / null.", encrypted, skipped)
    finally:
        db.close()


if __name__ == "__main__":
    main()
