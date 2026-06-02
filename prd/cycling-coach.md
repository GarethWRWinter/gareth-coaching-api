---
title: 'AI Cycling Coach (Marco)'
slug: 'cycling-coach'
scope: product
status: resolved
parent: null
children: ['cycling-coach/indoor-training-sessions.md', 'cycling-coach/memory-layer.md', 'cycling-coach/multi-user-auth.md', 'cycling-coach/conversational-onboarding.md']
created: 2026-04-13
updated: 2026-05-05
resolution: 8/8
version: 0.2
prototype: 'https://frontend-iota-seven-6je7r6040e.vercel.app/dashboard'
---

# Marco — AI Cycling Coach

> **v0.2** — Working draft, intended as a brief for Claude Code. Sections are sequenced from "why" to "what" to "how". Anything marked **OPEN** is a decision still to be made. The three pillars in §2 are non-negotiable; everything else is in service of them.

## Problem

Competitive amateur cyclists already have hardware, data, and a vague training plan. What they don't have, and can't afford, is a relationship with a coach who:

1. Builds a plan from *their* goal, life, history and context.
2. Adapts that plan continuously as life and form diverge from the model.
3. Walks them through each session indoors with live coaching.
4. Remembers what was said, what worked, what didn't, what hurt, what scared them.
5. Coaches their head as well as their legs — fear of the descent before a sportive, race-day nerves, motivation slumps in week 8 of a long block.

Existing tools each solve one slice. Nobody solves the whole relationship.

- **TrainingPeaks** — calendar and analytics layer. No coach. The coach is a human you pay separately, and most amateurs can't afford one.
- **Intervals.icu** — brilliant analytics, zero coaching, no plan generation, no companion.
- **TrainerRoad / Adaptive Training** — strong workout library and AT plan adaptation, but the personalisation is statistical, not relational. It does not know your life, your race history, your psychology, or your context. There is no one to talk to.
- **Join / Humango** — closer; AI plan generation exists. But the experience is "set the plan and follow it". There is no sustained companion. No memory of who you are across months. No mindset coaching.
- **Strava** — a social feed and ride store. Not a coach.
- **Strava's official MCP** (rolling out from 1 June 2026, included with Strava subscription) — an AI-native query tool that lets users slice their own Strava data conversationally. This is **analytics-as-a-service, not coaching.** It answers *"what was my best 20-min in June?"* It does not generate adaptive training plans, hold persistent memory across years of conversations, ride with you on the trainer, or coach the head as well as the legs. Strava is going down the data-analysis path; Marco is going up into the relationship layer. The two can coexist — Marco can in future consume Strava's MCP as a tool while remaining the coach. Strategically, Strava's move *validates* the AI-on-cycling thesis and trains users to expect AI on their data — which grows the addressable market for a real coach product.

## Vision

**One sentence:** Marco is a world-tour-level cycling coach in your pocket — a sport scientist and mindset coach combined, with persistent memory of every ride, goal, and conversation, who builds and adapts your training plan to *your* life and walks every kilometre with you, indoors and out.

**Why it exists.** Tadej Pogačar has a coach, a sports scientist, a nutritionist, a psychologist and a directeur sportif building his season around him. Competitive amateurs have a Garmin, a Strava subscription and a generic plan written for somebody who isn't them. Marco closes that gap. Not a plan-you-adapt-to. A coach who adapts to you.

**Wedge:** the *coach* is the product. The plan, the analytics, the ride execution, the race reports — those are the *evidence* of the coach. Every screen and every interaction must feel like one continuous relationship with one coach who knows you.

**Note on naming:** "Marco" is the **default coach name** within the app. Users pick their coach's name and voice during onboarding — Marco (male voice) is the default, Maria (female voice) is the equally-prominent alternative, and custom names are supported. The product brand itself is TBD (see OQ1) and is decoupled from the in-app coach name.

### The three pillars (non-negotiable)

These are the three things that, if they don't work, the product doesn't exist. Every feature ships in service of one or more.

#### Pillar 1 — Marco is everywhere, and Marco is one coach

Marco is not a chat tab. Marco is the operating layer of the product. He shows up on the Dashboard, in every ride detail, on the Performance page reading the trends, on the Goals page interpreting the route, in Training writing the next block, and in the live ride session pacing you through the workout.

The same persona, the same memory, the same voice, in every surface.

#### Pillar 2 — Persistent, layered memory

Marco remembers. Every ride, every conversation, every goal, every race report, every off-hand comment ("I've got a wedding in June, no Saturday ride that week"), every PR, every illness, every bike, every life event. This is the moat. No competitor can replicate years of relational context.

Memory is the engine that makes Pillar 1 feel human and Pillar 3 feel coached rather than scripted.

#### Pillar 3 — Marco rides with you. Indoor first.

