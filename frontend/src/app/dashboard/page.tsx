"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Minus,
  Bike,
  Target,
  Calendar,
  ClipboardCheck,
} from "lucide-react";
import Link from "next/link";
import { metrics, rides, training, goals as goalsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDuration, formatDate, daysUntil } from "@/lib/utils";
import { StatCard } from "@/components/ui/stat-card";
import { RiderProfileRadar } from "@/components/charts/rider-profile-radar";

export default function DashboardPage() {
  const { user } = useAuth();

  // Fast query for CTL/ATL/TSB (skips expensive power profile scan)
  const { data: fitnessQuick } = useQuery({
    queryKey: ["fitness-summary-quick"],
    queryFn: () => metrics.getFitnessSummary(false),
  });

  // Full query with power profile for rider radar (loads in background)
  const { data: fitnessFull } = useQuery({
    queryKey: ["fitness-summary"],
    queryFn: () => metrics.getFitnessSummary(true),
    staleTime: 5 * 60 * 1000, // cache for 5 min
  });

  // Use full data when available, fall back to quick
  const fitness = fitnessFull ?? fitnessQuick;

  const { data: recentRides } = useQuery({
    queryKey: ["recent-rides"],
    queryFn: () => rides.list(1, 5),
  });

  const { data: plans } = useQuery({
    queryKey: ["plans"],
    queryFn: () => training.getPlans(),
  });

  const { data: goalsData } = useQuery({
    queryKey: ["goals"],
    queryFn: () => goalsApi.list(),
  });

  const tsbColor =
    (fitness?.current_tsb ?? 0) > 10
      ? "text-green-400"
      : (fitness?.current_tsb ?? 0) < -20
        ? "text-red-400"
        : "text-yellow-400";

  const tsbLabel =
    (fitness?.current_tsb ?? 0) > 10
      ? "Fresh"
      : (fitness?.current_tsb ?? 0) < -20
        ? "Fatigued"
        : "Neutral";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Welcome back, {user?.full_name?.split(" ")[0] || "Rider"}
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Here&apos;s your training overview
        </p>
      </div>

      {/* Fitness Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Fitness (CTL)"
          value={Math.round(fitness?.current_ctl ?? 0)}
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
        />
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Form (TSB)
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-2xl font-bold ${tsbColor}`}>
              {Math.round(fitness?.current_tsb ?? 0)}
            </span>
            <span className={`text-sm ${tsbColor}`}>{tsbLabel}</span>
          </div>
        </div>
        <StatCard
          label="FTP"
          value={user?.ftp ?? "-"}
          unit="W"
        />
      </div>

      {/* Rider Profile with Radar Chart */}
      {fitness && fitness.rider_type !== "unknown" && fitness.profile_scores && fitness.profile_scores.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-lg font-semibold text-white">Rider Profile</h2>
              <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs font-semibold text-amber-400 capitalize">
                {fitness.rider_type.replace("_", " ")}
              </span>
              {fitness.w_per_kg && (
                <span className="text-sm text-slate-400">
                  {fitness.w_per_kg.toFixed(2)} W/kg
                </span>
              )}
            </div>
            <Link
              href="/dashboard/performance"
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Full performance &rarr;
            </Link>
          </div>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:gap-6">
            <div className="w-[200px] shrink-0 sm:w-[240px]">
              <RiderProfileRadar
                scores={fitness.profile_scores}
                riderType={fitness.rider_type ?? "unknown"}
                strengths={fitness.strengths}
                weaknesses={fitness.weaknesses}
                compact
              />
            </div>
            <div className="flex flex-1 flex-wrap justify-center gap-1.5 sm:justify-start">
              {fitness.strengths.map((s) => (
                <span
                  key={s}
                  className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-medium text-emerald-400"
                >
                  {s}
                </span>
              ))}
              {fitness.weaknesses.map((w) => (
                <span
                  key={w}
                  className="rounded-full bg-orange-500/15 px-2.5 py-0.5 text-xs font-medium text-orange-400"
                >
                  {w}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Goals Needing Assessment */}
      {goalsData?.goals.filter((g) => g.needs_assessment).map((goal) => (
        <Link
          key={goal.id}
          href={`/dashboard/goals/${goal.id}/assess`}
          className="flex items-center gap-4 rounded-xl border border-amber-500/30 bg-amber-900/10 p-4 transition-colors hover:border-amber-500/50"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-500/20">
            <ClipboardCheck className="h-5 w-5 text-amber-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">
              You completed {goal.event_name}!
            </p>
            <p className="text-xs text-amber-400/70">
              Tell us how it went — complete your race report
            </p>
          </div>
          <span className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-medium text-white">
            Race Report
          </span>
        </Link>
      ))}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Rides */}
        <div className="rounded-xl border border-slate-800 bg-slate-800/50">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
            <h2 className="font-semibold text-white">Recent Rides</h2>
            <Link
              href="/dashboard/rides"
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              View all
            </Link>
          </div>
          <div className="divide-y divide-slate-800">
            {recentRides?.rides.length === 0 && (
              <div className="px-5 py-8 text-center text-sm text-slate-500">
                No rides yet.{" "}
                <Link
                  href="/dashboard/rides"
                  className="text-blue-400 hover:text-blue-300"
                >
                  Upload your first FIT file
                </Link>
              </div>
            )}
            {recentRides?.rides.map((ride) => (
              <Link
                key={ride.id}
                href={`/dashboard/rides/${ride.id}`}
                className="flex items-center justify-between px-5 py-3 hover:bg-slate-800/50"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-white">
                    {ride.title}
                  </p>
                  <p className="text-xs text-slate-400">
                    {formatDate(ride.ride_date)}
                    {ride.duration_seconds &&
                      ` \u00B7 ${formatDuration(ride.duration_seconds)}`}
                  </p>
                </div>
                <div className="flex items-center gap-4 text-right">
                  {ride.tss != null && (
                    <div>
                      <p className="text-sm font-medium text-white">
                        {Math.round(ride.tss)}
                      </p>
                      <p className="text-xs text-slate-500">TSS</p>
                    </div>
                  )}
                  {ride.normalized_power != null && (
                    <div>
                      <p className="text-sm font-medium text-white">
                        {Math.round(ride.normalized_power)}W
                      </p>
                      <p className="text-xs text-slate-500">NP</p>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Goals & Plan */}
        <div className="space-y-6">
          {/* Upcoming Goals */}
          <div className="rounded-xl border border-slate-800 bg-slate-800/50">
            <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
              <h2 className="font-semibold text-white">Active Goals</h2>
              <Link
                href="/dashboard/goals"
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                View all
              </Link>
            </div>
            <div className="divide-y divide-slate-800">
              {(!goalsData || goalsData.goals.filter((g) => g.status === "upcoming").length === 0) && (
                <div className="px-5 py-6 text-center text-sm text-slate-500">
                  No upcoming goals
                </div>
              )}
              {goalsData?.goals.filter((g) => g.status === "upcoming").slice(0, 3).map((goal) => (
                <div key={goal.id} className="flex items-center gap-3 px-5 py-3">
                  <Target className="h-4 w-4 shrink-0 text-blue-400" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-white">
                      {goal.event_name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {formatDate(goal.event_date)} &middot;{" "}
                      <span className="capitalize">
                        {goal.priority.replace("_", " ")}
                      </span>
                    </p>
                  </div>
                  {goal.days_until != null && goal.days_until > 0 && (
                    <span className="rounded-full bg-blue-600/10 px-2.5 py-0.5 text-xs font-medium text-blue-400">
                      {goal.days_until}d
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Active Plan */}
          {plans && plans.plans.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-blue-400" />
                <h2 className="font-semibold text-white">Active Plan</h2>
              </div>
              {plans.plans
                .filter((p) => p.status === "active")
                .slice(0, 1)
                .map((plan) => (
                  <div key={plan.id} className="mt-3">
                    <p className="text-sm text-white">{plan.name}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      {formatDate(plan.start_date)} &ndash;{" "}
                      {formatDate(plan.end_date)} &middot; {plan.total_weeks}{" "}
                      weeks &middot; {plan.phase_count} phases
                    </p>
                    <Link
                      href="/dashboard/training"
                      className="mt-3 inline-block text-xs text-blue-400 hover:text-blue-300"
                    >
                      View training calendar &rarr;
                    </Link>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
