---
title: 'Conversational Onboarding'
slug: 'conversational-onboarding'
scope: feature
status: discovery
parent: cycling-coach/multi-user-auth.md
children: []
created: 2026-05-05
updated: 2026-05-05
resolution: 6/7
---

# Conversational Onboarding

> Part of [Multi-User & Auth](multi-user-auth.md), which is part of [AI Cycling Coach (Forma)](../cycling-coach.md)

## Purpose

First contact with Forma must feel like meeting a coach, not signing up for SaaS. Most apps onboard via forms because forms are easy to build — but for a coach product, the form is a category mistake. A form establishes a transactional relationship from minute one.

Conversational onboarding instead has Forma speak first — by voice or text — and ask open questions: "What are you training for?", "What's the rest of your life look like?", "Tell me about a session that went well recently." From those answers, Forma extracts the structured profile he needs (goal, FTP, hours, history, life context, injuries) AND seeds his Layer C / Layer D memory with the relational context that makes him feel like a coach forever after.

This is also the moment the user first hears Forma's voice and forms an impression of his persona. Get this right and the relationship has the right starting energy. Get it wrong and they bounce.

## Behavior

### Entry

- New user lands on `/onboarding` immediately after email verification (full sign-up) or after accepting a secret-link invite.
- Cannot access dashboard, training, rides, or any feature until onboarding is complete (or explicitly skipped).
- "Skip for now" option exists but with a soft warning: *"Forma won't know you yet — coaching will be generic until you finish this. OK?"*

### Opening

The default coach speaks first, by synthesised voice (ElevenLabs) and text simultaneously, in a generic-but-warm intro that doesn't yet commit to a name:

> *"Hi — I'm going to be your coach. Before we start, one quick thing."*

### Shaping Forma (immediately after opening)

The coach is always **Forma** — there is no "what should I call you?" step, because naming is not the personalisation that matters and asking for it up front adds a decision cost at the exact moment we want activation. Instead, Forma invites the rider to shape *how it shows up*:

> *"I'm Forma, and I'll adapt to you. Some riders want me blunt, some want me warm. Want to set how I talk, and pick my voice and face? Takes ten seconds, or skip it and we'll tune as we go."*

Three independent, optional choices — each with a sensible default so the step can be skipped entirely:

- **Manner** (`coach_tone`) — Balanced (default), Empathetic, Stoic, Direct, Analytical, Playful. Each shows a one-line sample so the rider hears the difference. This is the primary personalisation.
- **Voice** (`coach_voice_id`) — a short gallery of voices to preview. Voice is where masculine / feminine / accent live. Default: a neutral house voice (ElevenLabs voice ID per OQ2).
- **Face** (`coach_avatar`) — an avatar chosen from the gallery. Default: house avatar.

**Decoupled, never coupled.** Manner, voice and face are set independently — "feminine and stoic" and "masculine and encouraging" are both one tap each. The product never bundles a gender with a manner, and never infers either from the rider's own gender. There is no `coach_gender` field; gender expression is simply whatever voice and avatar the rider picks.

**Optional custom name.** A single quiet setting — *"Prefer to call your coach something else? Name it."* — lets the rider rename Forma. It is **off by default**, not part of the required flow, and Forma remains the name everywhere in marketing and shared copy regardless.

On selection (any subset; unset falls back to defaults):
- `users.coach_tone` set (enum, default `balanced`).
- `users.coach_voice_id` set (ElevenLabs voice ID).
- `users.coach_avatar` set (avatar key).
- `users.coach_name` set only if the rider explicitly renames; otherwise stays `Forma`.
- All subsequent voice synthesis uses the chosen voice; all system prompts render the persona at the chosen tone and substitute `{coach_name}` (Forma by default).

Forma then moves straight into getting to know the rider (heard in the chosen voice for the first time):

> *"Good. Before I build your plan I want to understand who you are and what you're chasing. Take your time — speak or type, whichever's easier."*

Mic button is live by default. Text input is also live as a fallback.

### Changing it later

