# HANDOFF — the baton

> Whoever holds the baton has the turn. Read the protocol in `CLAUDE.md`.
> At the start of your turn: `git pull --rebase`, claim below. At the end: commit, push, release below.

Holder: FREE
Updated: 2026-07-15

## In flight / Next
- **Brand v2 shipped across the app** (kite mark, chalk page, new zone inks, Archivo Expanded,
  CoachDot, TODAY/COACH/RIDES/FORM/PLAN nav). Source: `frontend/docs/brand/`; skills updated.
- **Production fixes landed**: Dropbox debrief await-sync bug, workout auto-complete on in-app
  ride save, link-ride IDOR, SECRET_KEY rotated locally (**ROTATE ON RAILWAY TOO** — the deployed
  env still has the placeholder), Performance page Forma reading (Pillar 1), seated zone orbs cut
  from `mockups/Masters/` approved set.
- Next (from the 15 Jul PRD reconciliation): `forma-core` funnel (9 scattered Anthropic clients),
  pgvector + forma_calls cost logging, auth hardening (email verify, reset, refresh rotation,
  RLS), ASR for voice input, ElevenLabs voice ID ≠ OQ2 pick.
- ALMANAC docs (`almanac-DESIGN.md`, `voicebox-DESIGN.md`, old mockups) are historical — safe to
  delete when ready.

## Recent handoffs
- 2026-06-11 — **ALMANAC rollout.** Re-skinned VoiceBox → ALMANAC (warm linen, humanist sans,
  forest accent, handwritten Marco signature). New fonts (Bricolage/Schibsted/Caveat), re-mapped
  `vb-*` tokens, restyled dashboard + sidebar + all dashboard pages + auth/landing/onboarding +
  shared UI primitives + all charts. Fixed the empty-PMC bug (dropped manual recharts ticks).
- 2026-06-07 — Collaboration protocol created (CLAUDE.md + HANDOFF.md). PRD updated to v0.3
  (Strava MCP confirmed live; Appendix A reconciled against code audit).