Marco is not just an analytics layer that reads your Strava after the fact. The training plan is rideable *inside the app*, on a turbo trainer (Wahoo Kickr Core first), with live power, heart rate and cadence, ERG control, in-ride coaching cues, and a complete ride record written back to memory the moment the cooldown ends.

**v1: Desktop Chrome only** (Web Bluetooth limitation). **v1.1: Native iOS companion** (Capacitor wrapper) extends Pillar 3 to mobile. Outdoor live ride support follows in v2.

If a user can't do a session inside Marco — even on one supported device class — Marco isn't a coach yet. He's a critic.

## Users

### Primary — "The Working Cat 3"

- 35–50, cycles 6–10 hrs/week, full-time job, partner, often kids.
- Owns a power meter and a smart trainer (Wahoo Kickr / Tacx Neo / Wahoo Kickr Core).
- Does 1–4 A-races a year — sportives, gran fondos, regional road races, Cat 3 / Cat 2 amateur scene, 100–400 km events.
- Has used TrainingPeaks, Intervals.icu, TrainerRoad, Strava — has FTP literacy, knows what TSS is, knows what a build block is.
- Cannot justify £200–£500/month for a real coach. Has tried generic plans and felt them not fit their life.
- Pain: every Sunday they wonder *"is what I did this week the right thing for the goal in 12 weeks?"* and there is no one to answer.

### Secondary — "The Aspirational Cat 1/2"

- 25–40, racing seriously at amateur elite, 12–18 hrs/week.
- Wants the coaching infrastructure of a pro without the team.
- Higher data literacy. Will scrutinise the plan and push back. Marco needs to defend its choices.

### Tertiary (later) — "The Returning Athlete"

- Used to race, has come back after 5–10 years off, weight up, FTP down.
- Needs a coach to *re-learn* them. This is a memory-heavy persona.

### Anti-users (out of scope)

- Pure recreational cyclists with no power, no goals, no data.
- Multi-sport athletes (triathletes / runners). May come later.
- Junior athletes (under 18) — coaching minors carries different duty of care.

## Core Capabilities

### 1. Conversational onboarding (Marco's first contact)

Voice + text conversation that captures goals, history, life context, FTP, equipment, injuries — feels like meeting a coach, not filling a form. Generates the first plan as the closing act of onboarding. **Feature PRD:** `cycling-coach/conversational-onboarding.md`.

### 2. Adaptive training plans

Goal-driven, periodized plans that respond to what actually happens — not just what was planned. Multi-goal awareness. A/B/C race priority. Adaptive to fitness, life, missed sessions. Workout types span endurance, tempo, sweet spot, threshold, VO2max, sprint, recovery. Export to ZWO/ERG/MRC/FIT. **Status: largely BUILT.**

### 3. Omnipresent Coach Marco (Pillar 1)

Marco appears on every surface — Dashboard, Rides, Performance, Goals, Training, Workout Detail, in-ride. Same persona, same voice, same memory. Proactive nudges, post-ride debriefs, in-context metric explanations, chat conversations, voice mode. **Status: chat + voice BUILT; cross-surface presence in M2.**

### 4. Layered persistent memory (Pillar 2)

Five-layer store (structured state, event log, episodic facts, semantic profile, coach arc). Hide-from-view but retain-in-background editability. **Epic PRD:** `cycling-coach/memory-layer.md`.

### 5. In-app indoor ride execution (Pillar 3)

Web Bluetooth (FTMS) trainer pairing on desktop Chrome → live workout player → ERG control → in-ride voice cues → completed-ride record + Marco debrief. **Epic PRD:** `cycling-coach/indoor-training-sessions.md`.

### 6. Performance analytics, narrated by Marco

PMC (CTL/ATL/TSB), power profile, rider profiling (sprinter/climber/TT/all-rounder), zone distribution, race projection, FTP history. All numbers paired with Marco's interpretation in plain English. **Status: charts BUILT; Marco interpretation layer in M2.**

### 7. Race execution support

Race reports, post-race needs assessments, race-day pacing strategies, segment-level pacing on goals with GPX. **Status: race report flow BUILT; race-day mode in v2.**

### 8. Multi-user auth & data isolation

Email + password + OAuth (Google, Apple), per-user data isolation via Postgres RLS, session/refresh-token rotation, GDPR-compliant deletion. **Epic PRD:** `cycling-coach/multi-user-auth.md`.

## Boundaries

### In scope, v1 (Now)

