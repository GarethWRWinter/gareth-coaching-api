"""forma-core — the single funnel for every Claude call Forma makes.

The PRD's non-negotiable architecture: one place that owns model routing,
prompt caching, cost logging, and the provider client. There is no other
path to Claude — services never construct their own anthropic client.

Every call:
  1. resolves its model + max_tokens from the TASKS routing table
     (callers may override max_tokens but never hardcode a model),
  2. gets `cache_control` applied to the stable system prefix,
  3. is logged to `forma_calls` (tokens, cost in cents, latency, surface)
     in its OWN db session, so a caller's rollback never loses the record.

Usage:
    from app.core import forma_core

    resp = forma_core.call(
        user_id=user.id, task="nudge", surface="dashboard",
        system=persona + NUDGE_PROMPT, messages=[...],
    )

    with forma_core.stream(
        user_id=user.id, task="chat", surface="coach",
        system=system_blocks, messages=messages, tools=COACH_TOOLS,
    ) as s:
        for event in s: ...
        final = s.get_final_message()
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

SONNET = "claude-sonnet-5"
HAIKU = "claude-haiku-4-5-20251001"


@dataclass(frozen=True)
class TaskConfig:
    model: str
    max_tokens: int


# The routing table — the ONLY place a model name is bound to a job.
# Sonnet where Forma reasons as a coach, Haiku for extraction and
# short interpretive lines (mirrors the PRD cost model).
TASKS: dict[str, TaskConfig] = {
    "chat": TaskConfig(SONNET, 2048),          # streaming coach chat (tools)
    "chat_voice": TaskConfig(SONNET, 1024),    # voice chat — shorter replies
    "chat_sync": TaskConfig(SONNET, 2048),     # non-streaming chat turn
    "debrief": TaskConfig(SONNET, 500),        # post-ride debrief
    "assessment": TaskConfig(SONNET, 1500),    # workout execution assessment
    "nudge": TaskConfig(HAIKU, 200),           # daily dashboard nudge
    "explain": TaskConfig(HAIKU, 200),         # metric explanation
    "memory_extraction": TaskConfig(HAIKU, 1500),
    "memory_reading": TaskConfig(HAIKU, 220),  # Brain page narration
}

# USD per million tokens, matched by model-id prefix. Cache reads bill at
# 0.1x input, cache writes at 1.25x (5-minute TTL).
_PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-opus-4-8": (5.00, 25.00),
}

_client_instance: anthropic.Anthropic | None = None


def _client() -> anthropic.Anthropic:
    """One provider client for the whole app — swap providers here."""
    global _client_instance
    if _client_instance is None:
        _client_instance = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client_instance


def _prices_for(model: str) -> tuple[float, float]:
    for prefix, prices in _PRICES_PER_MTOK.items():
        if model.startswith(prefix):
            return prices
    logger.warning("forma-core: no price entry for model %s — logging zero cost", model)
    return (0.0, 0.0)


def cost_cents(model: str, usage) -> float:
    """Cost of one call in US cents from an anthropic Usage object."""
    in_price, out_price = _prices_for(model)
    tokens_in = getattr(usage, "input_tokens", 0) or 0
    tokens_out = getattr(usage, "output_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    usd = (
        tokens_in * in_price
        + cache_read * in_price * 0.10
        + cache_write * in_price * 1.25
        + tokens_out * out_price
    ) / 1_000_000
    return usd * 100


def _normalize_system(system) -> list:
    """String system prompts become a cached block; block lists pass through.

    Callers that already manage their own cache breakpoints (the chat
    service's [cached education, dynamic context] split) are untouched.
    """
    if isinstance(system, str):
        return [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    return system


def _log(
    user_id: str,
    task: str,
    surface: str | None,
    model: str,
    usage,
    latency_ms: int,
    error: bool = False,
) -> None:
    """Write a forma_calls row in its own session — never on the caller's
    transaction, so cost records survive caller rollbacks and vice versa."""
    try:
        from app.database import SessionLocal
        from app.models.forma_call import FormaCall

        row = FormaCall(
            user_id=user_id,
            task=task,
            surface=surface,
            model=model,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
            cost_cents=cost_cents(model, usage) if usage is not None else 0.0,
            latency_ms=latency_ms,
            error=error,
        )
        db = SessionLocal()
        try:
            db.add(row)
            db.commit()
        finally:
            db.close()
    except Exception:  # noqa: BLE001 — cost logging must never break Forma
        logger.exception("forma-core: failed to log call (task=%s user=%s)", task, user_id)


def call(
    *,
    user_id: str,
    task: str,
    system,
    messages: list,
    surface: str | None = None,
    tools: list | None = None,
    max_tokens: int | None = None,
):
    """One non-streaming Forma call. Returns the anthropic Message."""
    cfg = TASKS[task]
    kwargs = {}
    if tools:
        kwargs["tools"] = tools
    t0 = time.monotonic()
    try:
        resp = _client().messages.create(
            model=cfg.model,
            max_tokens=max_tokens or cfg.max_tokens,
            system=_normalize_system(system),
            messages=messages,
            **kwargs,
        )
    except Exception:
        _log(user_id, task, surface, cfg.model, None, int((time.monotonic() - t0) * 1000), error=True)
        raise
    _log(user_id, task, surface, cfg.model, resp.usage, int((time.monotonic() - t0) * 1000))
    return resp


@contextmanager
def stream(
    *,
    user_id: str,
    task: str,
    system,
    messages: list,
    surface: str | None = None,
    tools: list | None = None,
    max_tokens: int | None = None,
):
    """One streaming Forma call. Yields the anthropic MessageStream;
    usage is logged from the final message when the block exits."""
    cfg = TASKS[task]
    kwargs = {}
    if tools:
        kwargs["tools"] = tools
    t0 = time.monotonic()
    try:
        with _client().messages.stream(
            model=cfg.model,
            max_tokens=max_tokens or cfg.max_tokens,
            system=_normalize_system(system),
            messages=messages,
            **kwargs,
        ) as s:
            yield s
            final = s.get_final_message()
    except Exception:
        _log(user_id, task, surface, cfg.model, None, int((time.monotonic() - t0) * 1000), error=True)
        raise
    _log(user_id, task, surface, cfg.model, final.usage, int((time.monotonic() - t0) * 1000))
