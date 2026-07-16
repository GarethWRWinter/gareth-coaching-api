from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenRefresh, TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import token_service

router = APIRouter(prefix="/auth", tags=["auth"])

# Verified against when the email is unknown, so a login attempt takes the same
# time whether or not the account exists (defeats timing-based user enumeration).
_DUMMY_HASH = hash_password("forma-nonexistent-account-placeholder")


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise ConflictException(detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    # Always run a bcrypt verify — against a dummy hash when the email is
    # unknown — so response time doesn't reveal whether an email is registered.
    hashed = user.hashed_password if user else _DUMMY_HASH
    password_ok = verify_password(user_in.password, hashed)
    if not user or not password_ok:
        raise UnauthorizedException(detail="Invalid email or password")

    access, refresh = token_service.issue_pair(db, user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefresh, db: Session = Depends(get_db)):
    access, refresh = token_service.rotate(db, body.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=204)
def logout(body: TokenRefresh, db: Session = Depends(get_db)):
    """Revoke the presented refresh token's session lineage. Idempotent."""
    token_service.logout(db, body.refresh_token)
    return Response(status_code=204)
