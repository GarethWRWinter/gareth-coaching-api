# FORMA Brand v2 — Audit & Rollout Map

Source of truth: `docs/brand/FORMA-Brand-v2-source.html` (archived from
`~/Documents/Forma /FORMA Brand.html`, 14 Jul 2026). This doc records the
delta between the shipped v1 kit and the v2 guidelines, and where each
change lands in the codebase.

## 1. The mark — round dot → THE KITE

v1: FORMA wordmark + round flamme full stop (`forma-mark.tsx`).
v2: the full stop is a **kite** — a downward pennant, CSS-native:

```css
clip-path: polygon(0 0, 100% 0, 50% 100%);  /* flamme #FF3D00 */
```

Rules: the kite hangs from the banner/baseline (tip touches the baseline,
like a pennant hung from the finish gantry). It is never an arrow, never
rotated, never outlined. Type inside the kite only at display sizes ≥64px.
→ `components/ui/forma-mark.tsx` rebuilt; `.f-kite` utility in `globals.css`.

## 2. The six inks (+ chalk becomes THE PAGE)

| Ink    | Hex       | v2 role                                   | v1 role (changed?)            |
|--------|-----------|-------------------------------------------|-------------------------------|
| Ink    | `#0B0B0C` | text, strong rules                        | same                          |
| Paper  | `#FAFAF7` | **cards / sheets laid on the page**       | was the page background       |
| Chalk  | `#F0F0EC` | **THE PAGE** — app + site ground          | was sunken fills only         |
| Slate  | `#9A9A94` | muted text, quiet data                    | same                          |
| Carbon | `#101012` | ride mode / instrument surfaces           | same                          |
| Flamme | `#FF3D00` | THE accent — one thing per screen         | same, law now explicit        |

→ `globals.css`: `--color-vb-bg` → chalk, `--color-vb-surface` → paper,
white `#FFFFFF` demoted to `surface-raised` only.

## 3. Zone inks — full remap (data colour, never brand colour)

| Zone | v1        | v2        |
|------|-----------|-----------|
| Z1   | `#4A6FA5` | `#8E9196` |
| Z2   | `#3E8E7E` | `#4A72AE` |
| Z3   | `#D9A62E` | `#439D7C` |
| Z4   | `#E8641B` | `#D9AC34` |
| Z5   | `#E01B1B` | `#E86F22` |
| Z6   | `#B4123F` | `#D92420` |
| Z7   | `#6E0E3C` | `#B81743` |

Zone inks are DATA ONLY — they never decorate brand surfaces.
→ `globals.css` `--color-vb-z1..z7`, `lib/palette.ts`, `lib/zones.ts`.
Semantic tokens ride along: success → `#439D7C`, warning/amber → `#D9AC34`.

## 4. Type — three voices, Archivo goes Expanded

- **Announcer** — Archivo **Expanded (`font-stretch: 125%`)**, 700–900.
  Headlines, wordmark, numbers that shout. → `.f-display` gains stretch;
  `layout.tsx` loads Archivo with the `wdth` axis.
- **Coach** — Inter Tight, regular weights. Body, guidance, Forma's voice.
- **Timekeeper** — IBM Plex Mono, tabular. Kickers, data, deltas (`▲▼` only).

## 5. Coach presence — the pulsing dot

No avatar, no face, no disc-with-core. Forma is a **flamme dot**:
- **C1 still** — present, listening.
- **C2 pulsing** — thinking / typing.
- **C3 rippling rings** — speaking; carbon surfaces only.
→ `coach-glyph.tsx` reimplemented as `CoachDot` (compat export kept);
keyframes `f-dot-pulse` / `f-dot-ripple` in `globals.css`.

## 6. Product laws — "print, not pixels"

- No cards-with-shadows; sheets are flat paper on chalk with hairline rules.
- Square corners: 2px max radius (already policy — verified).
- Data is mono; trends are mono `▲▼` glyphs, never coloured pills.
- One flamme moment per screen.
- Nav IA: **TODAY · COACH · RIDES · FORM · PLAN** (+ Brain, Goals,
  Settings as secondary). → `components/layout/sidebar.tsx`.

## 7. Rollout surfaces

1. App kit (this repo): `globals.css`, `layout.tsx`, `forma-mark.tsx`,
   `coach-glyph.tsx`, `lib/palette.ts`, `lib/zones.ts`, `sidebar.tsx`.
2. Landing page: `GarethWRWinter/forma` → ridewithforma.com.
3. Brand guidelines artifact (scratchpad build → claude.ai artifact).
