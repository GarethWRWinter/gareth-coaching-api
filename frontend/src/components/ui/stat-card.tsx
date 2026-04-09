import * as React from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down";
}

const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ className, label, value, unit, trend, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-lg border border-slate-700 bg-slate-800 p-4 shadow-sm",
          className
        )}
        {...props}
      >
        <p className="text-sm font-medium text-slate-400">{label}</p>
        <div className="mt-1 flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white">{value}</span>
          {unit && <span className="text-sm text-slate-400">{unit}</span>}
          {trend && (
            <span
              className={cn(
                "ml-auto flex items-center text-sm font-medium",
                trend === "up" ? "text-green-400" : "text-red-400"
              )}
            >
              {trend === "up" ? (
                <TrendingUp className="h-4 w-4" />
              ) : (
                <TrendingDown className="h-4 w-4" />
              )}
            </span>
          )}
        </div>
      </div>
    );
  }
);
StatCard.displayName = "StatCard";

export { StatCard };
