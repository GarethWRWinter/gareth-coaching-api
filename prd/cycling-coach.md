---
title: 'AI Cycling Coach'
slug: 'cycling-coach'
scope: product
status: resolved
parent: null
children: []
created: 2026-04-13
updated: 2026-04-13
resolution: 8/8
---

# AI Cycling Coach

## Problem

Competitive amateur cyclists train without structured, adaptive guidance. They ride 5-12 hours a week around full-time jobs and families, chasing event goals with no certainty that what they're doing is actually building toward anything.

The existing platforms don't solve this:

- **TrainingPeaks** and **Intervals.icu** give you data and charts, but no one to interpret them for you. You're left staring at CTL curves wondering "am I on track?"
- **TrainerRoad** and **Join** provide generic plans based on FTP, but they don't adapt to your life context — miss a week and you're off-script with no guidance on how to recover.
- **Human coaches** cost $100-300/month, have limited availability, and most amateurs can't justify the expense or don't feel "serious enough" to hire one.

The result: athletes guess. They overtrain, undertrain, burn out, or plateau — not because the data isn't there, but because no one is helping them make sense of it. Every ride feels like it might be meaningful, but there's no certainty, no accountability, and no one in their corner.

## Vision

A world-class cycling coach in your pocket — always available, deeply personal, and at a fraction of the cost of a human coach.

The app treats every rider like Tadej Pogacar: the lead rider with an entire support system built around them. Bespoke training plans that adapt to your goals, your schedule, and your physiology. A coach who knows your data, understands your context as a human and an athlete, and makes training purposeful and fun.

This isn't a training platform with an AI bolted on. The coach IS the product. Marco — the AI coach — is a partner, a companion, someone who holds you accountable, inspires you, explains what your numbers mean, and adjusts when life gets in the way. The experience should feel human, supportive, and enjoyable — like texting a coach who genuinely knows you.

## Users

### Primary: "The Competitive Amateur"

- **Demographics**: Cat 1-4 racer or sportive/gran fondo rider, 25-55 years old
- **Context**: Full-time job, family responsibilities. Cycling is their passion and identity. Trains 5-12 hours/week, often early mornings or lunch rides
- **Equipment**: Power meter, smart trainer (Wahoo/Tacx/Elite), HR monitor. Uses Strava religiously
- **Current tools**: TrainingPeaks or Strava free tier, maybe Intervals.icu for analytics. Has tried TrainerRoad but found it rigid
- **Core need**: Certainty that every ride is meaningful and building toward their goal. Someone to explain their data and adjust when they miss sessions or life gets complicated
- **Key frustration**: "I have all this data but I don't know what to DO with it. Am I training too hard? Not hard enough? Should I ride today or rest?"
- **Willingness to pay**: $15-25/month. Currently spending $0-15 on training apps. Would drop TrainingPeaks for this

### Secondary: "The Aspiring Competitor"

- **Demographics**: Newer structured cyclist, 20-40, moving from casual riding to event preparation
- **Context**: Signed up for their first sportive or gran fondo. Overwhelmed by power zones, TSS, periodization concepts
- **Core need**: Hand-holding. Needs the coach to explain basics, build confidence, and remove the intimidation of structured training
- **Key difference**: Needs more education, simpler language, and encouragement. Less data-literate than the primary persona

### Anti-users (explicitly NOT targeting)

- **Pro/WorldTour athletes** — already have human coaching staff, team infrastructure, and don't need this
- **Purely casual riders** — ride for fun, don't want structure, don't train with power
- **Data-only users** — want raw analytics without coaching interpretation (Intervals.icu serves them)

## Core Capabilities

Five pillars define the v1 product. Each one is a necessary condition for the coaching experience to feel complete.

### 1. Adaptive Training Plans

Goal-driven, periodized training plans that respond to what actually happens — not just what was planned.

- Generate plans from goals with A/B/C race priority (A-race drives peak/taper, B-races get mini-tapers, C-races get rest days)
- Multi-goal awareness: adding a new goal regenerates a unified plan that respects all events
- Plans adapt to current fitness (CTL/ATL/TSB), experience level, and available hours
- Workout types span the full spectrum: endurance, tempo, sweet spot, threshold, VO2max, sprint, recovery
- Structured workout steps with power targets, cadence targets, and intervals
- Planned-vs-did scoring: after every workout, compare plan to execution and rate quality out of 10
- Export to all major formats: ZWO (Zwift), ERG, MRC, FIT (Garmin/Wahoo)

**Status**: Core plan generation, multi-goal priority, workout assessment, and export are BUILT and DEPLOYED.

### 2. Omnipresent Coach Marco

Marco isn't confined to a chat window. He shows up across the entire app as a coaching presence.

