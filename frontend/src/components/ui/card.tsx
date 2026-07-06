import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * FORMA card — flat paper, hairline border, no shadow.
 * `rail` adds the 3px flamme left rail: the mark of Forma speaking.
 * `lift` adds hover lift for clickable cards.
 */
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  rail?: boolean;
  lift?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, rail, lift, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-sm border border-vb-border-subtle bg-vb-surface text-vb-text",
        rail && "border-l-[3px] border-l-vb-red",
        lift && "f-lift cursor-pointer",
        className
      )}
      {...props}
    />
  )
);
Card.displayName = "Card";

const CardBody = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-5", className)} {...props} />
));
CardBody.displayName = "CardBody";

export { Card, CardBody };
