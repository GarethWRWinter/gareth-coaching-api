import * as React from "react";
import { cn } from "@/lib/utils";
import { Kicker } from "@/components/ui/kicker";

/**
 * The canonical "Forma speaks" block — flamme rail, prose, and the
 * handwritten signature. Every debrief, note and nudge uses this so
 * the coach is recognisable at a glance on any surface.
 */
export function CoachNote({
  kicker = "A note from Forma",
  children,
  coachName = "Forma",
  signature = true,
  action,
  className,
}: {
  kicker?: string;
  children: React.ReactNode;
  coachName?: string;
  signature?: boolean;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "border border-vb-border-subtle border-l-[3px] border-l-vb-red bg-vb-surface p-5",
        className
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <Kicker flamme>{kicker}</Kicker>
        {action && <div className="shrink-0">{action}</div>}
      </div>
      <div className="mt-3 text-[15px] leading-relaxed text-vb-text">
        {children}
      </div>
      {signature && (
        <p className="mt-4">
          <span className="f-signature text-2xl leading-none">{coachName}</span>
          <span className="ml-2 text-xs text-vb-text-muted">your coach</span>
        </p>
      )}
    </div>
  );
}