- **Proactive dashboard nudges**: Marco comments on dashboard cards with contextual coaching. "Good recovery yesterday — you're primed for today's threshold session." "Your CTL has been climbing steadily. This is exactly the trend we want heading into your event."
- **Post-ride auto-debriefs**: After every Strava sync, Marco auto-generates a short debrief card on the ride: what went well, what to watch, how it affects the upcoming plan. Supportive tone, never demoralising.
- **In-context metric explanations**: Tap any metric (CTL, TSS, IF, power curve) and Marco explains what it means FOR YOU specifically. Not a generic definition — a personalised interpretation. "Your CTL is 62, up from 48 six weeks ago. For your sportive in 3 weeks, we want to be around 70-75. You're tracking well."
- **Chat conversations**: Full conversational coaching via text and voice. Multi-turn sessions with full rider context injected. Streaming responses.
- **Voice mode**: Talk to your coach hands-free. ElevenLabs text-to-speech for Marco's voice. Browser speech recognition for rider input.

**Status**: Chat + voice are BUILT. Proactive nudges, post-ride debriefs, and in-context explanations are NEW — the highest-priority epic.

### 3. Data Intelligence

Rich performance analytics, all made accessible through Marco's interpretation.

- Performance Management Chart (PMC): CTL/ATL/TSB trend over time
- Power profile: best efforts at standard durations (5s, 1min, 5min, 20min, FTP, 60min) with current form vs all-time
- Rider profiling: automatic categorisation (sprinter/climber/time trialist/all-rounder) with category scores
- Zone distribution: power and HR zone time breakdown per ride and over time
- Race projection: "you today" vs "you on race day" performance estimates with segment-level pacing
- Elevation profile with target vs actual power overlay
- FTP history and trend tracking
- Weekly training load charts (TSS, ride count, duration)

**Status**: All analytics are BUILT and DEPLOYED. Marco interpretation layer is NEW (part of Epic 1).

### 4. Indoor Training Sessions

Ride structured workouts directly from the app on a smart trainer via Bluetooth.

- Web Bluetooth API connection to smart trainers (Wahoo KICKR, Tacx Neo, Elite, etc.)
- Real-time power target display from workout steps
- ERG mode control (set trainer resistance to match target watts)
- Live data capture: power, cadence, HR, speed
- Step-by-step workout progression with countdown timers
- Session recording saved as a ride with full time-series data
- Auto-link completed session to the planned workout

**Status**: Session page exists (`/dashboard/training/[id]/session`) with recording UI. Bluetooth connectivity and ERG mode control are NOT YET IMPLEMENTED — this is Epic 2.

### 5. Accountability & Progress

The system that makes training sticky by showing proof it works.

- Planned-vs-did execution scoring (0-10) with component breakdown (duration, intensity, TSS, workout type match)
- Marco's supportive post-workout feedback with suggested plan adjustments
- Goal readiness assessment: fitness vs event demands
- Trend visualisation: "you're stronger than you were 6 weeks ago" with proof
- Race day countdown with fitness trajectory
- Progress toward A-race with clear leading indicators

**Status**: Execution scoring and feedback are BUILT. Goal readiness is BUILT. Trend narration by Marco is NEW (part of Epic 1).

## Boundaries

### In scope (v1)

- Cycling disciplines: road, gravel, MTB, track, indoor trainer
- Indoor AND outdoor training
- AI coaching via text and voice
- Strava and Dropbox integrations for data import
- Web application (responsive, mobile-friendly)
- Structured workout export (ZWO, ERG, MRC, FIT)
- Single-subscription pricing model

### Out of scope (v1)

- **Multi-sport**: No running, swimming, triathlon. Cycling only.
- **Social features**: No friend lists, leaderboards, clubs, or group challenges
- **Workout marketplace**: No buying/selling training plans from other coaches
- **Nutrition planning**: No meal plans, calorie tracking, or fueling strategy (Marco can discuss nutrition in chat, but no structured feature)
- **Equipment recommendations**: No bike fit, gear suggestions, or product reviews
- **Native mobile app**: Web-first (PWA acceptable). No iOS/Android native app in v1.
- **Third-party coach marketplace**: No human coaches using the platform to manage athletes

### Future consideration

- Multi-sport (running, swimming) if cycling PMF is proven
- Social/club features for group accountability
- Native mobile apps (iOS priority)
- Wearable integrations beyond Strava (Garmin Connect, Wahoo Cloud)
- TrainingPeaks import (token storage exists, sync not implemented)

## Success Criteria

### 6-month targets (PMF signal)

| Metric | Target | How Measured |
|--------|--------|--------------|
| Active users | 100 weekly active (opened app + completed 1+ workout/week) | Analytics dashboard |
| 30-day retention | >60% | Cohort analysis |
| 90-day retention | >40% | Cohort analysis (leading indicator for 2yr target) |
| NPS | >50 | In-app survey at 30-day mark |
| AI cost per user | <$10/month (Claude + ElevenLabs combined) | Cost monitoring per user_id |
| Paying subscribers | 50+ at $19.99/month | Stripe dashboard |
| Referral rate | 20%+ of new users from word-of-mouth | Attribution tracking |
| Coach engagement | 3+ Marco interactions/week per active user | Chat + nudge + debrief analytics |

### Long-term north star

