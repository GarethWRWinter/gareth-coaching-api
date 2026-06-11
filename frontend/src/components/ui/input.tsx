import * as React from "react";
import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text placeholder:text-vb-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vb-forest focus-visible:ring-offset-2 focus-visible:ring-offset-vb-bg disabled:cursor-not-allowed disabled:opacity-50",
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
