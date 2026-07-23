# HANDOFF — the baton

> Whoever holds the baton has the turn. Read the protocol in `CLAUDE.md`.
> At the start of your turn: `git pull --rebase`, claim below. At the end: commit, push, release below.

Holder: FREE
Updated: 2026-07-23

## In flight / Next
- **FULL-PIPELINE SMOKE TEST PASSED + 3 BUGS FIXED (2026-07-23).** Fresh sign-up →
  onboarding → auto 12-week plan → dashboard → coach chat → Brain, all verified live, zero
  console errors. Fixed: (1) **new users got coach_name 'Marco'** — DB column default was
  still 'Marco' from migration k5g6h7i8j9d0; migration q1m2n3o4p5j6 flips default to 'Forma'
  + re-backfills (RUN `alembic upgrade head` ON RAILWAY — happens automatically on deploy);
  (2) 422 validation errors rendered "[object Object]" in every form — api.ts now normalizes
  FastAPI detail arrays to readable sentences; (3) data tiles stuck at 0 in hidden tabs —
  useCountUp skips animation when document hidden + settle timeout. Also "your AI coach" →
  "your coach". Brand doc updated (Abstract imagery register: ink-dispersion climbs, IB2
  chalk+kite lockup) → frontend/docs/brand/ + forma-brand skill.
- **STRAVA IMPORT SCOPE FIX SHIPPED (2026-07-23).** Root cause of "connected but 0 rides
  import": `exchange_code` HARDCODED `scope="read,activity:read_all"` regardless of what
  Strava granted. If the user doesn't tick "View data about your activities", Strava grants
  `read` only → card shows LINKED → every `/athlete/activities` call 403s silently. Fixes:
  (1) `exchange_code(...granted_scope=)` stores the REAL granted scope (callback passes it +
  falls back to token response); (2) callback gates on `scope_has_activity_read()` and redirects
  `?strava=error&reason=missing_activity_scope` instead of a fake "connected", skips backfill;
  (3) `/strava/status` now returns `scope`+`can_read_activities`, and `?probe=true` makes ONE
  live Strava call (`probe_activity_access`) = ground-truth 403 check for already-linked tokens;
  (4) sync + backfill raise a clear "reconnect and tick activities" error on 403 (backfill status
  `failed_no_activity_scope`), no more silent retry; (5) settings page shows a **Reconnect Strava**
  banner driven by `can_read_activities===false` OR the live probe OR the new backfill status.
  Typecheck clean, app boots. **USER ACTION to confirm the live fix:** on the live site, hit
  Settings → the banner should appear if the current token lacks activity scope; Disconnect →
  Connect and TICK "View data about your activities". Then rides import. (Ground truth also at
  `GET /integrations/strava/status?probe=true`.)
- **AUTH + DATA SECURITY — 7 increments shipped this session** (all pushed, verified; GDPR target).
  Memory `forma-auth-security` + **PRD Appendix I (Launch Readiness Checklist)** have the full map.
  Done: token encryption at rest; refresh rotation/revocation + `/auth/logout`; login timing fix +
  rate limiting; security headers; account status (`is_active`/`deleted_at`); GDPR export
  (`GET /users/me/export`) + erasure (`DELETE /users/me`) + purge script; cross-user isolation
  test suite (`tests/`, pytest, 4 passing). **RLS deferred to pre-launch** (app-layer + tests now).
  **RAILWAY NEW: set `TOKEN_ENCRYPTION_KEY` + run `python -m scripts.encrypt_integration_tokens`.**
- **NEXT (task #32, the one auth item left):** email verification + password reset — build
  pluggable/stubbed sender, wire Resend/Postmark at launch. Social login (Google/Apple) needs
  Gareth's OAuth apps. Everything else outstanding → PRD Appendix I.
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
