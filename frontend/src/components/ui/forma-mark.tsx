/**
 * FORMA wordmark — brand v2. The letters plus THE KITE: a flamme
 * pennant hung after the final A, tip touching the baseline. It is
 * the wordmark's full stop, never an arrow, never rotated.
 * Sized in `em` so it scales with whatever font-size the parent sets;
 * drop it inside a styled <h1>/<span> that owns the type (Announcer
 * voice: `.f-display`, Archivo Expanded).
 */
export function FormaMark({ className = "" }: { className?: string }) {
  return (
    <span className={className}>
      FORMA
      <span aria-hidden="true" className="f-kite ml-[0.14em]" />
    </span>
  );
}

/** The kite on its own — for list markers, sign-offs, page furniture. */
export function Kite({
  className = "",
  size,
}: {
  className?: string;
  /** CSS length for the kite width (height derives at 1.22×). */
  size?: string;
}) {
  return (
    <span
      aria-hidden="true"
      className={`f-kite ${className}`}
      style={size ? ({ "--kite": size } as React.CSSProperties) : undefined}
    />
  );
}
