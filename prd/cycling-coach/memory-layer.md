---
title: 'Memory Layer (Pillar 2)'
slug: 'memory-layer'
scope: epic
status: discovery
parent: cycling-coach.md
children: []
created: 2026-05-05
updated: 2026-05-05
resolution: 4/7
---

# Memory Layer (Pillar 2)

> Part of [AI Cycling Coach (Marco)](../cycling-coach.md)

## Purpose

Memory is the moat. Every other Marco capability — coaching tone, plan adaptation, in-ride cues, post-ride debriefs, race reports — depends on Marco knowing who the user is across months and years. Without memory, Marco is a stateless chatbot wearing a coach's voice. With memory, Marco is the only coach who can say "you bonked here last year, let's pace this differently" and mean it.

The memory layer is also the structural foundation of Pillars 1 and 3:
- Pillar 1 (Marco everywhere) is only coherent if every surface reads the same memory.
- Pillar 3 (Marco rides with you) only feels coached, not scripted, if Marco recalls the rider during the workout.

This epic delivers the storage, write, retrieval, audit, and user-control machinery for Marco's memory.

## User Stories

### Returning to a familiar workout

*"Marco asks me how I'm feeling before the threshold session. I say tired. Marco says: 'Last time you said tired before this one, you still nailed the second interval. Let's start the warm-up and see how it goes — we can scale back if it's still in your legs at the first ramp.' That's the memory making the coaching feel real."*

### Quietly adapting around life

*"I told Marco three weeks ago I had a wedding in Cornwall. Today's plan view for that weekend shows Saturday as a rest day with a note: 'Cornwall — enjoy it.' I never had to remind him."*

### Hide-not-delete trust

*"I told Marco about a knee twinge in March. It's healed and I don't want to keep seeing it in my profile. I hide it. Marco still avoids stacking heavy sprint blocks without first checking in — he uses the fact, but doesn't surface it. That's the right balance of privacy and care."*

### Recall under pressure

*"Mid-conversation I ask Marco what my best 20-minute power was last summer. He answers correctly with the date, the ride, and the conditions. If he can't do this, the whole 'remembers you' promise is a lie."*

## Workflows

### Layered store

Memory has five layers, each with a different write rate, retention, and read pattern.

**Layer A — Structured athlete state.**
Numerical, queryable, updated on data ingestion.
Examples: FTP curve, weight curve, CTL/ATL/TSB time series, power-duration curve, HRV trend, ride-by-ride TSS, sleep, RHR.

**Layer B — Event log.**
Append-only timeline of *things that happened*.
Examples: every ride (id, date, planned vs actual, file source), every goal created/edited, every plan generated, every plan adaptation, every device connection, every Marco conversation turn, every voice session.

**Layer C — Episodic facts.**
Small, dated, natural-language statements extracted from conversations and ride debriefs.
Examples: "Felt strong on the Cicle Classic climbs, dropped my mate at km 60." / "Knee twinge on left leg week of 22 March, eased off." / "Wedding in Cornwall 13–15 June, no rides Saturday." / "Hates VO2 work on Tuesdays, tired by then." / "Goal: sub-12 for M2L 2026 (PR is sub-12 from 2017)." / "Daughter's recital 14 May."

**Layer D — Semantic profile.**
Slow-moving, distilled summary of *who this rider is*. Updated weekly.
Example: "All-rounder. ~3.9 W/kg. Strong steady-state, weaker repeated 30-second efforts. Tends to overtrain early in a block. Responds well to direct coaching, doesn't need hand-holding. Race head good — race-prep emotional steadiness above average."

**Layer E — Coach identity / running narrative.**
The current arc Marco is coaching. Updated every session.
Example: "Currently in build phase 2/4 for M2L 2026. 8 weeks out. Last week was a good adherence week. Next week is a rest week and he tends to feel guilty about rest weeks — pre-empt."

### Write paths

- **A and B** are written by the data pipeline (Strava webhook → FIT parse → DB upsert). Append-only audit on B.
- **C** is written by an extraction pass: after each Marco conversation turn or ride debrief, a small Claude (Haiku) call extracts dated facts in JSON, deduped against existing C entries by embedding similarity. Each fact is auto-tagged with a category (`general`, `medical`, `life`, `performance`).
- **D** is written by a weekly cron — a Claude (Sonnet) call that reads the prior week of layers A, B, C and rewrites the semantic profile.
- **E** is written every time Marco generates or adapts a plan (Sonnet).

### Read paths

