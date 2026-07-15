/**
 * Forma's presence — brand v2. No avatar, no face, no disc: the coach
 * is a flamme DOT with three states.
 *   C1 "still"     — present, listening (default)
 *   C2 "pulsing"   — thinking / typing
 *   C3 "rippling"  — speaking; reserve for carbon surfaces
 * Size via the `size` prop (any CSS length) or --dot on the parent.
 */
export type CoachDotState = "still" | "pulsing" | "rippling";

export function CoachDot({
  state = "still",
  size,
  className = "",
}: {
  state?: CoachDotState;
  size?: string;
  className?: string;
}) {
  return (
    <span
      aria-hidden="true"
      data-state={state}
      className={`f-coach-dot ${className}`}
      style={size ? ({ "--dot": size } as React.CSSProperties) : undefined}
    />
  );
}

/**
 * Legacy export — earlier surfaces imported a carbon disc glyph sized
 * via className (e.g. "h-20 w-20"). Brand v2 retires the disc; the same
 * import now centres the still dot inside the old box, so every call
 * site inherits the new presence without touching its layout.
 */
export function CoachGlyph({ className = "" }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-flex items-center justify-center ${className}`}
    >
      <CoachDot state="still" size="34%" />
    </span>
  );
}
