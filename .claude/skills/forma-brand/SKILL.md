---
name: forma-brand
description: FORMA visual brand and design system reference. Use whenever building or editing FORMA UI — app screens, components, landing pages, mockups, charts, emails. Trigger on "design", "restyle", "new page", "component", "chart colors", "brand", or any FORMA visual work. Guarantees new work matches the FORMA design system.
---

# FORMA brand — the design system

FORMA is Rouleur-editorial: paper ground, ink structure, one flamme accent, mono data. Bold type, hairline rules, flat surfaces, purposeful motion. The wordmark is FORMA followed by a round flamme full stop.

## Tokens (defined in `frontend/src/app/globals.css` @theme, names `vb-*`)

- **Paper** `#FAFAF7` (bg) · **Surface** `#FFFFFF` · **Chalk** `#F0F0EC` (sunken fills)
- **Ink** `#0B0B0C` (text, strong borders) · dim `#55554F` · muted `#9A9A94`
- **Flamme** `#FF3D00` (`vb-red`, THE accent) · bright `#FF5A2A` · dim `#D93400`
- **Borders**: subtle `#ECEBE6`, hairline `#D8D8D2`, strong = ink
- **Carbon** `#101012` + raised `#1A1A1E` + chalk text — dark instrument mode (live ride only)
- **Zone ramp** z1→z7 (cold→hot): `#4A6FA5 #3E8E7E #D9A62E #E8641B #E01B1B #B4123F #6E0E3C`
- Semantic: success `#3E8E7E`, warning `#D9A62E`

## Type

- **Display**: Archivo, weight 800, tracking -0.02em (`.f-display`). Big and confident. Never font-light at display sizes.
- **Body**: Inter Tight 400/500.
- **Labels + data**: IBM Plex Mono (`.f-kicker` for eyebrows: 11px, 0.16em, uppercase; `.f-data` tabular-nums for numbers). Numbers are a design feature: make them huge.
- **Signature**: Caveat, flamme, only for Forma's handwritten sign-off (`.f-signature`).

## Rules of composition

- Flat. No shadows, no gradients, no rounded-lg. Radius 2px (sm) or 4px (md) max.
- Hairline borders do the separating; a 2px ink rule (`.f-rule`) opens sections.
- Flamme is scarce: one hot element per screen. If everything is flamme, nothing is.
- The round flamme dot = the brand full stop (see `FormaMark`); also the live/active marker.
- Whitespace is generous; editorial numbered sections (`01 ·`) when content is sequential.
- Dark carbon (`.f-carbon`) is reserved for the live ride player and ride-mode surfaces.

## Motion (in globals.css, reduced-motion safe)

- `.f-rise` / `.f-stagger` entrance (fade + 12px rise, 60ms stagger).
- `.f-lift` hover (-2px + border-strong) for clickable cards; `.f-press` active scale.
- `.f-pulse-dot` flamme breathing for live elements; `.f-draw` rule wipe-in.
- `useCountUp` hook for data tiles. Motion is purposeful and brief, never decorative loops.

## Component kit (`frontend/src/components/ui/`)

`FormaMark` (wordmark + round dot) · `CoachGlyph` (carbon disc + flamme core, stands in for the Presence orb) · `Button` (ink / flamme / ghost / quiet / carbon; mono uppercase; `Arrow` slides) · `Card` (`rail` = flamme left rail, `lift`) · `Kicker` · `SectionHeader` · `DataTile` (count-up, `hot` state) · `EmptyState` (Forma speaks + one CTA) · `ZoneChip` · `ProgressSteps` (mono numbers) · `CoachNote` (the canonical Forma-speaks block: rail + prose + Caveat signature) · `Badge` · `Input`.

## Data-viz (`frontend/src/lib/palette.ts` — never hardcode data colours)

- `SERIES`: ink = primary line, grey = context, flamme = the story (TSB, actual-vs-plan), amber = HR, hairline grids. Thin strokes (1.5px), no area fills, mono tick labels.
- `ZONES` + `ZONE_BLOCKS` for intensity; `STEPS` for workout profiles; `BRAIN` for the memory graph (You=ink, Goals=flamme, Values=teal, Habits=blue, Insights=amber, People=plum, Rides=orange, Health=crimson, Life=grey, Rules=carbon).

## Don'ts

Soft Scandi cards, forest green `#36513F`, clay `#BB6647`, linen `#F3F1EA` (ALMANAC is dead) · font-light display type · shadows/gradients · square typed "." in the wordmark (use `FormaMark`) · flamme everywhere · centred body text walls · emoji in UI · orbs in-app (Presence orbs await their execution language; use `CoachGlyph`).

For words, load the `forma-voice` skill. Fuller visual reference: `mockups/forma.html` + live guidelines at ridewithforma.com/brand-guidelines.
