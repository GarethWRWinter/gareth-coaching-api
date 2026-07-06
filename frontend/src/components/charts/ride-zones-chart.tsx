"use client";

import { ZONES, SERIES } from "@/lib/palette";

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

function zoneRampColor(zoneNum: number): string {
  const key = `z${zoneNum}` as keyof typeof ZONES;
  return ZONES[key] ?? SERIES.grey;
}

export function RideZonesChart({ zones, totalSeconds }: RideZonesChartProps) {
  const maxPct = Math.max(...zones.map((z) => z.percentage), 1);

  return (
    <div className="space-y-2">
      {zones.map((zone) => {
        const zoneNum = parseInt(zone.zone.replace("Z", ""));
        const color = zoneRampColor(zoneNum);
        const widthPct = (zone.percentage / maxPct) * 100;

        return (
          <div key={zone.zone} className="flex items-center gap-3">
            <div className="w-8 text-right font-mono text-[11px] font-semibold text-vb-text-dim">
              {zone.zone}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="h-6 flex-1 overflow-hidden rounded-sm bg-vb-sunken">
                  <div
                    className="h-full transition-all duration-500"
                    style={{
                      width: `${Math.max(widthPct, 1)}%`,
                      backgroundColor: color,
                      opacity: zone.percentage > 0 ? 1 : 0.3,
                    }}
                  />
                </div>
                <div className="w-24 text-right">
                  <span className="f-data text-xs font-medium text-vb-text">
                    {zone.percentage.toFixed(1)}%
                  </span>
                  <span className="f-data ml-1 text-xs text-vb-text-muted">
                    {formatTime(zone.seconds)}
                  </span>
                </div>
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-vb-text-muted">
                {zone.zone_name} · {zone.low_watts}-{zone.high_watts}W
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
