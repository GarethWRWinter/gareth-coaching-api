---
title: 'Memory Layer (Pillar 2) — The Brain'
slug: 'memory-layer'
scope: epic
status: resolved
parent: cycling-coach.md
children: []
created: 2026-05-05
updated: 2026-06-14
resolution: 7/7
version: 2.0
reference: 'TIE Memory v2 — Taxonomy & App Lenses (blinklife.com/vishen/p/memory-v2/taxonomy-and-lenses)'
---

# Memory Layer (Pillar 2) — The Brain

> Part of [AI Cycling Coach (Marco)](../cycling-coach.md)
>
> **v2** — rearchitected after studying TIE Memory v2 (BlinkLife). The core change: Layer C is no
> longer a flat pile of embedded sentences — it is a **typed entity graph** whose relationships are
> where the intelligence lives. The user-facing rendering of this graph — **"Your Brain"** — is a
> flagship product feature, not a settings page.

## Purpose

Memory is the moat. Every other Marco capability — coaching tone, plan adaptation, in-ride cues,
post-ride debriefs, race reports — depends on Marco knowing who the user is across months and years.

v2 adds the deeper claim: **"knows you better than you know yourself" doesn't come from recalling
facts; it comes from traversing connections between them.** A coach who can follow the thread from
your son's Tuesday school runs to your missed intervals — and re-plan around it — is a companion,
not a chatbot. Marco is a **life coach and a cycling coach**: the whole life feeds the training.

## Architecture decision: build, not buy

**Own it: Postgres (existing Railway instance) + two tables.** Memory is the moat; we do not rent
the moat (no Zep/Graphiti/mem0/Neo4j). The traversals a coach needs are 1–2 hops — plain SQL.

- `mem_entities` — typed nodes: `id, user_id, type, kind, life_area, label, summary, attrs jsonb,
  visibility, status, source, source_ref, embedding (nullable), observed_at, hidden_at, created_at`
- `mem_edges` — typed connections: `id, user_id, from_id, to_id, edge_type, attrs jsonb, created_at`

**Cost model** (on top of the master PRD's ~$1.87/user/mo): extraction ≈ +$0.05–0.15 (Haiku pass per
conversation/debrief; taxonomy prompt is a stable cacheable prefix), storage ≈ $0 (≤50MB/user after
years), retrieval ≈ $0 (SQL — no per-query vendor fees, ever). **Net ≈ +$0.15–0.30/user/mo; margin
stays ~89–90% at £19.99.** Embeddings (when added) ≈ $0.001/user/mo.

## The taxonomy (v2) — ~10 types, tags not types

Docstrings are load-bearing: each type's definition **is** the extraction LLM's prompt
(`app/core/memory_taxonomy.py`). New type only when it is *extracted differently* and *holds
different data*; otherwise a `kind` tag.

| # | Type | What it is | Key tags |
|---|---|---|---|
| 1 | **Value** | Why you ride — identity, beliefs, principles | kind: value\|identity\|principle |
| 2 | **Goal** | Events + aspirations | kind: a_race\|b_race\|dream\|comeback · status |
| 3 | **LearningGap** | Agent-inferred weakness, avoidance, fear, blind spot | kind: physiological\|technical\|psychological\|pacing\|fueling |
| 4 | **Insight** | Coaching advice given / learning surfaced | **status: noted\|applied\|became_habit\|rejected** · source_ref |
| 5 | **Habit** | Recurring practice | cadence · streak |
| 6 | **LifeEvent** | Weddings, work crunch, school runs — constraints & moments | kind: constraint\|event\|milestone · date |
| 7 | **Person** | Wife, kids, physio, clubmates, rivals | relationship |
| 8 | **HealthSignal** | Injury, illness, sleep, stress | **visibility: private, never auto-surfaced** |
| 9 | **Procedural** | How to coach me — "be direct", "no Sunday messages" | kind: preference\|rule · strength: hard\|soft |
| 10 | **RideMemory** | Notable rides — the epics, the bonks | source_ref → ride_id |

Every entity carries **`life_area`** (training \| body \| mind \| life) — the clustering dimension of
the Brain view — and **`visibility`** (private by default; medical never auto-surfaced; future
club/social mode reads only an opt-in projection, never the private graph).