- Cycling, indoor + outdoor (analytics on outdoor; in-app execution indoor only).
- Single-rider use (one human, one account).
- Strava ingestion + Dropbox FIT import + manual FIT upload. **A free Strava account is sufficient** — users do not need a paid Strava subscription. The endpoints we use (athlete, activities, streams, detailed activity) are available to free Strava accounts. The paid-Strava requirement in the developer program applies only to *our* developer-account registration, not to end users.
- Goal definition (event date, type, route via GPX, A/B/C tag, history notes).
- AI plan generation tied to goal + availability + history.
- Workout detail with targets (power, cadence, duration, zones).
- In-app ride execution on a smart trainer (Wahoo Kickr Core first), desktop Chrome, with ERG control, live telemetry, in-ride coaching prompts, auto-saved ride record. (Pillar 3.)
- Persistent multi-layer memory (Pillar 2).
- Coach Marco persona present on every screen (Pillar 1) — text + voice.
- Conversational voice/text onboarding.
- Performance analytics: PMC, FTP tracking, power curve, weekly load, ride list with TSS/IF/NP.
- Race reports / post-race needs assessments.
- Multi-user auth + secure account/data model.

### In scope, v1.1 (Next)

- **Native iOS companion (Capacitor wrapper)** — extends Pillar 3 to mobile. Trigger: ≥5 closed-beta users request it unprompted.
- Outdoor live ride support (mobile companion: in-ride voice cue, post-ride debrief on save).
- Health-data ingestion: Garmin Connect / Apple Health / Whoop (sleep, RHR, HRV, body battery).
- Coach proactivity — Marco messages first ("you said you had a bad sleep — let's pull tomorrow back to Z2").
- Beta program tooling (invites, feedback capture).

### In scope, v2 (Later)

- Multi-bike profile, indoor/outdoor power offset.
- Nutrition coaching (race-day fuelling plans tied to event GPX).
- Group / club mode (read-only — coach-of-friends sharing).
- Multi-sport (run / swim) — only after cycling retention hits target.
- Native Android companion.

### Explicitly out of scope (v1 and v1.1)

- Coaching minors.
- Medical advice (injury rehab is referred out, never prescribed).
- Real-time live ride video / Zwift-style world.
- Social feed.
- E-commerce (gear store, affiliate links).

## Success Criteria

### North star (operational)

**In-app ride share ≥ 40% by month 3 of a user's life.** This is the proof that Pillar 3 is real, which is the proof that the whole "rides with you" story works, which is the leading indicator for relationship quality, which trails into retention. Read it weekly.

### North star (strategic)

**18-month subscription retention ≥ 60%.** Cannot be measured for 18+ months but is the long-term proof the coach relationship is real. If users drop after 6 or 12 months, we've built a tool, not a coach.

### Supporting metrics

- **Performance proof.** Median TSS-per-week increased while maintaining freshness band (TSB ≥ -25), normalised by cohort starting fitness. Avoids vanity-metric trap of "FTP improvement %" that flatters returning riders and disadvantages near-ceiling racers.
- **Plan adherence.** Median % of planned sessions completed (any version — original or adapted). Target: ≥ 75%.
- **Coach engagement.** Median Marco conversations per active user per week. Target: ≥ 2 (operational), ≥ 3 aspirational once Pillar 1 is fully shipped. (One conversation = a multi-turn session, ~6 turns median.)
- **Voice usage.** % of conversations that include voice (mic) input. Target: ≥ 25%.
- **Memory recall quality.** Internal eval — when Marco is asked "what was my best 20-minute power last summer?" or "remind me what I said about my knee in March", he answers correctly. Target: ≥ 90%.
- **Referral rate.** Users acquired via existing-user referral. Target: ≥ 20% of new sign-ups by month 6 of public launch.

### Commercial guardrails

- **Gross margin ≥ 60%** after Anthropic + ElevenLabs + hosting + Strava per active user. (See cost model below.)
- **CAC payback ≤ 9 months.**

### Cost model

**Definitions:**
- A **conversation** = a multi-turn session opened from any surface. Median = 6 turns.
- A **Marco call** = one billable LLM invocation (one turn, one debrief, one extraction, etc.).

**Per-active-user monthly Marco workload (target engagement: 2 convs/week):**

| Activity | Volume | Model | Approx cost/call | Monthly cost |
|---|---|---|---|---|
| Conversation turns | 52 | Haiku 4.5 | $0.004 | $0.21 |
| Ride debriefs | 20 | Haiku 4.5 | $0.006 | $0.12 |
| Episodic-fact extraction | 26 | Haiku 4.5 | $0.003 | $0.08 |
| Plan generation/adaptation | 4 | Sonnet 4.5 | $0.09 | $0.36 |
| Weekly profile rewrite | 4 | Sonnet 4.5 | $0.075 | $0.30 |
| **Subtotal Claude** | | | | **~$1.07** |
| ElevenLabs voice synth (25% of turns) | ~13 | Creator tier | — | ~$0.50 |
| Hosting + Strava + Postgres (amortised at 100 users) | — | — | — | ~$0.30 |
| **Total per active user / month** | | | | **~$1.87** |