Manner, voice, face (and the optional name) are all editable in settings at any time. If a rider renames the coach, a soft confirmation frames it as cosmetic, not a coach-swap: *"You'll still be talking to the same coach — same memory, same plan, same relationship — just a new name and voice. OK?"*

### Conversation flow

Forma runs a conversation with a slot-filling state machine in the background. The slots, prioritised by importance:

| Priority | Slot | Example question |
|---|---|---|
| 1 | A-race goal + date | "What are you training for? Is there one event that matters most?" |
| 1 | Weekly hours available | "What's the rest of your life look like? When can you train, when can't you?" |
| 2 | Cycling history / identity | "Tell me about your cycling. What's the ride that made you fall in love with it?" |
| 2 | Recent form — good and bad | "Tell me about a session that went well recently. And one that didn't." |
| 2 | FTP + weight | "What do you already know about your body? FTP, weight, anything you've tested?" |
| 2 | Equipment | "What are you riding? Power meter, trainer model?" |
| 3 | Injuries + life events | "Anything I should know — old injuries, things you're worried about, weeks you can't ride?" |
| 3 | B/C races | "Anything else on the calendar this year?" |
| 4 | Coaching preferences | "When you've trained well in the past, what worked? Direct? Encouraging? Detailed?" |

Forma asks one question at a time, in plain conversational English. He doesn't number the questions. He follows up naturally — if the user mentions something interesting, Forma can dig into it before moving on.

After each user turn, an extraction call (Haiku) updates filled slots from the cumulative conversation. Forma's next question prompt knows which Priority-1 and Priority-2 slots are still empty and prioritises accordingly. Priority-3 and 4 are skipped if the user is short on time.

### Confirmation

When all Priority-1 and Priority-2 slots are filled (or the user signals "let's go"), Forma wraps:

> *"Okay — here's what I've got. You're aiming for sub-12 at Manchester to London on August 15th, you train 8-10 hours a week, you've got a wedding mid-June, your last FTP test was 270W, and you mentioned a left-knee twinge in March that we'll keep an eye on. Got it right?"*

User confirms or corrects. Corrections re-trigger the extraction pass. When confirmed, Forma transitions:

> *"Perfect. Give me a minute and I'll have your first plan ready."*

### Plan generation handoff

- Confirmed profile written to `user_profiles` and `goals` tables.
- Episodic facts written to `mem_facts` (Layer C) — including the throwaway human details ("daughter's recital May 14", "wedding in Cornwall", "hates VO2 on Tuesdays").
- Initial Layer D semantic profile written from the conversation summary.
- Plan generation triggered (`POST /plans/generate`).
- User redirected to plan view with a Forma card: *"Here's the next 12 weeks. Want me to walk you through it?"*

### Fallbacks

- **One-word answers** ("yeah", "no") for >2 turns → Forma offers structured options: *"Want me to ask you a quick set of questions instead? We'll cover the basics in 2 minutes."* — falls back to a 6-question form.
- **User clearly uncomfortable / rambling without info** → Forma gently re-anchors: *"Let me ask something specific — what's your most important event this year?"*
- **Voice not working** (mic permission denied, browser unsupported) → silently switch to text-only, no Forma voice.
- **Forma hallucinated a fact** during confirmation → user correction overrides; corrected version is what gets persisted.

## Rules & Logic

- **Slot extraction model:** Haiku 4.5. Cheap and fast. Runs after every user turn.
- **Forma's response model:** Sonnet 4.5 for the conversational turn (better warmth + reasoning). Cached system prompt.
- **Voice synthesis:** ElevenLabs, voice TBD per OQ2 in product PRD. Streamed for low first-byte latency.
- **Voice input:** Web Speech API for v1. Whisper API for v1.1 if quality is poor.
- **Streaming responses:** Forma's text streams as it generates; voice synthesis kicks off after first sentence to minimise perceived latency.
- **Memory write timing:** facts are written **on user-confirmation** of the extracted profile, not eagerly. Avoids polluting memory with hallucinations or mid-conversation corrections.
- **Token budget:** ~25 turns × 5K input tokens + 500 output = ~140K input + 12.5K output. With prompt caching (system prompt stable), real cost ~$0.06–0.10 in Claude per onboarding.
- **Voice cost:** ~13 voice synthesis calls × ~200 chars = $0.40–0.60 per onboarding.
- **Total one-time cost per onboarded user: ~$0.60.** Trivial.

