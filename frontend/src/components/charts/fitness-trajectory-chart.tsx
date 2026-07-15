"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { FitnessTrajectoryPoint } from "@/lib/api";

interface FitnessTrajectoryChartProps {
  trajectory: FitnessTrajectoryPoint[];
  className?: string;
}

function formatShortDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: FitnessTrajectoryPoint }>;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;

  return (
    <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-3 py-2">
      <p className="text-xs font-medium text-vb-text-dim">
        {formatShortDate(point.date)}
        {point.label && (
          <span className="ml-1.5 text-vb-forest">{point.label}</span>
        )}
      </p>
      <div className="mt-1.5 grid grid-cols-2 gap-x-4 gap-y-0.5">
        <p className="text-xs text-vb-text-dim">
          Fitness:{" "}
          <span className="font-mono font-medium text-vb-forest">
            {point.ctl.toFixed(0)}
          </span>
        </p>
        <p className="text-xs text-vb-text-dim">
          FTP:{" "}
          <span className="font-mono font-medium text-vb-clay">
            {point.ftp}W
          </span>
        </p>
      </div>
    </div>
  );
}

export function FitnessTrajectoryChart({
  trajectory,
  className,
}: FitnessTrajectoryChartProps) {
  if (!trajectory || trajectory.length < 2) return null;

  // Find labelled milestone points for reference lines
  const milestones = trajectory.filter((p) => p.label);

  // Calculate domains with padding
  const ctlValues = trajectory.map((p) => p.ctl);
  const minCtl = Math.floor(Math.min(...ctlValues) * 0.9);
  const maxCtl = Math.ceil(Math.max(...ctlValues) * 1.05);

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart
          data={trajectory}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <defs>
            <linearGradient id="ctlGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0B0B0C" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#0B0B0C" stopOpacity={0.02} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#ECEBE6"
            vertical={false}
          />

          <XAxis
            dataKey="date"
            tickFormatter={formatShortDate}
            tick={{ fontSize: 10, fill: "#9A9A94" }}
            tickLine={{ stroke: "#D8D8D2" }}
            axisLine={{ stroke: "#D8D8D2" }}
            interval="preserveStartEnd"
            minTickGap={40}
          />

          <YAxis
            domain={[minCtl, maxCtl]}
            tick={{ fontSize: 10, fill: "#9A9A94" }}
            tickLine={{ stroke: "#D8D8D2" }}
            axisLine={{ stroke: "#D8D8D2" }}
            width={35}
            tickFormatter={(v: number) => v.toFixed(0)}
          />

          {/* Milestone reference lines */}
          {milestones.map((m) => (
            <ReferenceLine
              key={m.date}
              x={m.date}
              stroke={m.label === "Race Day" ? "#FF3D00" : "#D8D8D2"}
              strokeDasharray={m.label === "Race Day" ? "0" : "4 4"}
              strokeWidth={m.label === "Race Day" ? 1.5 : 1}
              label={
                m.label
                  ? {
                      value: m.label,
                      position: "top",
                      fill: m.label === "Race Day" ? "#FF3D00" : "#9A9A94",
                      fontSize: 10,
                      fontWeight: m.label === "Race Day" ? 600 : 400,
                    }
                  : undefined
              }
            />
          ))}

          <Area
            type="monotone"
            dataKey="ctl"
            stroke="#0B0B0C"
            strokeWidth={2}
            fill="url(#ctlGradient)"
            dot={false}
            activeDot={{
              r: 4,
              fill: "#0B0B0C",
              stroke: "#FAFAF7",
              strokeWidth: 2,
            }}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "#9A9A94", strokeDasharray: "4 4" }} />
        </AreaChart>
      </ResponsiveContainer>

      {/* FTP milestones */}
      {trajectory.length >= 2 && (
        <div className="mt-2 flex items-center justify-between px-1">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-vb-forest" />
            <span className="text-[10px] text-vb-text-muted">
              CTL {trajectory[0].ctl.toFixed(0)} &rarr;{" "}
              {trajectory[trajectory.length - 1].ctl.toFixed(0)}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-vb-clay" />
            <span className="text-[10px] text-vb-text-muted">
              FTP {trajectory[0].ftp}W &rarr;{" "}
              {trajectory[trajectory.length - 1].ftp}W
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