**Subscription target: £19.99/month (annual £180).** Annual must be ≥ 70% of users to keep blended margin healthy.

**No double subscription.** Users keep their existing (free) Strava account. Marco is one £19.99/mo line item — not Marco + Strava Premium + something else. This is a real positioning advantage over TrainingPeaks Premium (~$20/mo, typically stacked on Strava Premium for serious users). Lead marketing copy with this when we launch: *"Free Strava + Marco. That's all you need."*

**Headroom:** ~92% gross margin at target engagement. Massive cushion.

**Hard alerting threshold: $8/user/month.** If real usage hits this, escalate to Pro tier or investigate runaway loop.

**Cost-control mechanisms:**
- Tiered model routing: Haiku for fact extraction, ride debriefs, simple chat. Sonnet for plan generation, weekly profile rewrite, race reports. Opus only for explicit user-requested deep analysis.
- **Prompt caching from day 1** — `cache_control` on stable system-prompt + memory-profile prefix. Expected to cut Claude subtotal another 30-40% on cache hits.
- Hard per-user monthly token budget. Soft-cap at 80%, hard-cap at 100% with graceful "you've used your conversation quota this month" — heavy users escalate to Pro tier.
- Voice: cap voice synthesis at N seconds per session.

## Open Questions

- **OQ1:** Final pricing — £19.99/mo? £14.99/mo with annual at £150? Founding-member rate for closed beta?
- **OQ2:** Voice personas — the user picks their coach's name + voice during onboarding (Marco / Maria / custom). **Female voice locked: ElevenLabs voice ID `NbkKnEAZ7Bqw4EAkVEaz` (used for Maria + custom-female).** Male voice (Marco + custom-male) still TBD — pick before conversational onboarding ships. Accent for the male voice should match the female voice's register (test the Maria voice first, then audition male candidates that pair with it tonally).
- **OQ3:** Native iOS trigger — confirmed at "≥5 closed-beta users request it unprompted." Re-evaluate at Milestone 2 review.
- **OQ4:** What does "rider profile" classify on? (Today: All-Rounder. Taxonomy matters because Marco coaches differently per type.)
- **OQ5:** Health-data ingestion priority — Whoop first or Garmin Connect first? Depends on the beta cohort.
- **OQ6:** Multi-coach personas — future "Marco voiced as Cav's coach" / "as a sport psychologist"? Park.
- **OQ7:** Race-day mode — separate spec or part of in-ride?
- **OQ8:** Memory limit per user — soft cap on episodic-fact count, age-out policy. Address in memory epic.
- **OQ9:** Strava API rate-limit budget at 100 active users — model and cache strategy.
- **OQ10:** Coaching liability insurance — required pre-public-launch.

## Epics

Sequenced by dependency and user impact. The architecture below uses `marco-core` as the single funnel for all Marco calls — it must exist (at least as a thin wrapper) before any other epic ships features that talk to Claude.

### Epic A — Indoor Training Sessions (Milestone 1)

**Status:** in scope, v1. **Detail:** `cycling-coach/indoor-training-sessions.md`

**Outcome:** Gareth (and shortly: closed-beta) can pick a planned session, pair Wahoo Kickr Core, ride the workout inside the app on desktop Chrome, and have the result land in ride history with a Marco-written debrief written into memory.

### Epic B — Memory Layer (Milestone 1 skeleton, Milestone 2 full)

**Status:** in scope, v1. **Detail:** `cycling-coach/memory-layer.md`

**Outcome:** Five-layer memory store, retrieval API, hide-from-view editability, audit log. Marco's prompts route through `marco-core` and consume memory automatically.

### Epic C — Coach Presence (Milestone 2)

**Status:** in scope, v1. *(Existing focus from v0.1 — formal PRD to follow.)*

**Outcome:** Marco surfaces on Dashboard, Rides, Performance, Goals, Training, Workout Detail. Proactive nudges. Post-ride debriefs. In-context metric explanations. Powered by memory layer + `marco-core`.

### Epic D — Multi-User & Auth (Milestone 3 gate)

**Status:** in scope, v1. **Detail:** `cycling-coach/multi-user-auth.md`

**Outcome:** Email/password + OAuth, per-user RLS, refresh-token rotation, GDPR deletion, intermediate "secret-link, single-shared-instance" mode for early beta dogfooding before full multi-tenant.

**Child feature:** Conversational Onboarding (`cycling-coach/conversational-onboarding.md`).

### Epic E — Native iOS Companion (Milestone 2 / v1.1)

**Status:** in scope, v1.1. *(PRD to follow when triggered.)*

**Outcome:** Capacitor-wrapped iOS app reusing the Next.js codebase + native BLE plugin, distributed via TestFlight. Cost: $99/yr Apple Dev Program + ~2 weeks dev time.

