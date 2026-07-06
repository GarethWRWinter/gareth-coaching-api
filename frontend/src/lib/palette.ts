/**
 * FORMA data-viz palette — the single source of colour for charts,
 * zones, workout steps and the Brain. No component should hardcode
 * a data colour; import from here.
 */

/** Training-zone ramp, cold → hot. Mirrors --color-vb-z1..z7. */
export const ZONES = {
  z1: "#4A6FA5",
  z2: "#3E8E7E",
  z3: "#D9A62E",
  z4: "#E8641B",
  z5: "#E01B1B",
  z6: "#B4123F",
  z7: "#6E0E3C",
} as const;

/** Chart series — editorial: ink lines, grey context, flamme for the story. */
export const SERIES = {
  ink: "#0B0B0C",       // primary series (CTL / power)
  grey: "#9A9A94",      // context series (ATL / cadence)
  flamme: "#FF3D00",    // the story (TSB / actual vs plan)
  amber: "#D9A62E",     // secondary warm (HR)
  hairline: "#D8D8D2",  // grids, reference lines
  paper: "#FAFAF7",
  chalk: "#F0F0EC",
} as const;

/** Workout step colours (profile bars, session player). */
export const STEPS: Record<string, string> = {
  warmup: ZONES.z1,
  steady_state: ZONES.z2,
  interval_on: ZONES.z4,
  interval_off: "#E7E7E1",
  cooldown: ZONES.z1,
  free_ride: ZONES.z2,
  ramp: ZONES.z3,
};

/**
 * The colours of your memory — Brain graph categorical palette.
 * Deliberate mapping: you are ink, goals burn flamme, the rest of
 * your life in the FORMA race-graphics range.
 */
export const BRAIN: Record<string, { c: string; label: string }> = {
  user: { c: "#0B0B0C", label: "You" },
  goal: { c: "#FF3D00", label: "Goal" },
  value: { c: "#3E8E7E", label: "Value" },
  gap: { c: "#E01B1B", label: "Gap" },
  insight: { c: "#D9A62E", label: "Insight" },
  habit: { c: "#4A6FA5", label: "Habit" },
  person: { c: "#6E0E3C", label: "Person" },
  life_event: { c: "#9A9A94", label: "Life" },
  ride_memory: { c: "#E8641B", label: "Ride" },
  health_signal: { c: "#B4123F", label: "Health" },
  procedural: { c: "#1A1A1E", label: "Coaching rule" },
};

/** Zone key → colour for workout intensity blocks. */
export const ZONE_BLOCKS: Record<
  string,
  { bg: string; fg: string; label: string }
> = {
  recovery: { bg: ZONES.z1, fg: "#FFFFFF", label: "Recovery · Z1" },
  endurance: { bg: ZONES.z2, fg: "#FFFFFF", label: "Endurance · Z2" },
  tempo: { bg: ZONES.z3, fg: "#3A2E10", label: "Tempo · Z3" },
  sweet_spot: { bg: "#E4801C", fg: "#3A2A10", label: "Sweet spot" },
  threshold: { bg: ZONES.z4, fg: "#FFFFFF", label: "Threshold · Z4" },
  vo2max: { bg: ZONES.z5, fg: "#FFFFFF", label: "VO₂ · Z5" },
  sprint: { bg: ZONES.z6, fg: "#FFFFFF", label: "Sprint · Z6" },
  rest: { bg: "#F0F0EC", fg: "#55554F", label: "Rest" },
};
