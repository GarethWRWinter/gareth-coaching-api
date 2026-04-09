# Race Day Projection — Implementation Plan

## Concept
BestBikeSplit-inspired feature integrated into the goal detail page. Shows two performance scenarios overlaid on the elevation profile:
- **"You Today"** — finish time & pacing based on current FTP/fitness
- **"You on Race Day"** — finish time & pacing based on projected FTP if training continues

Like a financial investment trajectory: here's where you are, here's where you'll be.

**Design principle: inspiring, not demoralising.** Frame everything as opportunity and progress.

---

## Phase 1 — Backend: Race Projection Service

### New file: `app/services/race_projection_service.py`

**A. Physics model — `speed_from_power(power_w, weight_kg, gradient_pct)`**
Solves the standard cycling dynamics equation for speed:
- `P = P_gravity + P_rolling + P_aero`
- `P_gravity = m·g·sin(θ)·v`, `P_rolling = Crr·m·g·cos(θ)·v`, `P_aero = 0.5·CdA·ρ·v³`
- Newton's method to solve cubic for v
- Defaults: CdA=0.35 (hoods), Crr=0.005 (road), ρ=1.225 (sea level)
- Minimum speed clamp: 5 km/h (walking with bike on steep gradient)
- Maximum speed clamp: 80 km/h (safety/drag limit on descents)

**B. Pacing strategy — `calculate_pacing(ftp, weight_kg, elevation_profile, event_duration_hours)`**
For each segment in the elevation profile:
1. Determine **sustainability factor** from expected event duration:
   - ≤1h: 0.95×FTP, 1-2h: 0.88, 2-4h: 0.80, 4-6h: 0.75, 6h+: 0.70
2. Apply **gradient adjustment** to get target power:
   - Gradient >6%: ×1.12 (push hard, speed matters most here)
   - Gradient 3-6%: ×1.06
   - Gradient 0-3%: ×1.00
   - Gradient -3-0%: ×0.90 (soft pedal, aero gains diminishing)
   - Gradient <-3%: ×0.60 (coast/light spin, gravity doing work)
3. Cap max power at FTP×1.05 (sustainable for event-length efforts)
4. Calculate speed per segment using physics model
5. Calculate time per segment = segment_distance / speed
6. Determine power zone for each segment (from existing POWER_ZONES constants)
7. Return: per-segment `{distance_km, elevation_m, gradient_pct, target_power_w, speed_kph, zone, time_seconds}` + totals

**C. FTP/CTL projection — `project_fitness(current_ctl, current_ftp, days_until, experience_level, has_plan)`**
- Day-by-day CTL projection assuming structured training:
  - With plan: use avg weekly TSS from plan phases → daily TSS → CTL growth via exponential decay formula
  - Without plan: assume moderate load = current_ctl × 1.1 daily TSS (conservative growth)
- Apply taper in final 14 days (reduce load 40-60%, CTL dips slightly, TSB rises)
- FTP growth model (conservative, based on fitness level):
  - Beginner: FTP tracks CTL growth at 0.12 factor (10% CTL gain → 1.2% FTP gain)
  - Intermediate: 0.08 factor
  - Advanced: 0.05 factor
  - Elite: 0.03 factor
- Return sampled trajectory (every 3-7 days) for charting: `{date, ctl, ftp}`
- Include milestone labels: "Today", "Peak Training", "Taper Starts", "Race Day"

**D. Main function — `get_race_projection(goal, user, db)`**
1. Validate: needs FTP + weight + elevation_profile (otherwise return null)
2. Get current fitness (CTL/ATL/TSB) from metrics service
3. Calculate "current performance" using today's FTP
4. Project fitness to event day
5. Calculate "race day performance" using projected FTP (skip if event ≤7 days)
6. Build improvement summary (time saved, speed gain, FTP gain)
7. Return combined projection object

---

## Phase 2 — Backend: Schema & Endpoint

### Modify: `app/schemas/onboarding.py`
Add new Pydantic models:

```python
class PerformanceEstimate(BaseModel):
    estimated_time_seconds: int
    avg_power_watts: int
    avg_speed_kph: float
    ftp_used: int
    ctl_used: float

class PacingSegment(BaseModel):
    distance_km: float
    elevation_m: float
    gradient_pct: float
    target_power_watts: int
    target_power_pct_ftp: int
    estimated_speed_kph: float
    zone: str
    zone_name: str

class FitnessTrajectoryPoint(BaseModel):
    date: str
    ctl: float
    ftp: int
    label: str | None = None

class PerformanceImprovement(BaseModel):
    time_saved_seconds: int
    speed_gain_kph: float
    ftp_gain_watts: int

class RaceProjectionResponse(BaseModel):
    current_performance: PerformanceEstimate
    projected_performance: PerformanceEstimate | None = None
    improvement: PerformanceImprovement | None = None
    pacing_strategy: list[PacingSegment]
    fitness_trajectory: list[FitnessTrajectoryPoint]
```

### Modify: `app/api/v1/goals.py`
Add endpoint:
```
GET /goals/{goal_id}/race-projection → RaceProjectionResponse
```
- Returns 404 if goal not found
- Returns 400 if missing FTP, weight, or elevation_profile
- Calls `get_race_projection()` from the new service