- **2-year retention**: Users stay because they see proof they're getting fitter. Their numbers go up, their event results improve, and training feels purposeful.
- **Referral-driven growth**: Users love the app so much they tell their riding partners. "You need to try this coach app" is the primary acquisition channel.

## Open Questions

1. **Claude API cost at scale**: Proactive nudges + auto-debriefs = ~10-20 background LLM calls per user per day. Using Claude Haiku for lightweight calls (nudges, metric explanations) and Sonnet for deep coaching (chat, debriefs) keeps costs manageable. Need to model at 100 users: estimated $3-6/user/month for text. Verify.

2. **ElevenLabs voice cost**: Per-character pricing makes voice chat expensive at scale. Options: (a) limit voice minutes per month (e.g., 30 min/month included), (b) voice as premium tier add-on, (c) switch to a cheaper TTS provider, (d) use browser-native TTS for non-critical audio. Decision needed before billing launch.

3. **Strava API rate limits**: 100 requests per 15 minutes, 1000 per day per application. At 100 users syncing every 5 minutes via auto-sync hooks, this gets tight. Need: (a) intelligent batching, (b) webhook-first architecture (already partially built), (c) user-level throttling. Model the budget.

4. **Web Bluetooth compatibility**: Web Bluetooth API works in Chrome and Edge on desktop/Android. Does NOT work in Safari (iOS or macOS) or Firefox. For indoor training sessions, this means: (a) iOS users can't use Bluetooth features in-browser, (b) a native app or Capacitor wrapper may be needed for iOS Bluetooth. Acceptable limitation for v1? Or does this block the indoor training epic?

5. **Solo-dev bandwidth**: 5 epics in 6 months is aggressive. Minimum shippable path: Epic 1 (Coach Presence) + Epic 3 (Multi-User) → private beta with friends. Epics 2, 4, 5 can follow. Prioritise ruthlessly.

6. **Brand naming**: Product needs a name, visual identity, and tone-of-voice document before public launch. Include as Epic 4. No candidates yet — naming session needed.

7. **Data privacy & compliance**: Storing power, heart rate, and training data is health-adjacent. GDPR applies (UK/EU users). Need: privacy policy, data export capability, account deletion flow, clear consent language. Not a v1 blocker for private beta, but required before public launch.

## Epics

Sequenced by dependency and user impact. Epics 1-3 can run in parallel; 4-5 are sequential.

### Epic 1: Coach Presence (Highest Priority)

**Why**: User's #1 frustration is Marco being confined to the chat page. This is the core differentiator — Marco everywhere makes this feel like having a real coach, not just a chatbot.

**Features**:
- Proactive dashboard nudge cards (contextual, daily)
- Post-ride auto-debrief generation (triggered by Strava sync)
- In-context metric explanations (tap-to-explain on any data point)
- Marco insight cards on ride detail, goal detail, and performance pages
- Cost-aware LLM routing (Haiku for lightweight, Sonnet for deep)

**Depends on**: Nothing. Can start immediately.

### Epic 2: Indoor Training Sessions

**Why**: User's milestone #1. Completing a structured workout on a smart trainer from the app is a "wow" moment that proves the platform is a real training tool, not just analytics.

**Features**:
- Web Bluetooth smart trainer connection (FTMS protocol)
- ERG mode control (set resistance to target watts)
- Real-time workout player with step progression, countdown, and live data
- Session recording with time-series data capture
- Auto-link recorded session to planned workout + trigger assessment

**Depends on**: Nothing. Can start immediately. Note: Web Bluetooth limitation on iOS/Safari.

### Epic 3: Multi-User & Auth Hardening

**Why**: Required before any external user touches the product. Currently functional for a single user but needs hardening for multi-tenant use.

**Features**:
- Password reset flow (email-based)
- Email verification on registration
- Improved onboarding flow (guided, not just a quiz)
- User data isolation audit (verify all queries are scoped to user_id)
- Account deletion (GDPR right to erasure)
- Rate limiting on auth endpoints
- Strava OAuth per-user (already works, verify at scale)

**Depends on**: Nothing. Can start immediately.

### Epic 4: Brand, UX & Design System

**Why**: Required for public launch. The product needs a name, a visual identity, and design polish that matches the premium $19.99/month positioning.

**Features**:
- Product naming and domain acquisition
- Brand identity: logo, colour palette, typography, tone of voice
- Design system: component library, consistent spacing/sizing, dark mode refinement
- Onboarding redesign: first-run experience that hooks in 60 seconds
- Marketing/landing page
- App Store / PWA metadata

**Depends on**: Epic 3 (multi-user must work before public launch).

### Epic 5: Growth & Billing

**Why**: Enables the pricing experiment and revenue generation required for the 6-month PMF target.

**Features**:
- Stripe integration: subscription management, payment processing
- Pricing page with plan tiers (or single tier at $19.99/month)
- Trial period (14 days free?)
- Usage analytics: per-user AI cost tracking, feature engagement
- Referral mechanism (invite code or link)
- Churn detection: flag users who stop engaging, trigger Marco re-engagement

**Depends on**: Epics 3 + 4 (need multi-user auth and brand before charging).
