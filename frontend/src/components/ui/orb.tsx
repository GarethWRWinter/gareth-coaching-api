import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * The Forma orb — the coach and the training zones made visible.
 *
 * This is the app-float treatment of the signed orb: a photographic
 * cutout that floats over a CSS contact shadow and a zone-tinted floor
 * pool. It is editorial by rule — use it at 120px and up (notes, debriefs,
 * headers, handovers). Below that line the zone chips carry the colour.
 *
 * The app never seats an orb and never puts a glow behind it; presence
 * lives entirely in the floor shadow.
 */
export function Orb({
  variant = "forma",
  orb,
  tint,
  size = 140,
  breathe = false,
  dark = false,
  alt,
  className,
}: {
  /** "forma" = the flamme coach orb; "zone" = a training-zone orb. */
  variant?: "forma" | "zone";
  /** Orb file base in /public/orbs, e.g. "z2-endurance". Overrides variant default. */
  orb?: string;
  /** Floor-caustic colour. Defaults to flamme for the Forma orb. */
  tint?: string;
  /** Rendered pixel size (square). Keep >= 120 for editorial legibility. */
  size?: number;
  /** Slow idle breathing (respects reduced motion). */
  breathe?: boolean;
  /** Carbon surface — deepens the contact shadow. */
  dark?: boolean;
  /** Accessible label; omit for purely decorative use. */
  alt?: string;
  className?: string;
}) {
  const file = orb ?? (variant === "forma" ? "forma-rest" : "z2-endurance");
  const src = `/orbs/${file}${dark && variant === "forma" ? "-dark" : ""}.webp`;
  const caustic = tint ?? (variant === "forma" ? "#FF3D00" : undefined);

  return (
    <span
      className={cn("f-orb", breathe && "f-orb-breathe", dark && "f-orb-dark", className)}
      style={
        {
          "--orb": `${size}px`,
          ...(caustic ? { "--orb-tint": caustic } : {}),
        } as React.CSSProperties
      }
      aria-hidden={alt ? undefined : true}
    >
      <img src={src} alt={alt ?? ""} draggable={false} />
    </span>
  );
}
