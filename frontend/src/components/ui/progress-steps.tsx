import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * FORMA stepper — editorial numbers, not dots.
 * Done steps are ink, the current step burns flamme, the rest wait.
 */
export function ProgressSteps({
  total,
  current,
  className,
}: {
  total: number;
  current: number; // 0-indexed
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {Array.from({ length: total }).map((_, i) => (
        <React.Fragment key={i}>
          <span
            className={cn(
              "f-data text-xs font-semibold",
              i < current && "text-vb-text",
              i === current && "text-vb-red",
              i > current && "text-vb-text-muted"
            )}
          >
            {String(i + 1).padStart(2, "0")}
          </span>
          {i < total - 1 && (
            <span
              aria-hidden="true"
              className={cn(
                "h-px flex-1 min-w-4",
                i < current ? "bg-vb-text" : "bg-vb-border"
              )}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
