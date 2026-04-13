"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { metrics } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { StatCard } from "@/components/ui/stat-card";
import { PMCChart } from "@/components/charts/pmc-chart";
import { PowerCurveChart } from "@/components/charts/power-curve-chart";
import { ZoneDistribution } from "@/components/charts/zone-distribution";
import { WeeklyLoadChart } from "@/components/charts/weekly-load-chart";
import { FTPHistoryChart } from "@/components/charts/ftp-history-chart";
import { PersonalBestsGrid } from "@/components/charts/personal-bests-grid";
import { RiderProfileRadar } from "@/components/charts/rider-profile-radar";

type DateRange = "1m" | "3m" | "6m" | "1y" | "all";

const DATE_RANGE_OPTIONS: { value: DateRange; label: string }[] = [
  { value: "1m", label: "1 Month" },
  { value: "3m", label: "3 Months" },
  { value: "6m", label: "6 Months" },
  { value: "1y", label: "1 Year" },
  { value: "all", label: "All Time" },
];

function getDateRangeCutoff(range: DateRange): Date | null {
  if (range === "all") return null;
  const now = new Date();
  switch (range) {
    case "1m":
      now.setMonth(now.getMonth() - 1);
      break;
    case "3m":
      now.setMonth(now.getMonth() - 3);
      break;
    case "6m":
      now.setMonth(now.getMonth() - 6);
      break;
    case "1y":
      now.setFullYear(now.getFullYear() - 1);
      break;
  }
  return now;
}

function getWeeklyLoadWeeks(range: DateRange): number {
  switch (range) {
    case "1m":
      return 5;
    case "3m":
      return 13;
    case "6m":
      return 26;
    case "1y":
      return 52;
    case "all":
      return 520;
  }
}

