# HANDOFF — the baton

> Whoever holds the baton has the turn. Read the protocol in `CLAUDE.md`.
> At the start of your turn: `git pull --rebase`, claim below. At the end: commit, push, release below.

Holder: FREE
Updated: 2026-07-16

## In flight / Next
- **Per-user monthly budget SHIPPED** on the forma_calls ledger: `settings.monthly_budget_cents`
  (env `MONTHLY_BUDGET_CENTS`, default $8). `forma_core.call/stream` raise `BudgetExceededError`
  before spending when over the hard cap; chat emits `QUOTA_MESSAGE`; `GET /coach/usage` exposes
  spend/pct/state for the soft-cap UI. Verified: $0.01 budget → blocked, no ledger row; $8 → normal.
- **Compliance decided: GDPR now, defer SOC2/ISO.** PRD Appendix B → "Compliance & certifications"
  has the pre-launch reminders (ICO reg, privacy policy, Cyber Essentials). Don't skip before launch.
- **AUTH still to build** — Gareth chose "GDPR for now" but has NOT yet answered the two gating
  questions: auth scope (public-launch = OAuth login + live email provider, vs beta baseline) and
  Postgres RLS (yes = defense-in-depth + isolation tests, vs app-layer + tests only). Known gaps to
  fix once scoped: refresh-token rotation/revocation + `/auth/logout`, email verify + password
  reset, login timing/user-enumeration + rate-limit/lockout, **plaintext Strava/Dropbox tokens
  (encrypt at rest — highest-severity data issue)**, security headers, GDPR export/delete endpoints,
  `is_active`/`deleted_at` on User. **Also still: rotate SECRET_KEY on Railway.**
- **forma-core SHIPPED** (`app/core/forma_core.py`): the single Claude funnel — routing table
  (Sonnet: chat/debrief/assessment; Haiku: nudge/explain/memory), cache_control on every stable
  system prefix, cost logging to the new `forma_calls` table (migration m7i8j9k0l1f2), provider
  client in one place. All 9 scattered `anthropic.Anthropic()` call sites migrated, prompts
  byte-identical. `GET /api/v1/admin/costs` (gated by `ADMIN_EMAILS` env — **set on Railway**)
  serves per-user/per-task spend. Verified live: chat turn-2 read 9.2K cached tokens (75%
  cheaper than turn-1). Next per PRD: per-user monthly token budget on top of forma_calls,
  then auth hardening (Epic D).
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
