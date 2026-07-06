---
title: 'Indoor Training Sessions'
slug: 'indoor-training-sessions'
scope: epic
status: discovery
parent: cycling-coach.md
children: []
created: 2026-05-01
updated: 2026-05-05
resolution: 5/7
---

# Indoor Training Sessions

> Part of [AI Cycling Coach (Forma)](../cycling-coach.md)

## Purpose

Indoor Training Sessions delivers Pillar 3 — Forma rides with you. The training plan must be rideable *inside the app*, on a smart trainer, with live power, heart rate and cadence streaming, ERG control, in-ride coaching cues, and a complete ride record written to memory the moment the cooldown ends.

This is not "build a better Zwift." Zwift, Wahoo Systm, TrainerRoad, Rouvy — all of them already do BLE pairing and ERG control well. The unique value is that **Forma is in the cockpit**. The trainer integration is the cost of admission. The actual feature is a coach who watches the rider in real time, encourages when they're nailing the target, gently nudges when they drift, and remembers this session next time they talk.

Without the live ride, Forma can only ever react after the fact, with whatever Strava decides to share, hours later. With it, Forma coaches the most important hour of the rider's day — and writes that hour into memory the moment the rider unclips.

**v1 device support:** Wahoo Kickr Core via FTMS, on desktop Chrome only (Web Bluetooth limitation). Native iOS companion follows in v1.1 — see Native iOS Companion epic.

## User Stories

### Founder dogfood (Milestone 1 exit)

*"I open the app on my MacBook on the trainer mat. I pick today's planned threshold session. I click pair, the chooser opens, I select my Kickr Core. ERG locks on, I start the warm-up, and the watts are right. Forma speaks at the start of the first interval ('here we go — 290 for 8 minutes, smooth and steady'). I finish the cooldown, the ride saves automatically, and ten seconds later there's a Forma debrief on the ride detail page that references how I felt going in (which I'd told him in chat that morning). That's the moment Pillar 3 is real."*

### Closed beta on a friend's setup

*"My mate Tom uses Windows + Chrome. Same flow. His Kickr Core pairs the same way. He doesn't have to install anything. The session saves to his (separate) account."*

### Reconnection during a session

*"Halfway through the warm-up the BLE drops out. The session keeps the workout going visually. After 3 seconds without samples, a small banner says 'Reconnecting…'. The trainer reconnects, ERG resumes, no data was lost — local buffer caught the gap. The cooldown starts on time."*

### Tab refresh tolerance

*"I accidentally hit refresh mid-interval. The page reloads. The session state was persisted to local storage, so I see 'Welcome back — your session is in progress, reconnect your trainer to continue.' I reconnect, finish, save."*

## Workflows

### Pairing

1. User clicks "Start Session" on a planned workout.
2. Pre-flight checklist screen: *"Connect your trainer (and HR strap if you wear one). Make sure Wahoo Companion app is closed — only one device can talk to your Kickr at a time."*
3. User clicks "Pair Trainer" → Web Bluetooth chooser opens (this requires a user gesture; cannot auto-trigger).
4. Browser shows nearby BLE devices advertising FTMS. User selects their Kickr.
5. App subscribes to FTMS service notifications: Indoor Bike Data (power, cadence, speed) + Fitness Machine Status (control state).
6. App acquires FTMS Control Point (write characteristic) for ERG commands.
7. Optional: HR strap pairing (separate Web Bluetooth call, Cycling Heart Rate Service).

### Live ride loop

- Workout step state machine drives the session: `warmup → step[0] → step[1] → … → cooldown → complete`.
- On entering each step, app sends ERG target watts via FTMS Control Point write (`Set Target Power`).
- Telemetry frames arrive at ~4 Hz from Kickr. Each frame: `{timestamp, power_w, cadence_rpm, speed_kph}`. HR strap frames arrive separately.
- UI renders: current target, current power, cadence, HR, step countdown, total elapsed.
- Local buffer (IndexedDB) writes every frame. Survives tab close / refresh / network drop.
- In-ride voice cues at: warm-up start, each interval start ("here we go — 290 for 8 minutes"), 30s before cooldown ("almost there, ease off in 30"), cooldown start, end-of-ride.

### Forma-in-cockpit (Milestone 1: basic; Milestone 2: full)

- **M1:** Pre-scripted voice cues at fixed transitions. Forma "speaks" the lines but doesn't react.
- **M2:** Forma can react to live data — if rider is consistently >10W under target for >30s, prompt: *"You're under target — anything wrong, or do we drop the interval?"*. Mid-session interaction via voice. Memory consulted for context.

### Ride completion

- On cooldown finish (or user manual stop) → confirmation modal *"Save this ride?"* (default Yes).
- Local buffer flushes to backend: `POST /sessions/{id}/complete` with telemetry blob + FIT file (locally generated from the buffer).
- Backend computes derived metrics (avg power, NP, TSS, IF) and creates `rides` row, links to `sessions` row.
- `forma-core` triggered: ride debrief generation (Haiku, ~$0.006). Debrief written to `mem_facts` (Layer C) and surfaced on ride detail page.
- User redirected to ride detail page with debrief visible.

### Reconnection / resilience

