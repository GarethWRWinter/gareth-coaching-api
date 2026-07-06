import * as React from "react";
import { cn } from "@/lib/utils";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

// FORMA input — sharp, hairline, flamme focus.
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text placeholder:text-vb-text-muted focus-visible:border-vb-red focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-vb-red disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
