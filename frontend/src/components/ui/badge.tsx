import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// FORMA badge — a mono chip. Square corners, hairline or filled.
const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-sm px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-[0.12em]",
  {
    variants: {
      variant: {
        ink: "bg-vb-text text-white",
        flamme: "bg-vb-red text-white",
        outline: "border border-vb-border text-vb-text-dim",
        chalk: "bg-vb-sunken text-vb-text-dim",
      },
    },
    defaultVariants: { variant: "outline" },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
