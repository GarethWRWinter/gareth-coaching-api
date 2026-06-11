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
  Z1: "#8AA3B0",
  Z2: "#9FB295",
  Z3: "#C7A458",
  Z4: "#D2855B",
  Z5: "#C06A48",
  Z6: "#A24E36",
  Z7: "#7E3A28",
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

  return "#948D80";
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
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2 shadow-[0_2px_8px_rgba(33,30,26,0.10)]">
      <p className="mb-1 text-xs font-medium text-vb-text-dim">{data.zone}</p>
      <p className="text-sm font-mono font-medium text-vb-text">
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
    <div className={cn("rounded-md border border-vb-border-subtle bg-vb-surface p-4", className)}>
      <h3 className="mb-4 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
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
            stroke="#E4DCCE"
            horizontal={false}
          />
          <XAxis
            type="number"
            stroke="#D6CFC1"
            tick={{ fontSize: 11, fill: "#948D80" }}
            tickLine={{ stroke: "#D6CFC1" }}
            axisLine={{ stroke: "#D6CFC1" }}
            domain={[0, Math.ceil(maxWatt / 50) * 50]}
            tickFormatter={(v: number) => `${v}W`}
          />
          <YAxis
            type="category"
            dataKey="zone"
            stroke="#D6CFC1"
            tick={{ fontSize: 12, fill: "#211E1A", fontWeight: 500 }}
            tickLine={false}
            axisLine={{ stroke: "#D6CFC1" }}
            width={40}
          />
          <Tooltip
            content={<ZoneTooltipContent />}
            cursor={{ fill: "#BCB3A3" }}
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
              fill="#948D80"
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