- Every coach prompt is constructed by retrieving (i) the relevant slice of A and B for the question (deterministic SQL), (ii) the top-k semantically relevant C facts (vector search, including hidden facts), and (iii) D + E as fixed prefixes.
- All prompts use `{coach_name}` as a substitution variable for the user's chosen coach name. The system prompt template is identical regardless of coach name — only the substitution + the voice ID differ between users.
- All retrieval is logged (`marco_calls.retrieval_count`, `retrieval_log_id`) so we can audit "why did Marco say this".
- Retrieval respects the **hidden-but-retained** rule: hidden C facts ARE included in retrieval results passed to Marco, but Marco's system prompt instructs him not to quote them verbatim or surface them in user-facing summaries.

### Hide-not-delete UX

- User can hide any C-layer fact from "What Marco Knows About Me" view → `mem_facts.user_hidden_at` set.
- Marco's retrieval continues to surface hidden facts internally; system prompt forbids verbatim quotation.
- Safety-relevant categories (`medical`) trigger a soft warning on hide: *"Marco uses this when planning intensity. Hide from view, but Marco will keep using it. OK?"*
- Deletion audit log accessible to user — they can recover a hidden fact at any time.
- Hard-delete only on account deletion (GDPR right to erasure).
- Privacy policy explicitly states retention behaviour.

### Cross-screen surfacing (Pillar 1 leverage)

Memory is rendered as Marco's voice on every screen — see Coach Presence epic for surface-by-surface detail.

## Boundaries

### In scope

- Five-layer store with the schemas above.
- Postgres + pgvector for embeddings (no external vector DB).
- Hide-not-delete with soft-warning for medical category.
- Retrieval audit log accessible to admins.
- "What Marco Knows About Me" settings page (Layer C only — A/B are too granular for end-user view).
- GDPR data export (JSON archive of all layers) and account deletion (hard-delete after 30-day grace).
- Cross-user isolation enforced via Postgres RLS + automated tests asserting no leak.

### Out of scope (for this epic)

- Cross-user "shared" memory (e.g., team training contexts).
- Memory-driven coaching personas beyond Marco (parked under OQ6).
- Multi-modal memory (image, video) — text-only.
- External-source memory ingestion (e.g., import TrainingPeaks notes) — v2.

## Dependencies

- **`marco-core` service** must be the sole funnel for Claude calls so retrieval + caching + cost logging are centralised. **Dependency for every read path.** Stand up the skeleton in Milestone 1.
- **Postgres + pgvector extension** enabled.
- **Multi-User & Auth (Epic D)** for per-user RLS — but a single-user mode with a hardcoded user_id can ship in M1 ahead of Epic D.

## Success Criteria

- **Memory recall quality (eval):** Marco answers ≥ 90% of recall questions correctly on a held-out test set of 50 questions covering A/B/C/D/E layers. *("What was my best 20-min power last summer?", "Remind me what I said about my knee in March.", "When's the wedding?", "What kind of rider am I?")*
- **Cross-user isolation:** automated test suite — no cross-user PII leak across 100 simulated users sharing a vector index. Zero tolerance.
- **Retrieval latency:** p95 ≤ 200ms for top-k=8 against a user with 5K+ facts.
- **Hide-respecting:** in eval, Marco never quotes a hidden fact verbatim. Acts on it (e.g., reduces intensity) but doesn't surface it.
- **User-controlled deletion:** on user account deletion, all layers wiped within 24 hours; data export job completes within 5 minutes.

## Features

### F1 — Memory schema + write pipeline

Postgres tables for layers A–E. Append-only event log. Strava-webhook → fact-extraction pipeline. Idempotent.

### F2 — Embeddings + retrieval API

pgvector index on `mem_facts.embedding`. `get_context(user_id, query, k, include_hidden=true)` API consumed only by `marco-core`.

### F3 — "What Marco Knows About Me" settings page

Layer-C view with hide/unhide controls, category filter, search. Soft warning on medical-category hide. Audit log access.

### F4 — Weekly profile rewrite + arc update

Cron job + Marco-call wiring for D and E layers.

### F5 — Cross-user isolation tests

Property-based tests + RLS assertions. Runs in CI on every change to memory paths.

### F6 — GDPR export + account-deletion job

JSON archive of all layers + raw FIT files. Hard-delete worker.

## Open Questions

- **OQ1:** Episodic-fact dedup similarity threshold — how close in embedding space before we treat a new fact as a duplicate / refinement of an old one?
- **OQ2:** Memory size cap — does a user with 5 years of daily rides + conversations end up with 10K+ facts? At what point does pgvector retrieval cost or latency degrade? Need to model and decide an age-out / consolidation policy. (Likely: facts older than 18 months get summarised into D-layer profile and archived.)
- **OQ3:** Should Marco be able to *correct* his own memory? E.g., user mentions "I was joking about hating Tuesdays" — does Marco update the prior C-fact, mark it superseded, or write a new contradicting fact and let retrieval handle it?
- **OQ4:** Embedding model — local (open source) or hosted (OpenAI/Voyage)? Cost vs quality trade-off; affects retrieval quality more than any other choice.
