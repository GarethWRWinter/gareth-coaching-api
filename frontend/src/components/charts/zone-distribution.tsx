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
import { ZONES, SERIES } from "@/lib/palette";

const MONO = "IBM Plex Mono, ui-monospace, SFMono-Regular, monospace";
const TICK = { fontSize: 11, fill: SERIES.grey, fontFamily: MONO };

interface ZoneDistributionProps {
  zones: Record<string, { low: number; high: number }>;
  className?: string;
}

function getZoneBarColor(zoneName: string): string {
  // Extract the zone number from names like "Z1", "Zone 1", "zone1"
  const match = zoneName.match(/(\d+)/);
  if (match) {
    const key = `z${match[1]}` as keyof typeof ZONES;
    if (ZONES[key]) return ZONES[key];
  }
  return SERIES.grey;
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
    <div className="rounded-sm border border-vb-border bg-vb-surface px-3 py-2">
      <p className="f-kicker mb-1 text-vb-text-muted">{data.zone}</p>
      <p className="f-data text-sm font-medium text-vb-text">
        {data.low} to {data.high === Infinity ? "max" : data.high}W
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
    <div
      className={cn(
        "rounded-sm border border-vb-border-subtle bg-vb-surface p-4",
        className
      )}
    >
      <h3 className="f-kicker mb-4 text-vb-text-muted">
        Where the efforts live
      </h3>
      <ResponsiveContainer width="100%" height={chartData.length * 48 + 40}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 40, left: 10, bottom: 5 }}
          barCategoryGap="20%"
        >
          <CartesianGrid stroke={SERIES.hairline} horizontal={false} />
          <XAxis
            type="number"
            stroke={SERIES.hairline}
            tick={TICK}
            tickLine={{ stroke: SERIES.hairline }}
            axisLine={{ stroke: SERIES.hairline }}
            domain={[0, Math.ceil(maxWatt / 50) * 50]}
            tickFormatter={(v: number) => `${v}W`}
          />
          <YAxis
            type="category"
            dataKey="zone"
            stroke={SERIES.hairline}
            tick={{ fontSize: 11, fill: SERIES.ink, fontFamily: MONO, fontWeight: 600 }}
            tickLine={false}
            axisLine={{ stroke: SERIES.hairline }}
            width={40}
          />
          <Tooltip
            content={<ZoneTooltipContent />}
            cursor={{ fill: SERIES.chalk }}
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
            radius={[0, 0, 0, 0]}
          >
            <LabelList
              dataKey="label"
              position="right"
              fill={SERIES.grey}
              fontSize={10}
              fontFamily={MONO}
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
