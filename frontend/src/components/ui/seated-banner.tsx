import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Infinity-on-chalk editorial lockup — the brand-guidelines journal card.
 * A seated orb render (flat chalk ground, full shadow, nothing clipped)
 * sits on the left; the copy is a LAYER ON TOP (z-2 over the image's z-1),
 * pulled left with a negative margin so it bleeds over the chalk negative
 * space but never touches the orb. align-items:center keeps orb and copy
 * aligned. The render ground is the chalk brand colour (vb-sunken) so it
 * dissolves into the card.
 */
export function SeatedBanner({
  src,
  children,
  className,
}: {
  src: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        // Brand v2: chalk is THE PAGE, and the renders' ground IS chalk —
        // so the plate is page-coloured with a hairline frame, and the orb
        // sits directly on the page.
        "flex items-center overflow-hidden border border-vb-border-subtle bg-vb-bg p-6 sm:p-8",
        className
      )}
    >
      <img
        src={src}
        alt=""
        aria-hidden="true"
        draggable={false}
        className="relative z-[1] -mr-10 w-[260px] shrink-0 select-none sm:w-[320px]"
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />
      <div className="relative z-[2] min-w-0 flex-1">{children}</div>
    </section>
  );
}

/**
 * The flamme/zone colour-block tag from the guidelines (e.g. "EFFORT · Z4").
 * Mono, tight tracking, white on the zone colour.
 */
export function ZoneChip({
  color,
  children,
  className,
}: {
  color: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-block rounded-[2px] px-2 py-[3px] font-mono text-[10px] font-medium uppercase leading-none tracking-[0.16em] text-white",
        className
      )}
      style={{ backgroundColor: color }}
    >
      {children}
    </span>
  );
}
