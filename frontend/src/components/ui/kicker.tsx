import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * FORMA kicker — the mono eyebrow above headings.
 * `dot` prefixes a small flamme disc (use for live / hot context).
 * `flamme` renders the whole kicker in flamme.
 */
export function Kicker({
  children,
  dot,
  flamme,
  className,
}: {
  children: React.ReactNode;
  dot?: boolean;
  flamme?: boolean;
  className?: string;
}) {
  return (
    <p
      className={cn(
        "f-kicker flex items-center gap-2",
        flamme ? "text-vb-red" : "text-vb-text-muted",
        className
      )}
    >
      {dot && (
        <span
          aria-hidden="true"
          className="inline-block h-1.5 w-1.5 rounded-full bg-vb-red"
        />
      )}
      {children}
    </p>
  );
}
