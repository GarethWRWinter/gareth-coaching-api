---
title: 'Multi-User & Auth'
slug: 'multi-user-auth'
scope: epic
status: discovery
parent: cycling-coach.md
children: ['cycling-coach/conversational-onboarding.md']
created: 2026-05-05
updated: 2026-05-05
resolution: 4/7
---

# Multi-User & Auth

> Part of [AI Cycling Coach (Forma)](../cycling-coach.md)

## Purpose

Today the prototype is single-user (Gareth). The product cannot reach a single beta tester until at minimum a "secret-link, single-shared-instance" mode exists, and cannot reach paying users until full multi-tenant auth is shipped with proper data isolation, OAuth, password reset, and GDPR-compliant deletion.

This epic gates Milestone 3 (paid beta) but has an **intermediate deliverable** — the secret-link mode — that gates closed dogfooding in Milestone 1 / 2.

## User Stories

### Closed dogfooding (intermediate)

*"I want my mate Tom to try the app this weekend on his Kickr. I send him a magic link. He doesn't sign up. He sees Gareth's data masked behind a 'demo' wrapper, runs his own indoor session, and the data lands somewhere I can review without it polluting my account."*

### Real beta sign-up

*"My friend gets a beta invite email. She clicks the link, sets a password, connects her own Strava, does the conversational onboarding with Forma, gets her first plan, and rides. Her data is invisible to me. I can't accidentally see her conversations."*

### OAuth convenience

*"I'd rather sign in with Apple — I don't want another password. One tap, I'm in."*

### GDPR deletion

*"I cancelled. I want my data gone. I click a button, confirm, and 30 days later it's hard-deleted everywhere — Postgres, vector index, FIT-file storage, ElevenLabs voice samples, everything."*

## Workflows

### Intermediate: Secret-link, single-shared-instance mode (Milestone 1)

- Admin (Gareth) generates a one-time magic link in admin tools.
- Recipient clicks link → no sign-up form, just a "Welcome — you're using a shared instance" screen.
- A scoped `beta_user_id` is assigned to that session; data lands tagged with that ID.
- Recipient's data is invisible to Gareth's user account by default; Gareth has an admin view to inspect it for feedback purposes.
- This is **not** a real multi-user system — it's a feedback mechanism for early dogfooding while real auth is being built.
- Hard expiry: 90 days from link generation. After that, real account migration is offered.

### Full sign-up flow (Milestone 3)

- Email + password sign-up with verification email. Verification expires in 24 hours.
- Password complexity: ≥10 chars, mixed case + number + symbol. Standard zxcvbn check.
- After verification → conversational onboarding (see child feature PRD).
- Strava OAuth connected during onboarding.

### OAuth providers

- Google OAuth and Apple Sign In as v1 providers.
- Strava OAuth is **integration-only**, not auth-only. (Reasoning: Strava tokens expire and re-auth flow would interrupt sessions; we own the auth identity.)

### Password reset

- "Forgot password" link on login → email with single-use reset link, 1 hour expiry.
- Reset invalidates all existing refresh tokens (force re-login on other devices).

### Sessions

- JWT access tokens, 15-minute lifetime.
- Refresh tokens, 30-day idle timeout, 90-day absolute timeout, rotated on every use.
- Revocation: refresh tokens stored server-side; "log out everywhere" clears them all.

### Per-user data isolation

- Postgres Row Level Security (RLS) on every user-scoped table: `users`, `goals`, `plans`, `rides`, `mem_*`, `conversations`, etc.
- Application connects as a low-privilege role; RLS policies enforce `user_id = current_setting('app.user_id')`.
- Automated test suite: simulate 100 users, run 1000 randomised queries, assert no cross-user data ever returned.

### Account deletion (GDPR)

- "Delete account" in settings → confirmation modal with data export offered first.
- On confirm: account marked `deleted_at`, all sessions invalidated, user logged out.
- 30-day grace period — login during grace period restores the account.
- After 30 days: hard-delete worker wipes Postgres rows, pgvector entries, FIT-file blobs, ElevenLabs voice samples, Stripe customer record.
- Deletion completes within 24 hours of grace expiry. Email confirmation sent.

### Rate limiting

- Auth endpoints: 5 attempts per IP per 5 minutes on login, 3 per email per hour on signup.
- Password reset: 3 per email per hour, 10 per IP per hour.
- Failed login → exponential backoff per email.

## Boundaries

### In scope (full epic)

- Email + password sign-up with verification.
- Google + Apple OAuth.
- Password reset.
- Refresh-token rotation, "log out everywhere".
- Postgres RLS + cross-user isolation tests.
- GDPR deletion flow (soft → 30-day grace → hard-delete).
- Rate limiting on auth endpoints.
- Audit log of auth events (login, password reset, OAuth link, deletion).
- "Secret-link, single-shared-instance" intermediate mode (M1 deliverable).

### Out of scope (deferred)

- Multi-Factor Authentication (TOTP) — pre-public-launch blocker, not v1 beta blocker.
- Team / organisation accounts (coach-of-friends sharing) — v2.
- SSO / enterprise auth — out.
- Per-user per-feature flags / experiments — separate concern, not auth.

## Dependencies

- Postgres RLS available (yes, on Railway managed Postgres).
- Email provider (Postmark / Resend / SendGrid) for verification + reset emails.
- Apple Developer Program account for Apple Sign In ($99/yr — same one needed for Capacitor wrapper, so cost is shared).
- Stripe account for billing-tied deletion (Epic G).

## Success Criteria

- **Cross-user data leak:** zero. Automated test suite asserts isolation, runs on every change to auth or query layer.
- **Sign-up to first ride completion** for a new user, median ≤ 15 minutes (signup → email verification → conversational onboarding → first plan → first session). This is the onboarding success metric.
- **Login conversion** ≥ 95% — fewer than 5% of "click login button" events fail to land on the dashboard within 5 seconds.
- **Password reset success rate** ≥ 90% — >90% of reset emails opened result in a successful new-password set within 1 hour.
- **GDPR deletion completion** within 24 hours of grace expiry, 100% of the time.

## Features

### F1 — Secret-link intermediate mode (M1 deliverable)

Magic-link generation, scoped `beta_user_id`, admin inspection view. Ships before full multi-tenant.

### F2 — Email + password sign-up + verification

Signup form, verification email, verified flag, blocked features pre-verification.

### F3 — OAuth providers (Google, Apple)

OAuth integration, account linking (existing email account → OAuth provider).

### F4 — Password reset

Forgot-password flow, single-use reset email, refresh-token invalidation.

### F5 — Postgres RLS + isolation test suite

RLS policies on every user-scoped table, application connection setup, automated property-based tests.

### F6 — GDPR deletion

Self-serve account deletion, 30-day grace, hard-delete worker, audit log.

### F7 — Rate limiting + audit log

IP + email-based rate limits on auth endpoints, structured audit log.

### F8 — Conversational Onboarding

Voice + text first-contact onboarding with Forma. **Sub-PRD:** [Conversational Onboarding](conversational-onboarding.md).

## Open Questions

- **OQ1:** Email provider choice — Postmark, Resend, or SendGrid? Resend has the best DX and is cheapest at low volume; Postmark has the best deliverability reputation. Probably Resend for v1.
- **OQ2:** Apple Sign In requires hiding email behind a relay address — does that affect Strava-side deliverability of weekly digests? Probably fine but verify.
- **OQ3:** Secret-link mode — does the "demo" wrapper hide Gareth's data, or does the recipient see a fresh empty state? Empty state is cleaner but loses the "wow this looks real" effect during dogfooding.
