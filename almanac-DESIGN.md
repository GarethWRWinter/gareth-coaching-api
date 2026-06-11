# ALMANAC — Marco Design System v0.1

> A warm, editorial design system for an AI cycling coach. **VoiceBox's editorial bones, Arket's Scandinavian skin.**
> Keeps the magazine structure and confident typographic hierarchy of VoiceBox; replaces the brutalist black + aggressive red with a light humanist sans, generous space, and a muted natural palette grounded in ARKET and 2026 warm-neutral colour trends.
>
> *Design-system name only — decoupled from the product brand (PRD OQ1). Alternatives: Roadbook, Atelier, Field, Linen.*

## Concept

VoiceBox reads masculine because it is a **heavy sans-serif + aggressive red in a tabloid register**. ALMANAC keeps the things you loved — editorial layouts, strong hierarchy, a masthead/"Issue" device, content-over-chrome, single-accent discipline — but shifts the *register* from tabloid to **a quiet, premium almanac**: the kind of warm, considered annual a serious cyclist keeps. Calm, inclusive, unhurried. Every ride reads like a feature, not a database row.

**Three moves vs VoiceBox:**
1. **Type** — Archivo Black / heavy weights → a **humanist grotesk at Light/Regular**, larger and airier. Optional refined **serif** for Marco's long-form voice.
2. **Colour** — stark black/white + red → **warm linen/oat grounds, soft charcoal ink, deep forest-green accent**, restrained clay highlight, sage fills.
3. **Density & finish** — intentionally dense, hard black rules → **generous whitespace, hairline warm borders, matte (no glossy shadows)**.

---

## Colour

Warm, low-contrast, nature-grounded. Never pure black on pure white.

### Neutrals (the canvas)
| Token | Hex | Use |
|---|---|---|
| `paper` | `#F6F2EB` | App background — warm linen/oat (a warmed *Cloud Dancer*) |
| `paper-sunken` | `#EDE7DD` | Sunken sections, sand |
| `surface` | `#FCFAF5` | Cards — warm white |
| `surface-raised` | `#FFFFFF` | Modals, popovers |
| `line` | `#E4DCCE` | Hairline borders (default) |
| `line-strong` | `#CFC6B6` | Dividers, emphasis rules |

### Ink (type)
| Token | Hex | Use |
|---|---|---|
| `ink` | `#211E1A` | Primary text — warm espresso, never `#000` |
| `ink-2` | `#5C564C` | Secondary text, taupe-grey |
| `ink-3` | `#8C857A` | Muted text, captions, labels |

### Accents
| Token | Hex | Use |
|---|---|---|
| `forest` | `#38513F` | **Primary brand + actions.** Deep muted pine. Confident but calm |
| `forest-soft` | `#5C7A63` | Hover / lighter forest |
| `sage` | `#C3CDBC` | Badges, soft fills |
| `sage-tint` | `#E7EBE0` | Subtle backgrounds, selected states |
| `clay` | `#C06A48` | **The single highlight** — replaces VoiceBox's red exclamation. Reserve for ONE emphasis per view (e.g. today's key metric, a PR) |
| `clay-soft` | `#D98E70` | Clay hover/tint |
| `dusty-blue` | `#708DA0` | Recovery / "easy" semantics |
| `ochre` | `#C9A24B` | Tempo / caution semantics |

### Training-zone scale (warm, natural — replaces harsh blue→red)
Z1 `#8AA3B0` · Z2 `#9FB295` · Z3 `#CBA85C` · Z4 `#D8915A` · Z5 `#C06A48` · Z6 `#A24E36` · Z7 `#7E3A28`

> Rationale: a dusty-blue → sage → ochre → clay → rust gradient reads as effort/heat without the clinical neon of a standard PMC. On-brand and still legible.

---

## Typography

Lighter, larger, airier. Humanist warmth over geometric coldness.

- **Display & UI:** `Schibsted Grotesk` (humanist, warm; free) — fallback `Hanken Grotesk`, `Inter`, system-ui. Weights **300 / 400 / 500 only** (no black).
- **Long-form / Marco's written voice:** `Fraunces` (soft serif, optical) at Light — fallback `Newsreader`, Georgia. Used for debriefs, narration, the "note from Marco." This is the editorial warmth, and it signals *Marco is writing to you*.
- **Eyebrows / labels:** uppercase, letter-spacing `0.12em`, `ink-3` or `forest`.

### Scale
| Role | Size / line-height | Weight | Family |
|---|---|---|---|
| Display XL | 56 / 1.05 | 300 | Grotesk |
| Display | 40 / 1.10 | 300 | Grotesk |
| H1 | 32 / 1.15 | 400 | Grotesk |
| H2 | 24 / 1.25 | 400 | Grotesk |
| H3 | 19 / 1.3 | 500 | Grotesk |
| Body | 16 / 1.6 | 400 | Grotesk |
| Long-form | 19 / 1.7 | 300 | **Fraunces serif** |
| Small | 14 / 1.5 | 400 | Grotesk |
| Label | 12 / 1.4 · 0.12em · UPPER | 500 | Grotesk |

Headlines are **light and large**, not bold and loud. Let size and space carry weight.

---

## Space, shape, finish

- **Spacing scale (4px base):** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96. Be generous — desktop section padding 64–96.
- **Reading width:** long-form content max ~680px for comfort.
- **Radius:** 6px default · 2px small · full on avatars/pills. Soft, not bubbly.
- **Borders:** hairline `line` (1px). Borders define structure, not shadows.
- **Elevation:** **matte.** Avoid glossy/heavy shadows. Overlays only: `0 1px 3px rgba(33,30,26,.08)`.
- **Motion:** calm, 200–300ms ease-out. No bounce.

---

## Photography direction

The mood Arket sells: **natural light, matte, warm-but-desaturated grading, real people in real settings, lots of negative space.** For Marco:
- Real riders, real roads, real weather — not glossy stock.
- Warm, slightly muted grade (lift blacks, desaturate ~15%).
- Landscape + human moments (hands on bars, a turbo in a sunlit room, a climb at golden hour).
- Optional **forest/sand duotone** for hero treatments and empty states.
- Generous negative space so type can breathe over the image.

---

## Mapping to Marco's surfaces

- **Dashboard** — masthead (`ALMANAC · Issue 47 · Your Coach`, but set light not black), a Fraunces "note from Marco" pull-quote, stat cards in warm white with hairline borders.
- **Marco's debrief / narration** — Fraunces long-form, 680px column. This is where the serif earns its place: it makes Marco feel like he *wrote* to you.
- **Performance / PMC** — the warm zone scale; calm earthy charts, not neon.
- **In-ride "Race Radio"** — forest on paper, clay reserved for the live target callout.
- **Training calendar** — sage-tint for completed, hairline grid, lots of air.

---

## What to keep from VoiceBox / kill
- **Keep:** editorial layout grammar, masthead/"Issue" device, strong hierarchy, single-accent discipline, content-first.
- **Change:** type (light humanist + serif), palette (warm naturals), density (open it up), finish (matte hairlines).
- **Kill:** Archivo Black headlines, the aggressive red, hard black rules, the tabloid density. And retire the `questui` experiment — one decided system.
