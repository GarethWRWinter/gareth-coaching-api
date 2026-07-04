# ALMANAC — Design Language

A portable creative brief for the ALMANAC visual system. Hand this file to any project (or any AI/designer) to reproduce the **exact** look, palette, type, and feel. Framework-agnostic — copy-paste CSS variables, with a Tailwind v4 block included.

> **One line:** *editorial bones, Scandinavian skin.* The structure and confidence of a print magazine, wearing the warm, light, restrained palette of a brand like ARKET. Calm, premium, unhurried, gender-neutral. Every screen should feel like a considered journal, not a dashboard — "a feature story, not a database row."

---

## 1. Design principles

1. **Warm, never stark.** Backgrounds are warm linen, not white. Text is soft espresso, *never* pure black. Borders are hairline and warm.
2. **Light type, generous air.** Large display type at *light* weights; whitespace carries the composition. Restraint over density.
3. **One calm accent.** Deep forest green is the single primary accent. A muted clay is the *one* highlight per view. Everything else is neutral.
4. **Editorial furniture.** Small uppercase letter-spaced labels (eyebrows), confident headlines, and a fine route-contour rule used as a divider.
5. **Matte, not glossy.** Structure is defined by hairline borders, not shadows. Avoid heavy elevation.
6. **A human signature.** A single handwritten gesture (a name, a sign-off) makes the product feel authored by a person.
7. **Colour carries meaning where it counts** — data/intensity blocks use a warm earth-tone scale instead of clinical neon.

---

## 2. Colour

Never pure black on pure white. All values below are the canonical tokens.

### Surfaces & ink
| Role | Hex | Notes |
|---|---|---|
| Paper (app background) | `#F3F1EA` | warm linen / oat |
| Paper sunken | `#ECE8DE` | sand fills, recessed areas |
| Surface (cards) | `#FFFFFF` | |
| Surface raised | `#FBFAF6` | popovers, hover |
| Ink (primary text) | `#23211C` | warm espresso — never `#000` |
| Ink secondary | `#615B50` | taupe-grey |
| Ink muted | `#948D80` | captions, labels, axis text |
| Border subtle | `#E7E2D7` | default hairline (1px) |
| Border | `#D6CFC1` | dividers / emphasis |
| Border strong | `#23211C` | rare; equals ink |

### Accents
| Role | Hex | Use |
|---|---|---|
| **Forest** (primary) | `#36513F` | primary actions, active states, key marks, primary data series |
| Forest soft | `#5C7A63` | hover / lighter forest |
| Sage | `#C3CDBC` | soft fills, positive bars |
| Sage tint | `#E9ECE2` | subtle backgrounds, positive chips, selected states |
| **Clay** (highlight) | `#BB6647` | the SINGLE highlight per view — emphasis, pending, attention, destructive |
| Clay soft | `#D2855B` | clay hover/tint |
| Dusty blue | `#7C95A3` | calm/recovery semantics, "form/balance" data |
| Ochre | `#C7A458` | tempo/caution semantics |
| Success | `#4C6747` | (a deeper forest) |
| Warning | `#C7A458` | (ochre) |

### Intensity / data scale (warm, earthy — replaces clinical blue→red)
Low → high. Use for any ordered/heat data (e.g. training zones, severity, density):
`#8AA3B0` · `#9FB295` · `#C7A458` · `#D2855B` · `#C06A48` · `#A24E36` · `#7E3A28`
(dusty-blue → sage → ochre → amber → clay → rust → deep)

### Chart / data-viz palette
- Gridlines `#E4DCCE` · axis text `#948D80` · axis lines `#D6CFC1` · hover cursor `#BCB3A3`
- Primary series `#36513F` (forest) · secondary `#BB6647` (clay) · tertiary/"balance" area `#7C95A3` (dusty, ~12% fill) · volume bars `#C3CDBC` (sage)
- Tooltips are **light**: white surface, hairline border, ink text. Never dark.

---

## 3. Typography

Three families. Sans-led (humanist), with a handwritten accent for human moments.