---

## Phase 3 — Frontend: New Components

### A. Performance Comparison Cards
**New file: `frontend/src/components/race-projection/performance-cards.tsx`**

Two side-by-side cards with an arrow between them:

```
┌──────────────┐         ┌──────────────┐
│  You Today   │   →→→   │  Race Day    │
│              │         │              │
│   2h 45m     │         │   2h 33m     │
│  28.5 km/h   │         │  30.8 km/h   │
│   245W avg   │         │   262W avg   │
└──────────────┘         └──────────────┘
   ▲ 12 min faster · 17W stronger
   "8 weeks of training unlocks this"
```

- "You Today" card: slate-800 with blue-500 accent border top
- "Race Day" card: slate-800 with emerald-500 accent border top + subtle glow
- Arrow between: animated pulse, emerald colored
- Improvement line below: emerald text, inspiring framing
- If no projected (event too close): show single "Race Day Performance" card
- Responsive: stacks vertically on mobile

### B. Fitness Trajectory Mini-Chart
**New file: `frontend/src/components/charts/fitness-trajectory-chart.tsx`**

Compact Recharts AreaChart (~180px height):
- X-axis: dates from today to event day
- Y-axis (left): CTL
- Y-axis (right): FTP (watts)
- Single line: projected CTL growth (emerald/green)
- Area under curve: soft emerald gradient fill
- Key markers as ReferenceLine + label: "Today", "Taper", "Race Day"
- FTP milestone dots: show projected FTP at midpoint and event day
- Design: follows existing chart conventions (axes, grid, tooltip styles)

### C. Enhanced Elevation Chart with Pacing Overlay
**Modify: `frontend/src/components/charts/elevation-profile-chart.tsx`**

Add optional `pacingStrategy` prop:
- When provided, overlay a second line/dots showing target power per segment
- Color-code by zone: Z2 blue, Z3 green, Z4 yellow, Z5 orange
- Enhanced tooltip: add "Target: 265W (Z4 Threshold)" row
- Visual: thin colored line riding on top of the elevation area
- This uses Recharts `<Line>` overlaid on the existing `<Area>` inside the same `<ComposedChart>`
- Change base chart from `AreaChart` to `ComposedChart` (Recharts) to support mixed types

---

## Phase 4 — Frontend: Integration

### Modify: `frontend/src/app/dashboard/goals/[id]/page.tsx`

1. Add new query:
```typescript
const { data: projection } = useQuery({
    queryKey: ["race-projection", goalId],
    queryFn: () => goalsApi.getRaceProjection(goalId),
    enabled: !!goal?.route_data?.elevation_profile?.length && !!goal?.route_data?.elevation_profile,
    retry: false,
});
```

2. Add new section between stats row and elevation chart:
```
{projection && (
  <div className="space-y-4">
    <h2>Race Day Projection</h2>
    <PerformanceCards projection={projection} daysUntil={goal.days_until} />
    <FitnessTrajectoryChart trajectory={projection.fitness_trajectory} />
  </div>
)}
```

3. Pass pacing strategy to elevation chart:
```
<ElevationProfileChart
  data={goal.route_data.elevation_profile}
  pacingStrategy={projection?.pacing_strategy}
/>
```

### Modify: `frontend/src/lib/api.ts`
- Add `RaceProjection` TypeScript interfaces
- Add `goals.getRaceProjection(id)` method → `GET /goals/{id}/race-projection`

---

## File Summary

| File | Action | What |
|------|--------|------|
| `app/services/race_projection_service.py` | **CREATE** | Physics model, pacing, FTP projection |
| `app/schemas/onboarding.py` | **MODIFY** | Add 5 new Pydantic models |
| `app/api/v1/goals.py` | **MODIFY** | Add GET race-projection endpoint |
| `frontend/src/lib/api.ts` | **MODIFY** | Add types + API method |
| `frontend/src/components/race-projection/performance-cards.tsx` | **CREATE** | Today vs Race Day cards |
| `frontend/src/components/charts/fitness-trajectory-chart.tsx` | **CREATE** | CTL/FTP growth chart |
| `frontend/src/components/charts/elevation-profile-chart.tsx` | **MODIFY** | Add pacing overlay |
| `frontend/src/app/dashboard/goals/[id]/page.tsx` | **MODIFY** | Wire projection into page |

---

## Edge Cases & Graceful Degradation

- **No elevation profile**: Race projection section doesn't render
- **No FTP/weight**: Section shows CTA: "Set your FTP and weight to see race projections"
- **Event in <7 days**: Only show "Race Day Performance" (no projection comparison)
- **Event today/past**: Show "What your performance would look like today" (single card)
- **Very low fitness**: Frame positively — "Starting from here, 12 weeks unlocks significant gains"
- **API error/loading**: Skeleton state, then graceful fallback

## Build Order
1. Backend service + schemas + endpoint (testable via curl/API)
2. Frontend types + API method
3. Performance cards component
4. Fitness trajectory chart
5. Elevation chart pacing overlay
6. Goal page integration
7. Build check → zero errors