- BLE dropout → if no telemetry frame for 3s, show "Reconnecting…" banner. Browser auto-reconnect attempts every 2s for up to 30s.
- If reconnection fails → user prompted *"Lost your trainer. Try again, or save what you've got?"*
- Tab close / refresh → session state persisted to IndexedDB. On next page load, banner offers resume.
- Network drop (backend unreachable) → continues fully offline; sync on reconnect.
- Browser crash → on relaunch, IndexedDB still has the buffer; partial-ride recovery flow offered.

## Boundaries

### In scope (Milestone 1)

- Wahoo Kickr Core pairing via Web Bluetooth FTMS.
- ERG control (target watts).
- Live telemetry capture (power, cadence, speed) at 4 Hz.
- Optional HR strap pairing (Cycling HR Service).
- Local IndexedDB buffer with refresh / tab-close survivability.
- Step-based workout player with countdown UI.
- Pre-scripted voice cues (warmup / interval start / cooldown).
- Auto-save on completion, FIT generation, ride record creation.
- Forma-authored ride debrief written to memory.
- Desktop Chrome, Edge, Brave only (any Chromium with Web Bluetooth).

### In scope (Milestone 2 follow-on)

- Reactive Forma mid-ride (under-target detection, voice intervention).
- Other smart trainers: Tacx Neo, Elite, Saris (also FTMS-compliant).
- Native iOS companion (separate epic — Native iOS Companion).

### Out of scope (this epic)

- Outdoor live ride (recorded via mobile companion, post-ride sync only — separate epic).
- Resistance / SIM / SLOPE modes (only ERG for v1).
- Multi-trainer setups (only one trainer per session).
- Power meter pairing as primary power source (v1: Kickr is the truth).
- Steering / climbing simulators (Kickr Climb, etc.).
- Group workouts / multi-rider sessions.
- Wahoo proprietary BLE service (only standard FTMS).
- Native macOS app.
- Browser extension for trainer integration.

## Dependencies

- **`forma-core` skeleton (Memory Layer epic, M1 deliverable)** — for the post-ride debrief generation. Without it, the ride saves but no debrief.
- **`memory` schema (Memory Layer epic, M1 deliverable)** — for writing the debrief to Layer C.
- **Multi-User & Auth secret-link mode (Multi-User & Auth epic, M1 deliverable)** — to share the experience with 2-3 close friends for early dogfood.
- **Existing infra:** Postgres, Strava connection (for cross-checking ride creation), workout step data model (already built).

## Success Criteria

### M1 exit gate

Gareth completes 5 consecutive planned sessions inside Forma with **no manual intervention**:
- Pairing succeeds first attempt in 5/5 sessions.
- ERG holds target within ±3W for ≥95% of in-step time.
- Telemetry capture: zero data gaps >5s.
- Ride saves and creates a `rides` row with TSS/IF/NP within 10s of cooldown finish.
- Forma debrief is generated and references at least one prior conversation or ride for each session.

### Beta exit (≥3 closed-beta users)

Each beta user, on their own Kickr Core, on Windows or Mac Chrome:
- Completes onboarding pairing on first attempt without contacting support.
- Median rider rates the experience ≥4/5 on a single in-app prompt: *"How was your session in Forma?"*.
- Reports zero data loss across 5+ sessions.

### Operational

- p95 ride save latency: ≤ 10s from cooldown finish to ride detail page rendered with debrief.
- BLE reconnection success rate: ≥ 95% of dropouts reconnect within 30s without user intervention.
- Local buffer integrity: 100% — no ride ever loses data due to a tab refresh, network drop, or browser-level interruption.

## Features

### F1 — Web Bluetooth pairing flow

User-gesture-triggered pairing UI, FTMS service subscription, HR strap optional pairing. Pre-flight checklist.

### F2 — Workout step player + ERG control loop

Step state machine, FTMS Control Point writes for target watts, UI rendering of target/actual/countdown.

### F3 — Local telemetry buffer + FIT generation

IndexedDB write path, refresh-survivable session state, FIT file synthesis from buffer on save.

### F4 — Voice cues (basic, scripted)

Pre-recorded ElevenLabs cues OR live-synthesised cues for fixed transitions. Reuse existing voice infra.

### F5 — Ride save + Forma debrief pipeline

`POST /sessions/{id}/complete` endpoint, ride record creation, `forma-core` debrief generation, memory write.

### F6 — Reconnection + resilience

BLE dropout detection, auto-reconnect, tab-refresh resume flow, network-loss tolerance.

## Open Questions

- **OQ1:** FIT file generation — client-side (TypeScript FIT library) or server-side (Python from telemetry blob)? Client-side is faster but the FIT spec is finicky. Server-side is the safer first pass.
- **OQ2:** Voice cues in M1 — pre-rendered audio files (cheaper, lower latency) or live synthesis (more flexible, paves way for reactive Forma in M2)? Probably pre-rendered for the 5-6 fixed cues, live for anything reactive in M2.
- **OQ3:** What's the right behaviour if the user's planned session is e.g. 90 minutes but they only have 45 minutes? Do we offer "shorten to fit" via Forma, or just let them stop early and Forma notes it post-ride? M1: stop-early; M2: offer-shorten.
- **OQ4:** ERG smoothing — Wahoo's ERG can hunt around the target on cadence changes. Do we filter / smooth client-side, or trust the trainer? Trust for v1; revisit if it feels jumpy.
