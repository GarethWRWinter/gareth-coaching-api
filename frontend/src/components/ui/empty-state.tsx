import * as React from "react";
import { cn } from "@/lib/utils";
import { CoachGlyph } from "@/components/ui/coach-glyph";
import { Kicker } from "@/components/ui/kicker";

/**
 * FORMA empty state — never "No data". Forma turns every empty
 * surface into an invitation: glyph, one line in the coach's voice,
 * one action.
 */
export function EmptyState({
  kicker,
  title,
  children,
  action,
  className,
}: {
  kicker?: string;
  title: React.ReactNode;
  children?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "f-rise flex flex-col items-center border border-vb-border-subtle bg-vb-surface px-6 py-14 text-center",
        className
      )}
    >
      <CoachGlyph className="h-12 w-12" />
      {kicker && <Kicker className="mt-5">{kicker}</Kicker>}
      <h3 className="f-display mt-2 text-2xl text-vb-text">{title}</h3>
      {children && (
        <div className="mt-3 max-w-md text-sm leading-relaxed text-vb-text-dim">
          {children}
        </div>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
