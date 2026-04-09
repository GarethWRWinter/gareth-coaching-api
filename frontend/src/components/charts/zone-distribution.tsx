"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
  LabelList,
} from "recharts";
import { cn } from "@/lib/utils";
import { zoneColor } from "@/lib/utils";

interface ZoneDistributionProps {
  zones: Record<string, { low: number; high: number }>;
  className?: string;
}

const ZONE_COLORS: Record<string, string> = {
  Z1: "#94a3b8", // gray
  Z2: "#3b82f6", // blue
  Z3: "#22c55e", // green
  Z4: "#eab308", // yellow
  Z5: "#f97316", // orange
  Z6: "#ef4444", // red
  Z7: "#a855f7", // purple
};

function getZoneBarColor(zoneName: string): string {
  // Try direct lookup first (e.g. "Z1", "Z2")
  if (ZONE_COLORS[zoneName]) return ZONE_COLORS[zoneName];

  // Try extracting the number from names like "Zone 1", "zone1"
  const match = zoneName.match(/(\d+)/);
  if (match) {
    const num = parseInt(match[1], 10);
    return zoneColor(num);
  }

  return "#6b7280";
}

interface ZoneBarData {
  zone: string;
  low: number;
  high: number;
  range: number;
  label: string;
  color: string;
}

function ZoneTooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ZoneBarData }>;
}) {
  if (!active || !payload?.length) return null;

  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 shadow-xl">
      <p className="mb-1 text-xs font-medium text-slate-300">{data.zone}</p>
      <p className="text-sm font-mono font-medium text-slate-100">
        {data.low} &ndash; {data.high === Infinity ? "max" : data.high}W
      </p>
    </div>
  );
}

export function ZoneDistribution({ zones, className }: ZoneDistributionProps) {
  const chartData: ZoneBarData[] = Object.entries(zones).map(
    ([zoneName, { low, high }]) => {
      const displayHigh = high === Infinity || high > 9999 ? low * 1.2 : high;
      return {
        zone: zoneName,
        low,
        high,
        range: displayHigh - low,
        label:
          high === Infinity || high > 9999
            ? `${low}W+`
            : `${low}-${high}W`,
        color: getZoneBarColor(zoneName),
      };
    }
  );

  // Find max watt value for domain
  const maxWatt = Math.max(
    ...chartData.map((d) =>
      d.high === Infinity || d.high > 9999 ? d.low * 1.2 : d.high
    )
  );

  return (
    <div className={cn("rounded-xl bg-slate-900 p-4", className)}>
      <h3 className="mb-4 text-sm font-semibold text-slate-200">
        Power Zones
      </h3>
      <ResponsiveContainer width="100%" height={chartData.length * 48 + 40}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 40, left: 10, bottom: 5 }}
          barCategoryGap="20%"
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#334155"
            horizontal={false}
          />
          <XAxis
            type="number"
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={{ stroke: "#475569" }}
            axisLine={{ stroke: "#475569" }}
            domain={[0, Math.ceil(maxWatt / 50) * 50]}
            tickFormatter={(v: number) => `${v}W`}
          />
          <YAxis
            type="category"
            dataKey="zone"
            stroke="#94a3b8"
            tick={{ fontSize: 12, fill: "#e2e8f0", fontWeight: 500 }}
            tickLine={false}
            axisLine={{ stroke: "#475569" }}
            width={40}
          />
          <Tooltip
            content={<ZoneTooltipContent />}
            cursor={{ fill: "#1e293b" }}
          />

          {/* Invisible base bar to offset from the low value */}
          <Bar
            dataKey="low"
            stackId="zone"
            fill="transparent"
            radius={0}
            isAnimationActive={false}
          />

          {/* Visible range bar stacked on top */}
          <Bar
            dataKey="range"
            stackId="zone"
            radius={[0, 4, 4, 0]}
          >
            <LabelList
              dataKey="label"
              position="right"
              fill="#94a3b8"
              fontSize={11}
            />
            {chartData.map((entry) => (
              <Cell key={entry.zone} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
