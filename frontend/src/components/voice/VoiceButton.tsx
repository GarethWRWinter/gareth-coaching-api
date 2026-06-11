"use client";

import { Mic, MicOff, Volume2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  /** Whether the mic is actively listening */
  isListening: boolean;
  /** Whether TTS audio is currently playing */
  isSpeaking: boolean;
  /** Whether the browser supports Web Speech API */
  isSupported: boolean;
  /** Whether voice processing is in progress */
  isProcessing?: boolean;
  /** Toggle listening on/off */
  onToggle: () => void;
  className?: string;
}

export function VoiceButton({
  isListening,
  isSpeaking,
  isSupported,
  isProcessing,
  onToggle,
  className,
}: VoiceButtonProps) {
  if (!isSupported) return null;

  // Allow interruption when coach is speaking, only disable during pure processing (no audio yet)
  const disabled = isProcessing && !isListening && !isSpeaking;

  return (
    <button
      onClick={onToggle}
      disabled={disabled}
      title={
        isListening
          ? "Stop listening"
          : isSpeaking
            ? "Interrupt coach"
            : "Voice input"
      }
      className={cn(
        "flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-sm text-white transition-all",
        isListening
          ? "bg-vb-forest pulse-ring hover:bg-vb-forest-soft"
          : isSpeaking
            ? "bg-vb-forest hover:bg-vb-forest-soft"
            : "bg-vb-sunken text-vb-text hover:bg-vb-surface-raised",
        disabled && "cursor-not-allowed opacity-50",
        className
      )}
    >
      {isListening ? (
        <MicOff className="h-4 w-4" />
      ) : isSpeaking ? (
        <Volume2 className="h-4 w-4 animate-pulse" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
    </button>
  );
}
