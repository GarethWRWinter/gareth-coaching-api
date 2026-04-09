// Coggan 7-Zone Power Model — mirrors backend app/core/constants.py

export interface PowerZone {
  zone: number;
  name: string;
  low: number; // fraction of FTP
  high: number;
}

export const POWER_ZONES: PowerZone[] = [
  { zone: 1, name: "Active Recovery", low: 0, high: 0.55 },
  { zone: 2, name: "Endurance", low: 0.56, high: 0.75 },
  { zone: 3, name: "Tempo", low: 0.76, high: 0.9 },
  { zone: 4, name: "Threshold", low: 0.91, high: 1.05 },
  { zone: 5, name: "VO2max", low: 1.06, high: 1.2 },
  { zone: 6, name: "Anaerobic", low: 1.21, high: 1.5 },
  { zone: 7, name: "Neuromuscular", low: 1.51, high: 3.0 },
];

export function getZoneFromPct(pct: number): PowerZone {
  for (let i = POWER_ZONES.length - 1; i >= 0; i--) {
    if (pct >= POWER_ZONES[i].low) return POWER_ZONES[i];
  }
  return POWER_ZONES[0];
}

// Tailwind class maps per zone (dark theme)
export const ZONE_COLORS: Record<
  number,
  { bg: string; bgSolid: string; text: string; border: string; bar: string; hex: string }
> = {
  1: {
    bg: "bg-slate-500/20",
    bgSolid: "bg-slate-500",
    text: "text-slate-300",
    border: "border-slate-500/40",
    bar: "bg-slate-500",
    hex: "#94a3b8",
  },
  2: {
    bg: "bg-blue-500/20",
    bgSolid: "bg-blue-500",
    text: "text-blue-400",
    border: "border-blue-500/40",
    bar: "bg-blue-500",
    hex: "#3b82f6",
  },
  3: {
    bg: "bg-green-500/20",
    bgSolid: "bg-green-500",
    text: "text-green-400",
    border: "border-green-500/40",
    bar: "bg-green-500",
    hex: "#22c55e",
  },
  4: {
    bg: "bg-amber-500/20",
    bgSolid: "bg-amber-500",
    text: "text-amber-400",
    border: "border-amber-500/40",
    bar: "bg-amber-500",
    hex: "#f59e0b",
  },
  5: {
    bg: "bg-orange-500/20",
    bgSolid: "bg-orange-500",
    text: "text-orange-400",
    border: "border-orange-500/40",
    bar: "bg-orange-500",
    hex: "#f97316",
  },
  6: {
    bg: "bg-red-500/20",
    bgSolid: "bg-red-500",
    text: "text-red-400",
    border: "border-red-500/40",
    bar: "bg-red-500",
    hex: "#ef4444",
  },
  7: {
    bg: "bg-purple-500/20",
    bgSolid: "bg-purple-500",
    text: "text-purple-400",
    border: "border-purple-500/40",
    bar: "bg-purple-500",
    hex: "#a855f7",
  },
};

export function getZoneColors(pct: number) {
  const zone = getZoneFromPct(pct);
  return ZONE_COLORS[zone.zone] || ZONE_COLORS[1];
}
