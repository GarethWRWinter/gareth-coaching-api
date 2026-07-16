"""Cross-user data isolation — the automated safety net for IDOR-class bugs.

For each user-scoped resource, a second user must NOT be able to read, modify,
or delete it by guessing its id. This is the test that would have caught the
workout link-ride IDOR. Add a case here for every new resource that takes an
id in its path. Runs against the configured database via TestClient and cleans
up the two throwaway accounts it creates.

Run:  python -m pytest tests/test_cross_user_isolation.py -q
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database import SessionLocal
from app.main import app
from app.models.base import generate_uuid
from app.models.user import User

client = TestClient(app)


def _make_user(db, email: str) -> dict:
    """Create a user directly and mint an access token. Bypasses the auth
    endpoints so the suite is independent of their (correct) rate limits."""
    uid = generate_uuid()
    db.add(User(id=uid, email=email, hashed_password=hash_password("testpass123"), is_active=True))
    db.commit()
    return {"h": {"Authorization": f"Bearer {create_access_token(uid)}"}}


@pytest.fixture
def two_users():
    tag = uuid.uuid4().hex[:8]
    a_email = f"iso-a-{tag}@example.com"
    b_email = f"iso-b-{tag}@example.com"
    db = SessionLocal()
    try:
        a = _make_user(db, a_email)
        b = _make_user(db, b_email)
    finally:
        db.close()
    yield a, b
    # Cleanup: remove both throwaway accounts and their goals/chat sessions.
    db = SessionLocal()
    try:
        from sqlalchemy import text
        for email in (a_email, b_email):
            uid = db.execute(text("SELECT id FROM users WHERE email=:e"), {"e": email}).scalar()
            if uid:
                db.execute(text("DELETE FROM chat_messages WHERE session_id IN "
                                "(SELECT id FROM chat_sessions WHERE user_id=:u)"), {"u": uid})
                db.execute(text("DELETE FROM chat_sessions WHERE user_id=:u"), {"u": uid})
                db.execute(text("DELETE FROM goal_events WHERE user_id=:u"), {"u": uid})
                db.execute(text("DELETE FROM refresh_tokens WHERE user_id=:u"), {"u": uid})
                db.execute(text("DELETE FROM users WHERE id=:u"), {"u": uid})
        db.commit()
    finally:
        db.close()


def test_cannot_read_another_users_goal(two_users):
    a, b = two_users
    created = client.post("/api/v1/goals", headers=a["h"], json={
        "event_name": "A's private race", "event_date": "2026-09-01",
        "event_type": "road_race", "priority": "a_race",
    })
    assert created.status_code == 201, created.text
    goal_id = created.json()["id"]

    # A can read it; B must not.
    assert client.get(f"/api/v1/goals/{goal_id}", headers=a["h"]).status_code == 200
    assert client.get(f"/api/v1/goals/{goal_id}", headers=b["h"]).status_code == 404


def test_cannot_modify_or_delete_another_users_goal(two_users):
    a, b = two_users
    goal_id = client.post("/api/v1/goals", headers=a["h"], json={
        "event_name": "A's race", "event_date": "2026-09-01",
        "event_type": "road_race", "priority": "a_race",
    }).json()["id"]

    assert client.patch(f"/api/v1/goals/{goal_id}", headers=b["h"],
                        json={"event_name": "hijacked"}).status_code == 404
    assert client.delete(f"/api/v1/goals/{goal_id}", headers=b["h"]).status_code == 404
    # A's goal is untouched.
    assert client.get(f"/api/v1/goals/{goal_id}", headers=a["h"]).json()["event_name"] == "A's race"


def test_cannot_read_another_users_chat_session(two_users):
    a, b = two_users
    session_id = client.post("/api/v1/chat/sessions", headers=a["h"],
                             json={"title": "A's private chat"}).json()["id"]

    assert client.get(f"/api/v1/chat/sessions/{session_id}", headers=a["h"]).status_code == 200
    assert client.get(f"/api/v1/chat/sessions/{session_id}", headers=b["h"]).status_code == 404


def test_unauthenticated_is_rejected():
    assert client.get("/api/v1/users/me").status_code == 401