**Trigger:** ≥5 closed-beta users request mobile in-ride support unprompted.

### Epic F — Brand, UX & Design System (pre-public-launch)

**Status:** pre-launch blocker. *(PRD to follow.)*

**Outcome:** Product naming finalised, domain acquired, logo + colour + typography + tone of voice locked, design system, marketing site, App Store / PWA metadata.

**Depends on:** Epic D.

### Epic G — Growth & Billing (pre-public-launch)

**Status:** pre-launch blocker. *(PRD to follow.)*

**Outcome:** Stripe subscriptions, pricing page, trial, usage analytics with per-user AI cost tracking, referral mechanism, churn detection with Marco re-engagement.

**Depends on:** Epics D + F.

---

## Appendix A — Current state inventory (5 May 2026)

This is what exists today, walked from the live URL.

### Working

| Surface | State |
|---|---|
| Auth (Gareth-only) | functional |
| Strava OAuth + activity ingestion | connected, 5,760 / 6,243 activities imported |
| Dropbox FIT-file import | connector wired |
| Manual FIT upload | button present |
| Dashboard | shows CTL/ATL/TSB/FTP, Marco message, rider profile, race-report nudge |
| Rides list | duration/distance/avg power/NP/TSS/IF |
| Performance page | tiles populate (CTL 25, ATL 34, TSB -9, weekly TSS); PMC chart renders empty axes — likely query/render bug |
| Goals | event date, GPX, A/B/C race tag, countdown, post-race needs-assessment, race report flow |
| Training (plan view) | active plan tied to "Manchester to London 2026", week view, planned vs done, plan phases stub |
| Workout detail | workout profile graphic, steps, target watts/cadence |
| Start Session → device pairing | Web Bluetooth chooser opens on desktop Chrome; the connect path itself runs |
| AI Coach | Marco persona, chat history sidebar, voice mic, suggested prompts |
| Settings | profile, FTP test, weekly hours, hard/easy/rest day calendar, Strava status |

### Broken / incomplete

1. **In-app ride execution end-to-end** — Web Bluetooth pairs on desktop but ERG control + telemetry capture + ride save not wired. This is what Pillar 3 hangs on.
2. **Marco inconsistency** — Marco appears on Dashboard and AI Coach, but not on Performance, Rides, Goals, Training pages as a coaching layer. He's a tab today; he should be the lens.
3. **Persistent memory layer** — chats persist as discrete conversations but there is no unified memory store. Pillar 2 is not yet built.
4. **Performance chart renders empty** — CTL/ATL/TSB tiles populate; chart axes draw but no series.
5. **Rider Profile says "Complete some rides with power data"** despite 5,760 rides, most with power.
6. **Multi-user** — single user (Gareth). No sign-up, no per-user data isolation, no per-user Strava OAuth, no email verification, no password reset.
7. **In-ride coaching cues** — even if a session can be ridden, Marco does not yet *speak* during the ride.
8. **Post-ride debrief** — completed rides do not yet trigger a Marco-authored debrief.

## Appendix B — Non-functional requirements

### Authentication & accounts (covered in Epic D)

- Email + password with verification. Password reset via email.
- OAuth providers: Google, Apple. Strava OAuth is integration-only, not auth-only.
- Per-user data isolation enforced at DB row level (RLS in Postgres).
- Session: refresh-token rotation, 30-day idle timeout, 90-day absolute.
- Optional MFA (TOTP) — not v1 blocker but pre-public-launch blocker.

### Data retention & privacy

- All ride data and memory layers retained while subscription active + 90 days.
- Account deletion: soft-delete 30 days, hard-delete after.
- **Memory layer C is user-hideable but retained in background** (per Pillar 2 spec). Marco continues to use hidden facts when planning, but does not surface them in user-facing views or quote them verbatim.
- Privacy policy must explicitly state: *"Marco retains coaching-relevant context even after you hide it from view, to keep your training safe. Account deletion permanently removes everything."*
- Safety-relevant categories (injuries, illnesses, surgeries, medications) get a soft warning on hide.
- GDPR / UK GDPR compliant. Data export = JSON archive of all layers + raw FIT files.
- Strava terms compliance (data not redistributed; user is the only consumer of their data).

### Strava API budget & Developer Program

- Strava: 100 requests / 15 min / app, 1000 / day / app (Standard Tier).
- Webhook-driven on new ride; bulk backfill rate-limited to fit window.
- Each user's initial 5–10 year backfill is queued, not real-time.

**Developer Program changes (announced May 2026):**

