import * as React from "react";
import { cn } from "@/lib/utils";
import { ZONE_BLOCKS } from "@/lib/palette";

/** FORMA zone chip — mono label on the zone's ramp colour. */
export function ZoneChip({
  zone,
  className,
}: {
  zone: string;
  className?: string;
}) {
  const z = ZONE_BLOCKS[zone] ?? ZONE_BLOCKS.rest;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-[0.1em]",
        className
      )}
      style={{ backgroundColor: z.bg, color: z.fg }}
    >
      {z.label}
    </span>
  );
}
