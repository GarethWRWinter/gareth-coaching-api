"use client";

import { cn } from "@/lib/utils";

interface VoiceIndicatorProps {
  /** Current voice mode state */
  mode: "idle" | "listening" | "processing" | "speaking";
  /** Real-time transcript while user is speaking */
  interimTranscript?: string;
  className?: string;
}

export function VoiceIndicator({
  mode,
  interimTranscript,
  className,
}: VoiceIndicatorProps) {
  if (mode === "idle") return null;

  return (
    <div
      className={cn(
        "mb-3 flex h-10 items-center gap-3 rounded-lg px-4 transition-all",
        mode === "listening" && "bg-red-500/10 border border-red-500/20",
        mode === "processing" && "bg-blue-500/10 border border-blue-500/20",
        mode === "speaking" && "bg-emerald-500/10 border border-emerald-500/20",
        className
      )}
    >
      {/* Waveform / Status icon */}
      <div className="flex items-center gap-0.5">
        {mode === "listening" && (
          <>
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="voice-bar w-1 rounded-full bg-red-400"
                style={{
                  animationDelay: `${i * 0.1}s`,
                  height: "4px",
                }}
              />
            ))}
          </>
        )}
        {mode === "processing" && (
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" />
        )}
        {mode === "speaking" && (
          <>
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="voice-bar w-1 rounded-full bg-emerald-400"
                style={{
                  animationDelay: `${i * 0.12}s`,
                  height: "4px",
                }}
              />
            ))}
          </>
        )}
      </div>

      {/* Status text */}
      <div className="min-w-0 flex-1">
        {mode === "listening" && (
          <p className="text-xs text-red-300">
            {interimTranscript ? (
              <span className="italic">{interimTranscript}</span>
            ) : (
              "Listening... speak now"
            )}
          </p>
        )}
        {mode === "processing" && (
          <p className="text-xs text-blue-300">Processing...</p>
        )}
        {mode === "speaking" && (
          <p className="text-xs text-emerald-300">Coach Marco is speaking...</p>
        )}
      </div>
    </div>
  );
}
