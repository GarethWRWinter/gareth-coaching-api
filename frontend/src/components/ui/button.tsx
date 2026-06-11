import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// ALMANAC buttons — forest primary, matte, soft radius, calm transitions.
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-sm text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vb-forest focus-visible:ring-offset-2 focus-visible:ring-offset-vb-bg disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-vb-forest text-white hover:bg-vb-forest-soft",
        secondary: "bg-vb-sunken text-vb-text hover:bg-vb-border",
        destructive: "bg-vb-clay text-white hover:opacity-90",
        outline:
          "border border-vb-border bg-transparent text-vb-forest hover:bg-vb-sage-tint",
        ghost: "bg-transparent text-vb-text-dim hover:bg-vb-surface hover:text-vb-text",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        default: "h-10 px-4 py-2",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