export default function PerformancePage() {
  const { user } = useAuth();
  const [dateRange, setDateRange] = useState<DateRange>("3m");

  const { data: pmc, isLoading: pmcLoading } = useQuery({
    queryKey: ["pmc"],
    queryFn: () => metrics.getPMC(),
  });

  const { data: fitnessQuick } = useQuery({
    queryKey: ["fitness-summary-quick"],
    queryFn: () => metrics.getFitnessSummary(false),
  });

  const { data: fitnessFull } = useQuery({
    queryKey: ["fitness-summary"],
    queryFn: () => metrics.getFitnessSummary(true),
    staleTime: 5 * 60 * 1000,
  });

  const fitness = fitnessFull ?? fitnessQuick;

  const { data: zones } = useQuery({
    queryKey: ["zones"],
    queryFn: () => metrics.getZones(),
  });

  const { data: powerProfile } = useQuery({
    queryKey: ["power-profile"],
    queryFn: () => metrics.getPowerProfile(),
  });

  const weeksToFetch = getWeeklyLoadWeeks(dateRange);
  const { data: weeklyLoad } = useQuery({
    queryKey: ["weekly-load", weeksToFetch],
    queryFn: () => metrics.getWeeklyLoad(weeksToFetch),
  });

  const { data: ftpHistory } = useQuery({
    queryKey: ["ftp-history"],
    queryFn: () => metrics.getFTPHistory(),
  });

  // Filter PMC data based on selected date range
  const filteredPMC = useMemo(() => {
    if (!pmc?.data) return [];
    const cutoff = getDateRangeCutoff(dateRange);
    if (!cutoff) return pmc.data;
    return pmc.data.filter((d) => new Date(d.date) >= cutoff);
  }, [pmc, dateRange]);

  const tsbColor =
    (fitness?.current_tsb ?? 0) > 10
      ? "text-green-400"
      : (fitness?.current_tsb ?? 0) < -20
        ? "text-red-400"
        : "text-yellow-400";

  // Calculate weekly load trend
  const weeklyTrend =
    weeklyLoad && weeklyLoad.weeks.length >= 2
      ? (() => {
          const recent = weeklyLoad.weeks.slice(-2);
          const diff = recent[1].total_tss - recent[0].total_tss;
          return diff > 20 ? "up" : diff < -20 ? "down" : undefined;
        })()
      : undefined;

  const currentWeekTSS =
    weeklyLoad?.weeks.length
      ? Math.round(weeklyLoad.weeks[weeklyLoad.weeks.length - 1].total_tss)
      : 0;

  const currentWeekRides =
    weeklyLoad?.weeks.length
      ? weeklyLoad.weeks[weeklyLoad.weeks.length - 1].ride_count
      : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Performance</h1>
        <p className="mt-1 text-sm text-slate-400">
          Track your fitness trends and training load
        </p>
      </div>

      {/* Fitness Stats Row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard
          label="FTP"
          value={user?.ftp ?? "-"}
          unit="W"
          explainable="FTP"
        />
        <StatCard
          label="Fitness (CTL)"
          value={Math.round(fitness?.current_ctl ?? 0)}
          explainable="CTL"
          trend={
            (fitness?.ramp_rate ?? 0) > 0
              ? "up"
              : (fitness?.ramp_rate ?? 0) < 0
                ? "down"
                : undefined
          }
        />
        <StatCard
          label="Fatigue (ATL)"
          value={Math.round(fitness?.current_atl ?? 0)}
          explainable="ATL"
        />
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Form (TSB)
          </p>
          <p className={`mt-2 text-2xl font-bold ${tsbColor}`}>
            {Math.round(fitness?.current_tsb ?? 0)}
          </p>
        </div>
        <StatCard
          label="This Week"
          value={currentWeekTSS}
          unit={`TSS · ${currentWeekRides} rides`}
          trend={weeklyTrend as "up" | "down" | undefined}
          explainable="Weekly TSS"
        />
      </div>

      {/* Date Range Selector */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-medium text-slate-400">Range:</span>
        <div className="flex flex-wrap gap-1 rounded-lg bg-slate-800 p-1">
          {DATE_RANGE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setDateRange(option.value)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                dateRange === option.value
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-400 hover:bg-slate-700 hover:text-slate-200"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* PMC Chart */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Performance Management Chart
        </h2>
        {pmcLoading ? (
          <div className="flex h-80 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          </div>
        ) : filteredPMC.length > 0 ? (
          <div className="h-80">
            <PMCChart data={filteredPMC} dateRange={dateRange} />
          </div>
        ) : (
          <div className="flex h-80 items-center justify-center text-sm text-slate-500">
            No PMC data yet. Upload rides with power data to see your chart.
          </div>
        )}
      </div>

      {/* Weekly Training Load */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Weekly Training Load
        </h2>
        {weeklyLoad && weeklyLoad.weeks.length > 0 ? (
          <WeeklyLoadChart data={weeklyLoad.weeks} />
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            No weekly data yet
          </div>
        )}
      </div>

      {/* Personal Bests Grid */}
      {powerProfile && powerProfile.points.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <PersonalBestsGrid points={powerProfile.points} days={powerProfile.days} />
        </div>
      )}

      {/* Power Curve + Rider Profile Radar (2 columns) */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Power Duration Curve */}
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Power Duration Curve
          </h2>
          {powerProfile && powerProfile.points.some((p) => p.best_power > 0) ? (
            <div className="h-72">
              <PowerCurveChart data={powerProfile.points} days={powerProfile.days} />
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-slate-500">
              No power data yet
            </div>
          )}
        </div>

        {/* Rider Profile Radar */}
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Rider Profile
          </h2>
          {fitness && fitness.profile_scores && fitness.profile_scores.length > 0 ? (
            <RiderProfileRadar
              scores={fitness.profile_scores}
              riderType={fitness.rider_type}
              strengths={fitness.strengths}
              weaknesses={fitness.weaknesses}
            />
          ) : (
            <div className="flex h-64 items-center justify-center text-sm text-slate-500">
              Complete rides with power data to see your profile
            </div>
          )}
        </div>
      </div>

      {/* Power Zones */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Power Zones
        </h2>
        {zones?.power_zones ? (
          <ZoneDistribution zones={zones.power_zones} />
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            Set your FTP in settings to see zones
          </div>
        )}
      </div>

      {/* FTP History */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          FTP History
        </h2>
        {ftpHistory && ftpHistory.history.length > 0 ? (
          <FTPHistoryChart
            data={ftpHistory.history}
            currentFTP={ftpHistory.current_ftp}
          />
        ) : (
          <div className="flex h-48 items-center justify-center text-sm text-slate-500">
            No FTP history yet
          </div>
        )}
      </div>

      {/* Fitness Details (ramp rate, fitness level) */}
      {fitness && fitness.rider_type !== "unknown" && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-3 text-lg font-semibold text-white">
            Training Status
          </h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-xs font-medium uppercase text-slate-400">
                Fitness Level
              </p>
              <p className="mt-1 text-lg font-semibold capitalize text-white">
                {fitness.fitness_level.replace("_", " ")}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium uppercase text-slate-400">
                W/kg
              </p>
              <p className="mt-1 text-lg font-semibold text-white">
                {fitness.w_per_kg?.toFixed(2) ?? "-"}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium uppercase text-slate-400">
                Ramp Rate
              </p>
              <p className="mt-1 text-lg font-semibold text-white">
                {fitness.ramp_rate.toFixed(1)}{" "}
                <span className="text-sm text-slate-400">TSS/day/wk</span>
              </p>
              {fitness.ramp_rate > 7 && (
                <p className="mt-0.5 text-xs text-orange-400">
                  High ramp rate - monitor recovery
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