### The growth loop (edges)

```
Value —GROUNDS→ Goal —SURFACES→ LearningGap —ADDRESSED_BY→ Insight —BECAME→ Habit —SERVES→ Goal
                                                                    ↑ re-measured against ride/metric data (Layers A/B)
```
Edge types: `GROUNDS, SERVES, SURFACES, ADDRESSED_BY, BECAME, INVOLVES, CONSTRAINS, ABOUT`.

The **closed loop is the signature coaching move**: gap found in March → advice → habit → the data
proves it worked → Marco says so. `Insight.status` means Marco never re-suggests what failed and can
celebrate what stuck. **Plans are wiring, not a type** — a plan is the traversal of a Goal's edges;
nothing to drift out of sync.

### Layers A/B/D/E (unchanged roles, one source of truth)

- **A — structured state** (rides, PMC, FTP…) and **B — event log** stay as-is: Marco's objective
  ground truth, *referenced* by entities via `source_ref`, never duplicated into the graph.
- **D — semantic profile / E — coach arc** remain cache-friendly prompt prefixes, now **derived by
  traversing the graph**, not rewriting a fact pile.

## Lenses (Pillar 1 = N lenses over one graph)

No surface owns its own memory. Each foregrounds a subgraph: **Dashboard nudge** (today's workout +
active gaps + imminent LifeEvents), **Ride debrief** (this ride + linked workout + relevant
gaps/insights + comparable past rides), **In-ride** (Procedural + psychological gaps + today's
targets), **Performance** (trends + closed loops), **The Brain** (everything, user-facing).

## Flagship feature: "Your Brain"

The graph rendered as a **living organ** — the most intimate surface in the product and the visible
proof of the moat. Reference: `mockups/memory-graph-almanac.html` (approved).

- Force-directed canvas, ALMANAC palette; **continuous motion** (breathing nodes, swaying threads).
- **Two lenses:** Organic ↔ **Life areas** (training / body / mind / life clusters).
- **Type filters** (Values, Goals, Habits, Insights, Gaps, People, Life).
- **Hover** → label + the node's thread lights up, everything else recedes.
- **Click** → the memory's story: lifecycle (noted → applied → became habit), edges in plain
  English, provenance, **Hide** (hide-not-delete lives here).
- **Time scrubber ▶** — replay the year; nodes appear when the memory was born. The relationship
  made visible ("+9 this week").
- **Marco's reading of your brain** — the graph narrated in Marco's voice, signed by hand.
- Empty state: "Your brain starts with your first conversation."

## Write & read paths

- **Extraction:** after each coach conversation turn and each ride debrief, a Haiku call with the
  taxonomy prompt returns entities + edges (JSON). Dedup on (type, normalized label) similarity;
  existing entities are enriched, not duplicated. Failures are **logged loudly** — never swallowed.
- **Retrieval (`get_context`)**: compact text block for Marco's prompts — recent + high-degree +
  goal-adjacent entities, hidden facts included but flagged *never quote verbatim*.
- Hidden ≠ deleted: `hidden_at` set; excluded from Brain view; retained for coaching safety
  (medical soft-warning per v1). Hard-delete only via GDPR account deletion.

## Success criteria (carried from v1 + new)

- Recall eval ≥ 90% on the 50-question held-out set; **extraction eval**: labelled fixture set in CI
  (docstrings are prompts — test them like prompts).
- Marco references at least one cross-life thread per week of active use (the companion metric).
- Retrieval p95 ≤ 200ms; zero cross-user leakage (RLS + tests, per v1).
- Brain page renders 1K+ nodes at 60fps (canvas).

## Open questions (v2)

- **OQ1 (was OQ4):** embedding vendor for semantic retrieval — OpenAI text-embedding-3-small vs
  Voyage. Deferred: v2 ships with type/recency/graph retrieval; embeddings slot in behind
  `get_context` without schema change (column reserved).
- **OQ2:** consolidation policy at 10K+ entities (age-out into D-layer profile) — revisit at 1K.
- **OQ3:** Insight.status transitions — automatic (workout-completion + debrief evidence) vs
  Marco-confirmed. Start manual/heuristic, automate at M2.
