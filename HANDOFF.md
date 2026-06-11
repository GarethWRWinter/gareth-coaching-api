# HANDOFF — the baton

> Whoever holds the baton has the turn. Read the protocol in `CLAUDE.md`.
> At the start of your turn: `git pull --rebase`, claim below. At the end: commit, push, release below.

Holder: FREE
Updated: 2026-06-11

## In flight / Next
- **ALMANAC design system is shipped across the whole frontend.** Spec in `almanac-DESIGN.md`,
  reference mockup in `mockups/marco-almanac.html`.
- Next polish passes (optional): audit every surface on a *real* data account (rich PMC/zone
  charts, debrief, rider profile), add a hero photo band, dark-mode pass.
- `voicebox-DESIGN.md` and `mockups/marco-{voicebox,questui}.html` are now superseded by ALMANAC —
  safe to delete when ready (kept for history for now).

## Recent handoffs
- 2026-06-11 — **ALMANAC rollout.** Re-skinned VoiceBox → ALMANAC (warm linen, humanist sans,
  forest accent, handwritten Marco signature). New fonts (Bricolage/Schibsted/Caveat), re-mapped
  `vb-*` tokens, restyled dashboard + sidebar + all dashboard pages + auth/landing/onboarding +
  shared UI primitives + all charts. Fixed the empty-PMC bug (dropped manual recharts ticks).
- 2026-06-07 — Collaboration protocol created (CLAUDE.md + HANDOFF.md). PRD updated to v0.3
  (Strava MCP confirmed live; Appendix A reconciled against code audit).
