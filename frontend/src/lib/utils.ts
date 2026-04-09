import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatPower(watts: number | null | undefined): string {
  if (watts == null) return "-";
  return `${Math.round(watts)}W`;
}

export function formatTSS(tss: number | null | undefined): string {
  if (tss == null) return "-";
  return Math.round(tss).toString();
}

export function daysUntil(dateStr: string): number {
  const target = new Date(dateStr);
  const now = new Date();
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

export function zoneColor(zone: number): string {
  const colors: Record<number, string> = {
    1: "#94a3b8", // gray
    2: "#3b82f6", // blue
    3: "#22c55e", // green
    4: "#eab308", // yellow
    5: "#f97316", // orange
    6: "#ef4444", // red
    7: "#a855f7", // purple
  };
  return colors[zone] || "#6b7280";
}