| Role | Family | Weights | Notes |
|---|---|---|---|
| **Display** | **Bricolage Grotesque** | 300 / 400 / 500 / 600 | headlines, section titles, big numbers. Use **light (300–400)** and large — never bold/black. |
| **Body / UI** | **Schibsted Grotesk** | 400 / 500 / 700 | the workhorse: body, labels, data, nav, buttons. (No weight < 400 — it doesn't exist.) |
| **Signature** | **Caveat** | 500 | a single handwritten gesture only (a sign-off / name). Never body text. |

Google Fonts import:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,400;12..96,500;12..96,600&family=Schibsted+Grotesk:wght@400;500;700&family=Caveat:wght@500&display=swap" rel="stylesheet">
```

### Type scale
| Token | Size / line-height | Weight | Family |
|---|---|---|---|
| Display XL | 52–60 / 1.04 | 300 | Bricolage |
| Display | 40 / 1.1 | 300 | Bricolage |
| H1 | 32 / 1.15 | 400 | Bricolage |
| H2 | 24–28 / 1.2 | 400 | Bricolage |
| H3 | 19 / 1.3 | 500 | Bricolage |
| Body | 16 / 1.6 | 400 | Schibsted |
| Small | 14 / 1.5 | 400 | Schibsted |
| **Eyebrow / label** | 11 / 1.4 | 500 | Schibsted · `text-transform:uppercase` · `letter-spacing:0.16em` · colour = ink-muted or forest |
| Big number | 44–48 / 1 | 300 | Bricolage · `font-variant-numeric: tabular-nums` · `letter-spacing:-0.02em` |

Headlines lean **light and large with negative tracking (`-0.01em` to `-0.02em`)**. Let size + space carry weight, not boldness.

---

## 4. Space, shape, finish

- **Spacing scale (4px base):** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96. Be generous; desktop section padding 64–96.
- **Reading width:** long-form text max ~680–820px.
- **Radius:** `sm` 4px (controls) · `md` 6px (cards) · `full` (pills, avatars). Soft, not bubbly; never sharp 0.
- **Borders:** hairline 1px `#E7E2D7`. Structure is border-defined.
- **Elevation:** matte. Avoid shadows; overlays only may use `0 2px 8px rgba(33,30,26,0.10)`.
- **Motion:** calm, 200–300ms ease-out. No bounce.

---

## 5. Signature components & motifs

**Eyebrow + headline** — every section opens with a tiny uppercase letter-spaced label over a light Bricolage title.

**Cards / panels** — `background:#FFFFFF; border:1px solid #E7E2D7; border-radius:6px;` matte. Group related stats as a single hairline-divided block (1px gaps over a border-subtle fill) rather than separate floating cards.

**Buttons**
- Primary: `background:#36513F; color:#fff; border-radius:4px;` hover → `#5C7A63`.
- Ghost/secondary: `border:1px solid #D6CFC1; color:#36513F; background:transparent;` hover → sage-tint.
- Destructive: clay `#BB6647`.

**Chips / badges** — positive: `background:#E9ECE2; color:#36513F; border-radius:full`. Attention: `border:1px solid rgba(187,102,71,.4); color:#BB6647`.

**Feature stat** — to spotlight one metric, fill its card solid forest `#36513F` with white text (one per view).

**The route-contour rule** (the ownable motif) — a fine wavy SVG line as a section divider / brand mark, in border-strong colour with a small clay dot marking "you are here":
```html
<svg viewBox="0 0 1000 22" preserveAspectRatio="none" fill="none" style="width:100%;height:22px;color:#D6CFC1">
  <path d="M0,15 C60,15 90,7 150,9 C210,11 240,18 300,16 C360,14 390,4 450,7 C510,10 540,17 600,14 C660,11 690,5 750,8 C810,11 840,15 900,12 C950,10 975,13 1000,12"
        stroke="currentColor" stroke-width="1.2" vector-effect="non-scaling-stroke"/>
</svg>
```

**Handwritten signature** — Caveat, forest colour, used once to sign an authored message:
`<span style="font-family:Caveat,cursive;font-size:34px;color:#36513F">Marco</span>`

**Data colour-blocks** — for ordered/intensity data, render each item as a *solid block* in its intensity-scale colour, with auto-contrasting text (ink on light blocks, white on dark) — the colour communicates the value at a glance. Add a small uppercase tag inside; let colour do the rest.

---

## 6. Imagery & illustration

- Natural light, **matte, warm but slightly desaturated** grading (lift blacks ~10%, −15% saturation).
- Real subjects in real settings — not glossy stock. Generous negative space so type breathes.
- Optional **forest/sand duotone** for heroes and empty states.
- Iconography: thin line icons (e.g. Lucide), `1.5px` stroke, ink-muted by default, forest when active.

---

## 7. Voice & tone

Editorial, warm, plain-spoken, quietly confident. Treats the reader as serious and capable. Short eyebrows, human headlines, copy that sounds *written by a person*. Avoid hype, exclamation, and jargon walls. Calm authority over loud enthusiasm.

**Hard rule: never use em dashes or en dashes in customer-facing copy.** They read as AI-generated. Use a comma, a full stop, or a colon in prose; a middle dot (·) between label fragments; a plain hyphen (-) in numeric and date ranges. Punctuate like a human texting, not an essayist.

---

## 8. Do / Don't

| Do | Don't |
|---|---|
| Warm linen grounds, espresso ink | Pure white bg / pure black text |
| Light, large Bricolage headlines | Bold/black brutalist headlines |
| Hairline warm borders | Heavy 2px black rules |
| Forest as the one accent; clay as the single highlight | Rainbow accents / multiple loud colours |
| Matte, border-defined surfaces | Drop shadows, glassmorphism, gloss |
| Warm earth intensity scale for data | Clinical blue→neon-red gradients |
| One handwritten signature moment | Script fonts in body or buttons |

---

## 9. Ready-to-paste tokens

### A) Framework-agnostic CSS custom properties
```css
:root {
  /* surfaces & ink */
  --paper:#F3F1EA; --paper-sunken:#ECE8DE; --surface:#FFFFFF; --surface-raised:#FBFAF6;
  --ink:#23211C; --ink-2:#615B50; --ink-3:#948D80;
  --line:#E7E2D7; --line-strong:#D6CFC1; --line-ink:#23211C;
  /* accents */
  --forest:#36513F; --forest-soft:#5C7A63; --sage:#C3CDBC; --sage-tint:#E9ECE2;
  --clay:#BB6647; --clay-soft:#D2855B; --dusty:#7C95A3; --ochre:#C7A458;
  --success:#4C6747; --warning:#C7A458;
  /* intensity scale */
  --z1:#8AA3B0; --z2:#9FB295; --z3:#C7A458; --z4:#D2855B; --z5:#C06A48; --z6:#A24E36; --z7:#7E3A28;
  /* type */
  --font-display:'Bricolage Grotesque', 'Segoe UI', sans-serif;
  --font-sans:'Schibsted Grotesk', -apple-system, 'Segoe UI', Helvetica, sans-serif;
  --font-script:'Caveat', cursive;
  /* shape */
  --radius-sm:4px; --radius-md:6px; --radius-full:9999px;
  --shadow-overlay:0 2px 8px rgba(33,30,26,.10);
}
body { background:var(--paper); color:var(--ink); font-family:var(--font-sans); line-height:1.6; -webkit-font-smoothing:antialiased; }
```

### B) Tailwind v4 (`@theme` in your CSS entry)
```css
@import "tailwindcss";
@theme {
  --color-paper:#F3F1EA; --color-paper-sunken:#ECE8DE; --color-surface:#FFFFFF; --color-surface-raised:#FBFAF6;
  --color-ink:#23211C; --color-ink-2:#615B50; --color-ink-3:#948D80;
  --color-line:#E7E2D7; --color-line-strong:#D6CFC1;
  --color-forest:#36513F; --color-forest-soft:#5C7A63; --color-sage:#C3CDBC; --color-sage-tint:#E9ECE2;
  --color-clay:#BB6647; --color-clay-soft:#D2855B; --color-dusty:#7C95A3; --color-ochre:#C7A458;
  --color-z1:#8AA3B0; --color-z2:#9FB295; --color-z3:#C7A458; --color-z4:#D2855B; --color-z5:#C06A48; --color-z6:#A24E36; --color-z7:#7E3A28;
  --font-display:'Bricolage Grotesque', sans-serif;
  --font-sans:'Schibsted Grotesk', -apple-system, sans-serif;
  --font-script:'Caveat', cursive;
  --radius-sm:4px; --radius-md:6px;
}
```
Then: `bg-paper text-ink border-line font-display text-forest`, etc. (If using Next.js, load the three families via `next/font/google` and map them to `--font-display / --font-sans / --font-script`.)

---

*ALMANAC is the name of the visual system; brand/product naming is decoupled and set per project.*
