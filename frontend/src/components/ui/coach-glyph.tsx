/**
 * Forma's presence glyph — a carbon disc with a flamme core.
 * A brand stand-in for the coach (one Forma, not a human face) and a
 * placeholder for the Presence orb once it is designed. Size it via
 * className (e.g. "h-20 w-20"); the flamme core scales to the disc.
 */
export function CoachGlyph({ className = "" }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-flex items-center justify-center rounded-full bg-vb-carbon ${className}`}
    >
      <span className="block h-[34%] w-[34%] rounded-full bg-vb-red" />
    </span>
  );
}