## Data

- **Reads:** none initially (new user).
- **Writes (on coach-identity selection, before slot-filling):**
  - `users.coach_tone`, `users.coach_voice_id`, `users.coach_avatar` (and `users.coach_name` only if the rider renamed; defaults to Forma)
- **Writes (on confirmation):**
  - `users.onboarded_at`
  - `user_profiles` (FTP, weight, weekly_hours, hard_days)
  - `goals` (A-race + B/C as separate records)
  - `mem_facts` (Layer C — episodic facts extracted from full conversation)
  - `mem_profile` (Layer D — initial semantic profile)
  - `conversations` + `conversation_turns` (full transcript stored for memory + audit)
- **API endpoints:**
  - `POST /onboarding/start` → conversation_id
  - `POST /onboarding/turn` → {message, voice?} returns {forma_message, voice_audio_url?, slots_filled, complete?}
  - `GET /onboarding/state` → current profile-being-built (for confirmation screen)
  - `POST /onboarding/confirm` → finalise, trigger plan generation

## Failure Modes

| Failure | Behaviour |
|---|---|
| Forma response p95 latency > 4s | UI shows "Forma is thinking…" indicator after 1.5s. If >10s, error toast with "Forma's a bit slow today. Want to try again or skip to a quick form?" |
| Voice synthesis fails | Silent fallback to text-only for the rest of the onboarding session. |
| Voice input not transcribed | Show transcript field for user to correct, or fall back to typing. |
| User abandons mid-onboarding | Conversation persisted; resume from last question on next login. After 7 days idle, prompt to either resume or restart. |
| Forma extraction misses key slot | Confirmation step catches it (user can add missing info). Worst case: Priority-1 slot still empty after 30 turns → force the explicit question: *"I need to ask directly — what's your A-race?"* |
| User says contradictory things across turns | Latest answer wins for slot extraction. Both versions retained in conversation transcript (Layer B). |
| Forma fabricates a "remembered" fact during onboarding (e.g., "since you said you ride mornings…" when user never said that) | This is the worst failure mode. Eval prompt explicitly tests for it. System prompt instruction: "Do not invent prior context — this is the user's first conversation with you." |

## Acceptance Criteria

- New user can complete onboarding in voice mode end-to-end on desktop Chrome and Safari.
- New user can complete onboarding in text-only mode if voice fails or is denied.
- Median onboarding duration: ≤ 8 minutes.
- ≥ 95% of completed onboardings produce a plan that the user accepts without manual editing.
- ≥ 25% of onboardings use voice input for at least one turn.
- Memory layer eval: after onboarding, asking Forma "what's my A-race?" and "when can I train?" returns correct answers in ≥ 95% of cases.
- Hallucination eval: in 100 simulated onboardings, Forma never invents a "prior" memory the user didn't share. Zero tolerance.

## Open Questions

- **OQ1:** Should onboarding offer a "5-minute quick-start" (form-based) for users who explicitly want to skip the conversation? Probably yes for accessibility / mood reasons. Lower priority for v1.
- **OQ2:** Voice personas must be locked before this ships (depends on product OQ2 — now requires both Forma and Forma voices, plus accent decision). Test 3-5 candidates per gender on a small panel; commit before M2.
- **OQ3:** Custom-name validation — profanity filter, length cap (probably 20 chars), single-word vs allow-spaces? Permissive but block clearly abusive names.
- **OQ4:** Does the chosen coach gender affect the system-prompt *persona* (different coaching tone) or only the *voice + name* (same tone, different surface)? My recommendation: same coaching substance, just different voice + name. Two personas would double the prompt-tuning work for marginal benefit. Revisit if testing shows users want differentiated styles.