- **Standard Tier** (current) — direct OAuth integration, ≤10 athletes self-serve. Requires the registered developer's Strava account to have an active subscription from 1 June 2026 (existing devs: 30 June 2026). 3-month free promo available via code `a44e571570` if no current subscription.
- **Extended Access Tier** — higher rate limits, greater user capacity, prioritised support, Partner API eligibility, **no developer-account subscription required.** Apply once we hit ≥25 active beta users. This is the long-term lane.
- **Intermediary platform restriction** (1 June 2026) — apps routing data through third-party brokers are no longer supported. **We are compliant:** direct REST calls to `strava.com` from our FastAPI backend, no proxy / no broker. Audited in `app/services/strava_service.py`.
- **June 2027 technical migration** — auth tokens already in `Authorization: Bearer` headers (compliant). Base URL change is one-line: `STRAVA_API_BASE = "https://www.strava.com/api/v3"` → `"https://www.api-v3.strava.com"` in `strava_service.py` line 39. No use of the retiring `oauth/deauthorize` endpoint; should add `oauth/revoke` call to `disconnect()` for clean revocation (security hygiene, not a blocker).

### Reliability

- Uptime target: 99.5% v1 (~3.6 hrs downtime / month). 99.9% pre-public-launch.
- RPO ≤ 24 hrs (daily Postgres backup minimum). RTO ≤ 4 hrs.
- Live-ride session: must continue to work *offline* in browser if connection drops mid-ride. Telemetry buffered locally, synced on reconnect.

### Performance

- Dashboard first contentful paint ≤ 2.0 s on broadband, ≤ 4.0 s on 4G.
- Marco response p95 ≤ 4 s (text), ≤ 6 s (voice synthesis).
- Live-ride telemetry render @ 1 Hz minimum, target 4 Hz from BLE.

### Observability

- Structured logging on every Marco call (model, prompt token count, response token count, latency, retrieval hits, cost in cents).
- Per-user cost dashboard (admin).
- Memory-retrieval audit log.
- Sentry on frontend + backend.

## Appendix C — Technical architecture

### Current stack

- **Frontend:** Next.js (Vercel deploy — `frontend-iota-seven-…vercel.app`). TypeScript + Tailwind.
- **Backend:** FastAPI on Railway.
- **Database:** Postgres on Railway.
- **AI:** Anthropic (Claude). Voice: ElevenLabs (synthesis) + Whisper or ElevenLabs ASR.
- **Integrations:** Strava OAuth + activity webhook + REST. Dropbox.
- **Schema migrations:** Alembic.

### New components required for v1

- **`marco-core` service** — single source of truth for Marco. Wraps Claude calls. Owns prompt construction (memory retrieval + system prompt + user turn). Routes between Haiku/Sonnet/Opus per task. Implements prompt caching. Emits structured cost logs. **Used by every screen — there is no other path to Claude.**
- **`memory` service** — owns layers A–E. Postgres tables for A/B (time series + event log), Postgres + pgvector for C (episodic facts with embeddings), Postgres jsonb for D and E. Provides `get_context(user_id, query, k)` to `marco-core`.
- **`ride-session` service** — runs on the frontend (Web Bluetooth is browser-only). Manages BLE pairing, ERG control, telemetry capture, local buffer. POSTs ride record to backend on completion. Mirrors a thin server-side state for "ride in progress" so Marco can be aware mid-ride.
- **`auth` service** — multi-user, Postgres row-level security, OAuth provider support, refresh-token rotation.
- **`billing` service** — Stripe subscription, quota enforcement, plan tier (Standard / Pro).

### Mobile platform strategy

- **v1:** Desktop Chrome only for in-app rides. Web Bluetooth + FTMS protocol. Dashboard/chat/analytics work on any modern browser.
- **v1.1:** Capacitor-wrapped iOS app reusing the Next.js codebase + `@capacitor-community/bluetooth-le`. Distributed via TestFlight (free for closed beta, no App Store approval needed). Cost: $99/yr Apple Dev Program + ~2 weeks dev time.
- **v2:** Native Android companion (likely also Capacitor) once iOS is validated.

### Known technical debt

- Alembic migration discipline — formalise migration review per merge.
- Test coverage — add e2e tests on the Marco-call path and the ride-session path before public launch. Property-based test on memory retrieval (no PII leak across users).
- Observability — instrument before public launch, not after.

## Appendix D — Roadmap & milestones

Three horizons, no dates. Each milestone has an exit gate — a thing that must be true to move on.

### Milestone 1 — "I can train inside Marco" (Now)

**Outcome:** Gareth can pick a planned session, pair his Wahoo Kickr Core, ride the workout inside the app on desktop Chrome, and have the result land in his ride history with a Marco-written debrief.

