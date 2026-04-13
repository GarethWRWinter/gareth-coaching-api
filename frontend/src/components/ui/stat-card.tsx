"use client";

import * as React from "react";
import { TrendingUp, TrendingDown, Bot, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { coachInsights } from "@/lib/api";

interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down";
  /** Pass a metric name to enable tap-to-explain (e.g. "CTL", "TSS", "NP") */
  explainable?: string;
}

const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ className, label, value, unit, trend, explainable, ...props }, ref) => {
    const [showExplain, setShowExplain] = React.useState(false);
    const [explanation, setExplanation] = React.useState<string | null>(null);
    const [loading, setLoading] = React.useState(false);

    const handleTap = async () => {
      if (!explainable || value === "-") return;
      if (showExplain) {
        setShowExplain(false);
        return;
      }
      setShowExplain(true);
      if (!explanation) {
        setLoading(true);
        try {
          const result = await coachInsights.explainMetric(explainable, value);
          setExplanation(result.explanation);
        } catch {
          setExplanation("Couldn't load explanation right now. Try again later.");
        } finally {
          setLoading(false);
        }
      }
    };

    return (
      <div className="relative">
        <div
          ref={ref}
          className={cn(
            "rounded-lg border border-slate-700 bg-slate-800 p-4 shadow-sm",
            explainable && value !== "-" && "cursor-pointer hover:border-blue-600/50 transition-colors",
            showExplain && "border-blue-600/50",
            className
          )}
          onClick={handleTap}
          role={explainable ? "button" : undefined}
          tabIndex={explainable ? 0 : undefined}
          {...props}
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-slate-400">{label}</p>
            {explainable && value !== "-" && (
              <Bot className="h-3.5 w-3.5 text-slate-600" />
            )}
          </div>
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
        {showExplain && (
          <div className="absolute left-0 right-0 top-full z-20 mt-1 rounded-lg border border-blue-500/30 bg-slate-900 p-3 shadow-xl">
            <div className="mb-1.5 flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Bot className="h-3.5 w-3.5 text-blue-400" />
                <span className="text-xs font-semibold text-blue-400">Coach Marco</span>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); setShowExplain(false); }}
                className="text-slate-500 hover:text-slate-300"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            {loading ? (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <div className="h-3 w-3 animate-spin rounded-full border border-blue-500 border-t-transparent" />
                Thinking...
              </div>
            ) : (
              <p className="text-xs leading-relaxed text-slate-300">{explanation}</p>
            )}
          </div>
        )}
      </div>
    );
  }
);
StatCard.displayName = "StatCard";

export { StatCard };
