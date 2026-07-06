import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// FORMA buttons — mono uppercase labels, sharp corners, press feedback.
// ink: the default action. flamme: the one hot action per screen.
// ghost: hairline outline. quiet: text-only. carbon: for ride mode.
const buttonVariants = cva(
  "f-press f-arrow inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-sm font-mono font-semibold uppercase tracking-[0.08em] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vb-red focus-visible:ring-offset-2 focus-visible:ring-offset-vb-bg disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        ink: "bg-vb-text text-white hover:bg-vb-red",
        flamme: "bg-vb-red text-white hover:bg-vb-red-dim",
        ghost:
          "border border-vb-border bg-transparent text-vb-text hover:border-vb-border-strong",
        quiet: "bg-transparent text-vb-text-dim hover:text-vb-red",
        carbon:
          "bg-vb-carbon-raised text-vb-chalk hover:bg-vb-red hover:text-white",
      },
      size: {
        sm: "h-8 px-3 text-[11px]",
        default: "h-11 px-5 text-xs",
        lg: "h-[52px] px-7 text-[13px]",
      },
    },
    defaultVariants: { variant: "ink", size: "default" },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
);
Button.displayName = "Button";

/** Sliding arrow for button/link labels: <Button>Start<Arrow /></Button> */
function Arrow({ className = "" }: { className?: string }) {
  return (
    <span aria-hidden="true" className={cn("f-arrow-head", className)}>
      →
    </span>
  );
}

export { Button, Arrow, buttonVariants };