**Work:**
- Stand up `marco-core` skeleton (model routing, prompt caching, cost logging).
- Stand up `memory` schema (layers A–E) — retrieval API stub, no full population yet.
- Fix Web Bluetooth ride flow on desktop Chrome end-to-end (pairing → ERG control → telemetry → save).
- Wire ride completion → Marco debrief → write to memory layer C.
- Fix Performance chart render bug.
- Fix Rider Profile "no power data" bug.
- Add in-ride voice cues at warm-up / interval start / cooldown (basic).
- "Secret-link, single-shared-instance" mode so 2-3 close friends can dogfood.

**Exit gate:** Gareth completes 5 consecutive planned sessions inside Marco with no manual intervention, and the debriefs reference at least one prior conversation or ride.

### Milestone 2 — "Marco feels like a coach" (Next)

**Outcome:** Memory layer is real, Marco shows up on every screen, the coaching feels continuous and human. Conversational onboarding live. Native iOS companion shipped to closed beta if trigger met.

**Work:**
- Memory service (layers A–E) fully populated and integrated.
- Marco surfaces on Dashboard, Rides, Performance, Goals, Training, Workout detail.
- "What Marco Knows About Me" settings page (with hide-not-delete UX + safety warnings).
- Voice quality pass on ElevenLabs voice selection + persona prompt (resolve OQ2).
- Conversational onboarding (text + voice) ships.
- Proactive Marco — daily morning message based on yesterday's ride + today's plan + life context.
- Race report flow rewritten to feed memory.
- Native iOS Capacitor wrapper if trigger met.

**Exit gate:** in a blind side-by-side eval, Marco's coaching responses score higher than a generic Claude+RAG baseline on relevance, recall, and *continuity* (does Marco remember the user). Gareth and ≥3 closed-beta users report "this feels like talking to a coach" unprompted.

### Milestone 3 — "Beta with friends" (Later)

**Outcome:** 5–15 cycling friends are using Marco daily. Multi-user, billing, retention data starts.

**Work:**
- Multi-user auth (per Epic D), per-user Strava OAuth.
- Stripe billing, quota enforcement.
- Onboarding flow polished (Strava connect → goal → first plan → first ride) under 10 minutes.
- Beta feedback capture in-app.
- **Apply for Strava Extended Access Tier** once we cross ~25 active beta users — drops the dev-account subscription requirement, lifts rate limits, signals seriousness to Strava. Required before public launch.

**Exit gate:** ≥ 10 paying beta users. Median user has completed ≥ 8 in-app rides. Cost-per-user dashboard live, blended cost ≤ £6/user/month.

### Beyond Milestone 3 — public launch

- Public sign-up, marketing site, pricing page (Epic F + G).
- Health-data integrations (Whoop, Garmin Connect, Apple Health).
- Outdoor live ride.
- Multi-bike profiles.

## Appendix E — Risks

| Risk | Mitigation |
|---|---|
| Claude + ElevenLabs cost exceeds subscription revenue | Tiered model routing, per-user token budget, voice caps, prompt caching, Pro tier for heavy users (cost model above) |
| Web Bluetooth dead-end on mobile blocks Pillar 3 at scale | Native iOS Capacitor companion in v1.1 (Epic E) |
| Strava API rate limit / access policy change | **Actively managed (May 2026):** direct integration audited (compliant with intermediary restriction); token-in-headers already correct; June 2027 base-URL migration is a one-line change tracked in code. Multiple ingestion paths (Strava + Dropbox + manual FIT) as fallback. Extended Access Tier application planned at ≥25 users to lift rate limits. |
| Strava's official MCP becomes "good enough" and users skip the coach | Marco's wedge is *relationship + plan + execution*, not analytics. The MCP answers questions; Marco proposes actions, remembers context, rides with you. Lean marketing positioning into this: *"Strava tells you what you did. Marco tells you what to do next, and rides with you while you do it."* |
| Solo-dev bandwidth | Ruthless scoping per milestone. Claude Code as a force multiplier. No sport extension until cycling retention proven. |
| Memory privacy breach (cross-user PII leak) | RLS at DB layer, retrieval audit log, automated tests asserting cross-user isolation, no shared embedding namespace |
| Anthropic / ElevenLabs pricing or model changes | Provider abstraction in `marco-core` so a model swap is one config change. Hold a 25% margin buffer on cost ceilings. |
| Coaching liability — bad advice causes injury | Marco never gives medical or rehab advice; refers out. Disclaimers on plan generation. Insurance pre-public-launch. Hidden-but-retained injury memory keeps Marco aware even when user hides facts. |
| Differentiation erodes if TrainingPeaks ships its own AI coach | Memory layer is the moat; ship Pillar 2 fast and well. The real defence is *quality* of memory + relational coach voice + tightness of plan-adapt-execute loop. |

## Appendix F — Data model (first pass)

Postgres + pgvector. Indicative — to be hardened in implementation.

