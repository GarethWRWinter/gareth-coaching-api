# The Forma orb — in-app rollout plan

The orb is the coach and the training zones made visible. It is the single
most recognisable brand asset, so it appears deliberately, at scale, and
always the same way.

## Principle
- **Editorial by rule.** Use the orb at **120px and up** — notes, debriefs,
  headers, handovers, hero moments. Below that line the zone chips carry the
  colour and `CoachGlyph` stands in.
- **The app floats, never seats.** In-app orbs are the signed cutouts on the
  shared CSS float treatment (`.f-orb`): a soft contact shadow directly
  beneath plus a zone-tinted floor caustic. No orb is ever composited on a
  photographic floor in-app, and there is **never a glow behind the orb** —
  presence lives in the floor shadow.
- **Two families, one law.** The **Forma orb** (flamme) is the coaching voice.
  The **zone orbs** are a single session's intensity: the same frosted sphere,
  its shell progressively crushed by the zone's power (calm at recovery,
  violently faceted at max effort).

## The kit
- `components/ui/orb.tsx` — `<Orb variant size tint dark breathe alt />`.
- `public/orbs/*.webp` — `forma-rest`, `forma-speak(-dark)`, `z1-rest` …
  `z7-max-effort` (+ `-dark`), 420px lossless cutouts.
- `lib/zones.ts` — `zoneFromIF()` (whole-ride intensity → zone) and
  `zoneFromWorkoutType()` (planned session → zone), each carrying the zone
  name, colour token, orb file, and floor-caustic tint.

## Placements
1. **Dashboard · A note from Forma** — Forma orb, 132, breathing. ✅ done
2. **Dashboard · debrief** — zone orb from the ride's IF, 150. ✅ done
3. **Coach chat · header** — Forma orb, ~120, breathing (speaking state next).
4. **Ride detail · hero** — zone orb from the ride's IF.
5. **Training / workout detail** — zone orb from the target workout type.
6. **Goal assess · coach-note** — Forma orb.
7. **Large empty states** — Forma orb (small empties stay chips/glyph).
8. **Session player (carbon)** — Race Radio: bold rest orb at 64; larger
   moments use the dark zone orb + `dark` shadow.

## Open decision (needs Gareth)
The current zone orbs predate the finalised **z1–z7** palette, so their liquid
colours don't match the chips: the Endurance orb is navy while the Endurance
zone token is green (#3E8E7E), Tempo is green vs amber, Recovery is teal vs
blue. `orbTint` keeps each composition cohesive for now, but the clean fix is
to **re-render the zone orb set** as frosted spheres with the finalised zone
liquid colours + progressive crush, matching the signed Forma master. Then orb
and chip colours reconverge and `orbTint` collapses back into `color`.
