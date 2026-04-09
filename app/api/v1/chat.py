"""AI Coach chat API endpoints with SSE streaming."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.exceptions import NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    TTSRequest,
)
from app.services.coach_service import (
    create_session,
    get_session,
    get_sessions,
    stream_response,
    stream_voice_response,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_chat_session(
    body: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session with the AI coach."""
    session = create_session(db, current_user.id, body.title)
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        message_count=0,
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chat sessions."""
    sessions = get_sessions(db, current_user.id)
    return [
        ChatSessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages) if s.messages else 0,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a chat session with all messages."""
    session = get_session(db, session_id, current_user.id)
    if not session:
        raise NotFoundException(detail="Chat session not found")

    return ChatSessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session.messages) if session.messages else 0,
        messages=[
            ChatMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                tokens_used=m.tokens_used,
                created_at=m.created_at,
            )
            for m in (session.messages or [])
        ],
    )


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    body: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to the AI coach and receive a streaming response.

    Returns Server-Sent Events (SSE):
        data: {"type": "text", "content": "..."}
        data: {"type": "done"}
    """
    session = get_session(db, session_id, current_user.id)
    if not session:
        raise NotFoundException(detail="Chat session not found")

    return StreamingResponse(
        stream_response(db, current_user, session, body.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/tts")
async def text_to_speech_endpoint(
    body: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Convert text to speech using ElevenLabs.

    Returns streaming audio/mpeg data. Used for replaying
    past messages as audio.
    """
    from app.services.voice_service import is_voice_enabled, text_to_speech_stream

    if not is_voice_enabled():
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Voice is not configured. Set ELEVENLABS_API_KEY in environment.",
        )

    return StreamingResponse(
        text_to_speech_stream(body.text),
        media_type="audio/mpeg",
        headers={
            "Content-Type": "audio/mpeg",
            "Cache-Control": "no-cache",
        },
    )


@router.post("/sessions/{session_id}/voice-message")
async def send_voice_message(
    session_id: str,
    body: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message and receive both text AND audio chunks via SSE.

    Combines Claude AI response with ElevenLabs TTS, streaming
    sentence-by-sentence for low-latency audio playback.

    Returns Server-Sent Events (SSE):
        data: {"type": "text", "content": "..."}
        data: {"type": "audio", "content": "<base64>", "sentence_index": N}
        data: {"type": "done"}
    """
    session = get_session(db, session_id, current_user.id)
    if not session:
        raise NotFoundException(detail="Chat session not found")

    return StreamingResponse(
        stream_voice_response(db, current_user, session, body.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
