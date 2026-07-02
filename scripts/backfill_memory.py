"""Backfill the memory graph from existing history.

Seeds the Brain (Pillar 2) from data that predates the memory layer:
  1. Chat history — each user↔Marco exchange runs through extraction.
  2. Ride debriefs — every ride with a stored debrief_text.

Memories are dated with `observed_at` = when the conversation/ride actually
happened, so the Brain's growth replay tells the true story.

Idempotent-ish: extraction dedups by (type, label) similarity, so re-runs
enrich rather than duplicate.

Usage:
    python scripts/backfill_memory.py --email gareth@test.com
    python scripts/backfill_memory.py --email ... --dry-run
    python scripts/backfill_memory.py --email ... --limit 10 --skip-debriefs
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal  # noqa: E402
from app.models.chat import ChatMessage, ChatSession  # noqa: E402
from app.models.ride import Ride  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.memory_service import extract_memories  # noqa: E402


def backfill_chat(db, user, limit: int | None, dry_run: bool) -> dict:
    """Pair user→assistant messages into exchanges and extract each."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.asc())
        .all()
    )
    totals = {"exchanges": 0, "created": 0, "linked": 0}
    for s in sessions:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == s.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        i = 0
        while i < len(messages):
            m = messages[i]
            role = m.role.value if hasattr(m.role, "value") else str(m.role)
            if role != "user":
                i += 1
                continue
            reply = None
            if i + 1 < len(messages):
                nrole = messages[i + 1].role
                nrole = nrole.value if hasattr(nrole, "value") else str(nrole)
                if nrole in ("assistant", "marco"):
                    reply = messages[i + 1]
            text = f"Rider: {m.content}"
            if reply is not None:
                text += f"\n\nMarco: {reply.content}"
            totals["exchanges"] += 1
            if limit and totals["exchanges"] > limit:
                return totals
            print(f"  chat {totals['exchanges']:>3} · {m.created_at} · {m.content[:60]!r}")
            if not dry_run:
                r = extract_memories(
                    db, user, text,
                    source="chat", source_ref=s.id, observed_at=m.created_at,
                )
                totals["created"] += r["created"]
                totals["linked"] += r["linked"]
                time.sleep(0.4)  # be gentle with the API
            i += 2 if reply is not None else 1
    return totals


def backfill_debriefs(db, user, limit: int | None, dry_run: bool) -> dict:
    rides = (
        db.query(Ride)
        .filter(Ride.user_id == user.id, Ride.debrief_text.isnot(None))
        .order_by(Ride.ride_date.asc())
        .all()
    )
    totals = {"debriefs": 0, "created": 0, "linked": 0}
    for ride in rides:
        totals["debriefs"] += 1
        if limit and totals["debriefs"] > limit:
            return totals
        print(f"  debrief {totals['debriefs']:>3} · {ride.ride_date} · {ride.title!r}")
        if not dry_run:
            r = extract_memories(
                db, user,
                f"Ride: {ride.title}\n\nMarco's debrief:\n{ride.debrief_text}",
                source="debrief", source_ref=str(ride.id), observed_at=ride.ride_date,
            )
            totals["created"] += r["created"]
            totals["linked"] += r["linked"]
            time.sleep(0.4)
    return totals


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--email", required=True)
    p.add_argument("--limit", type=int, default=None, help="max items per source")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--skip-chat", action="store_true")
    p.add_argument("--skip-debriefs", action="store_true")
    args = p.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            print(f"No user with email {args.email}")
            sys.exit(1)
        print(f"Backfilling memory for {user.email} (dry_run={args.dry_run})\n")

        if not args.skip_chat:
            print("— Chat history —")
            c = backfill_chat(db, user, args.limit, args.dry_run)
            print(f"  → {c['exchanges']} exchanges · +{c['created']} entities · +{c['linked']} edges\n")

        if not args.skip_debriefs:
            print("— Ride debriefs —")
            d = backfill_debriefs(db, user, args.limit, args.dry_run)
            print(f"  → {d['debriefs']} debriefs · +{d['created']} entities · +{d['linked']} edges\n")

        from app.services.memory_service import get_graph
        g = get_graph(db, user)
        print(f"Brain now: {len(g['entities'])} entities · {len(g['edges'])} edges")
    finally:
        db.close()


if __name__ == "__main__":
    main()
