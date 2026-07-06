/**
 * FORMA wordmark — the letters plus the round flamme full stop.
 * The dot is sized in `em`, so it scales with whatever font-size the
 * parent sets. Drop it inside a styled <h1>/<span> that owns the type.
 */
export function FormaMark({ className = "" }: { className?: string }) {
  return (
    <span className={className}>
      FORMA
      <span
        aria-hidden="true"
        className="ml-[0.06em] inline-block rounded-full bg-vb-red align-baseline"
        style={{ width: "0.16em", height: "0.16em" }}
      />
    </span>
  );
}
