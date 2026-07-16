"""Application-level encryption for secrets stored in the database.

Third-party OAuth tokens (Strava, Dropbox, TrainingPeaks) are encrypted at
rest so a database compromise does not hand an attacker live access to every
user's connected accounts. Uses Fernet (AES-128-CBC + HMAC) via a dedicated
`TOKEN_ENCRYPTION_KEY` — deliberately separate from SECRET_KEY, so rotating
the JWT signing key never risks the stored integration tokens.

`EncryptedString` is a SQLAlchemy type: assign/read plaintext in Python, and
ciphertext is what lands in the column. Reads tolerate legacy plaintext rows
(pre-encryption), so the rollout is safe without a flag-day backfill — every
token write re-encrypts, and `scripts/encrypt_integration_tokens.py` encrypts
the rest immediately.

Key rotation: set `TOKEN_ENCRYPTION_KEY` to a comma-separated list. The first
key encrypts; all keys are tried on decrypt (MultiFernet), so you add a new
key, re-encrypt, then drop the old one.
"""
from __future__ import annotations

import binascii
import logging

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy.types import Text, TypeDecorator

from app.config import settings

logger = logging.getLogger(__name__)


def _fernet() -> MultiFernet:
    raw = settings.token_encryption_key
    if not raw:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is not set — cannot encrypt/decrypt integration "
            "tokens. Generate one with "
            "`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`"
        )
    keys = [Fernet(k.strip().encode()) for k in raw.split(",") if k.strip()]
    return MultiFernet(keys)


def encrypt_str(plaintext: str) -> str:
    """Encrypt with the primary (first) key."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_str(ciphertext: str) -> str:
    """Decrypt, trying every configured key. Raises InvalidToken if none match."""
    return _fernet().decrypt(ciphertext.encode()).decode()


def looks_encrypted(value: str) -> bool:
    """True if `value` decrypts under a current key (i.e. already ciphertext)."""
    try:
        decrypt_str(value)
        return True
    except (InvalidToken, ValueError, binascii.Error):
        return False


class EncryptedString(TypeDecorator):
    """Transparently encrypt on write, decrypt on read. Column holds ciphertext
    (Text — Fernet output is longer than the plaintext token)."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return decrypt_str(value)
        except (InvalidToken, ValueError, binascii.Error):
            # Legacy plaintext row not yet re-encrypted — return as-is so reads
            # never break mid-rollout. A missing key raises RuntimeError instead
            # (loud), so we never silently hand ciphertext to an API as if plain.
            return value
