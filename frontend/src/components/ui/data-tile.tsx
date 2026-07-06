"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { useCountUp } from "@/hooks/useCountUp";

/**
 * FORMA data tile — the number is the design.
 * Huge Plex Mono value with count-up, kicker label, optional unit,
 * optional sub-line and delta. `hot` inverts to flamme (one per row, max).
 */
export function DataTile({
  label,
  value,
  unit,
  sub,
  delta,
  hot,
  decimals = 0,
  className,
}: {
  label: string;
  value: number;
  unit?: string;
  sub?: string;
  /** signed number; renders ▲/▼ coloured by direction */
  delta?: number;
  hot?: boolean;
  decimals?: number;
  className?: string;
}) {
  const v = useCountUp(value);
  return (
    <div
      className={cn(
        "border border-vb-border-subtle p-4",
        hot ? "border-vb-red bg-vb-red text-white" : "bg-vb-surface",
        className
      )}
    >
      <p
        className={cn(
          "f-kicker",
          hot ? "text-white/80" : "text-vb-text-muted"
        )}
      >
        {label}
      </p>
      <p className="f-data mt-2 text-4xl font-semibold leading-none">
        {v.toFixed(decimals)}
        {unit && (
          <span
            className={cn(
              "ml-1 text-base font-medium",
              hot ? "text-white/70" : "text-vb-text-muted"
            )}
          >
            {unit}
          </span>
        )}
      </p>
      {(sub || delta !== undefined) && (
        <p
          className={cn(
            "mt-2 text-xs",
            hot ? "text-white/80" : "text-vb-text-dim"
          )}
        >
          {delta !== undefined && delta !== 0 && (
            <span
              className={cn(
                "f-data mr-1.5 font-semibold",
                hot
                  ? "text-white"
                  : delta > 0
                    ? "text-vb-success"
                    : "text-vb-red"
              )}
            >
              {delta > 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(decimals)}
            </span>
          )}
          {sub}
        </p>
      )}
    </div>
  );
}