```
users (id, email, password_hash, created_at, …)
user_profiles (user_id, full_name, weight, ftp, max_hr, resting_hr, weekly_hours, hard_days)
strava_links (user_id, strava_athlete_id, access_token, refresh_token, expires_at)

goals (id, user_id, name, event_type, race_grade {A,B,C}, event_date, route_gpx_blob, history_notes, status)
plans (id, user_id, goal_id, generated_at, model_version, status)
plan_phases (plan_id, phase_index, name, start_date, end_date, target_focus)
sessions (id, plan_id, scheduled_date, name, description, planned_duration_s, planned_tss, status {planned, completed, skipped})
session_steps (session_id, step_index, type {warmup, interval, recovery, steady, cooldown}, duration_s, target_pct_ftp_lo, target_pct_ftp_hi, target_cadence)

rides (id, user_id, source {strava, dropbox, fit_upload, in_app}, source_id, started_at, duration_s, distance_m, avg_power, np, tss, if, fit_blob)
ride_session_link (ride_id, session_id)  -- actual ↔ planned

devices (id, user_id, device_type {power_meter, hr, smart_trainer, cadence}, ble_id, friendly_name)

-- Memory layers
mem_state_timeseries (user_id, metric, ts, value)               -- Layer A
mem_events (user_id, ts, event_type, payload_jsonb)             -- Layer B
mem_facts (id, user_id, ts_observed, fact_text, embedding,
           source_event_id, category {general, medical, life, performance},
           user_hidden_at, soft_deleted_at)                     -- Layer C
mem_profile (user_id, updated_at, profile_md)                   -- Layer D
mem_arc (user_id, updated_at, arc_md)                            -- Layer E

-- Marco conversations
conversations (id, user_id, started_at, surface {dashboard, coach, rides, …, onboarding})
conversation_turns (id, conversation_id, role {user, marco}, content, tokens_in, tokens_out, model, retrieval_log_id, created_at)

-- Cost / observability
marco_calls (id, user_id, ts, model, tokens_in, tokens_out, cost_cents, latency_ms, surface, retrieval_count, cache_hit)
```

## Appendix G — API surface (first pass)

REST. JWT auth. All endpoints per-user via RLS.

```
POST   /auth/signup
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout

GET    /me
PATCH  /me/profile

POST   /onboarding/start
POST   /onboarding/turn          -- {message, voice?} → {marco_message, voice_audio_url?, complete?}
GET    /onboarding/state         -- profile-being-built

POST   /integrations/strava/connect
DELETE /integrations/strava
POST   /integrations/strava/sync

GET    /goals
POST   /goals
PATCH  /goals/{id}
DELETE /goals/{id}
POST   /goals/{id}/route        -- GPX upload

POST   /plans/generate          -- {goal_id, available_hours_override?}
GET    /plans/active
GET    /plans/{id}
POST   /plans/{id}/adapt        -- triggers a Marco-driven re-plan

GET    /sessions?week=…
GET    /sessions/{id}
POST   /sessions/{id}/start     -- creates an in-app ride container
POST   /sessions/{id}/complete  -- {ride_telemetry blob, fit_file}
POST   /sessions/{id}/skip

GET    /rides?range=…
GET    /rides/{id}
POST   /rides/upload            -- manual FIT
GET    /rides/{id}/debrief      -- Marco-written

GET    /performance/pmc?range=…
GET    /performance/power-curve?range=…
GET    /performance/ftp-history

POST   /coach/converse          -- {surface, message, voice?} → {marco_message, voice_audio_url?}
GET    /coach/conversations
GET    /coach/conversations/{id}
GET    /coach/memory            -- "What Marco Knows About Me"
PATCH  /coach/memory/{fact_id}/hide       -- hide-not-delete
PATCH  /coach/memory/{fact_id}/unhide
PATCH  /coach/memory/{fact_id}            -- edit fact text
DELETE /coach/memory                       -- account-level GDPR erasure only

GET    /billing/subscription
POST   /billing/portal
```

## Appendix H — Glossary

- **CTL** — Chronic Training Load. 42-day exponentially weighted average of TSS. "Fitness".
- **ATL** — Acute Training Load. 7-day EWMA of TSS. "Fatigue".
- **TSB** — Training Stress Balance. CTL − ATL. "Form".
- **TSS** — Training Stress Score. Quantified ride load.
- **IF** — Intensity Factor. NP / FTP for that ride.
- **NP** — Normalized Power. Variability-corrected average power.
- **FTP** — Functional Threshold Power. Roughly 1-hour sustainable power.
- **ERG** — Smart-trainer mode that holds a target wattage regardless of cadence.
- **FTMS** — Fitness Machine Service. Standard BLE service for trainer telemetry + control.
- **A/B/C race** — race priority. A = peak event. B = important. C = training/tune-up.
- **RLS** — Row-Level Security. Postgres feature for per-row access control.
