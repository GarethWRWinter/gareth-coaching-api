"use client";

import { zoneColor } from "@/lib/utils";

interface ZoneData {
  zone: string;
  zone_name: string;
  low_watts: number;
  high_watts: number;
  seconds: number;
  percentage: number;
}

interface RideZonesChartProps {
  zones: ZoneData[];
  totalSeconds: number;
}

function formatTime(seconds: number) {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m < 60) return s > 0 ? `${m}m ${s}s` : `${m}m`;
  const h = Math.floor(m / 60);
  const rm = m % 60;
  return rm > 0 ? `${h}h ${rm}m` : `${h}h`;
}

export function RideZonesChart({ zones, totalSeconds }: RideZonesChartProps) {
  const maxPct = Math.max(...zones.map((z) => z.percentage), 1);

  return (
    <div className="space-y-2">
      {zones.map((zone) => {
        const zoneNum = parseInt(zone.zone.replace("Z", ""));
        const color = zoneColor(zoneNum);
        const widthPct = (zone.percentage / maxPct) * 100;

        return (
          <div key={zone.zone} className="flex items-center gap-3">
            <div className="w-8 text-right text-xs font-medium text-slate-400">
              {zone.zone}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-6 rounded bg-slate-700/50 overflow-hidden">
                  <div
                    className="h-full rounded transition-all duration-500"
                    style={{
                      width: `${Math.max(widthPct, 1)}%`,
                      backgroundColor: color,
                      opacity: zone.percentage > 0 ? 1 : 0.3,
                    }}
                  />
                </div>
                <div className="w-24 text-right">
                  <span className="text-xs text-white font-medium">
                    {zone.percentage.toFixed(1)}%
                  </span>
                  <span className="ml-1 text-xs text-slate-500">
                    {formatTime(zone.seconds)}
                  </span>
                </div>
              </div>
              <div className="mt-0.5 text-[10px] text-slate-500">
                {zone.zone_name} · {zone.low_watts}-{zone.high_watts}W
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
