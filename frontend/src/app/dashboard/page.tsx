"use client";

import { useQuery } from "@tanstack/react-query";
import { ClipboardCheck } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { metrics, rides, training, goals as goalsApi, coachInsights } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDuration, formatDate } from "@/lib/utils";
import { RiderProfileRadar } from "@/components/charts/rider-profile-radar";

/**
 * VoiceBox-styled dashboard.
 *
 * Layout philosophy:
 *  - Top section is the masthead "Today" — overline rubric + huge display headline.
 *  - Marco's nudge lives as a pull-quote with a 4px red left border.
 *  - Fitness stats live as one continuous strip (no card gaps), 4 columns,
 *    Archivo Black numerals, single red accent on FTP.
 *  - Rides + Goals as editorial lists with rubrics over each title.
 */

export default function DashboardPage() {
  const { user } = useAuth();

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

  const { data: nudge } = useQuery({
    queryKey: ["coach-nudge"],
    queryFn: () => coachInsights.getNudge(),
    staleTime: 30 * 60 * 1000,
    retry: false,
  });

  const latestRide = recentRides?.rides?.[0];
  const { data: latestDebrief } = useQuery({
    queryKey: ["ride-debrief", latestRide?.id],
    queryFn: () => coachInsights.getRideDebrief(latestRide!.id),
    enabled: !!latestRide?.id,
    staleTime: 60 * 60 * 1000,
    retry: false,
  });

  const tsb = Math.round(fitness?.current_tsb ?? 0);
  const tsbLabel = tsb > 10 ? "Fresh" : tsb < -20 ? "Fatigued" : "Productive";

  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const firstName = user?.full_name?.split(" ")[0] || "Rider";

  return (
    <div className="space-y-12">
      {/* ============ MASTHEAD ============ */}
      <header className="border-b-2 border-vb-border-subtle pb-8">
        <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.18em] text-vb-red">
          Today · {today}
        </p>
        <h1 className="font-display text-5xl leading-[0.95] tracking-tight md:text-6xl">
          Welcome back,<br />
          {firstName}.
        </h1>
      </header>

      {/* ============ COACH MARCO NUDGE (pull-quote) ============ */}
      {nudge && (
        <section className="border-l-4 border-vb-red bg-vb-surface px-6 py-6 md:px-8 md:py-7">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
              A note from Marco
            </p>
            <Link
              href="/dashboard/coach"
              className="text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
            >
              Reply →
            </Link>
          </div>
          <blockquote className="font-sans text-xl italic leading-relaxed text-vb-text md:text-2xl">
            &ldquo;{nudge.nudge}&rdquo;
          </blockquote>
        </section>
      )}

      {/* ============ FITNESS STAT STRIP ============ */}
      <section className="border-y-2 border-vb-text">
        <div className="grid grid-cols-2 md:grid-cols-4">
          {/* CTL */}
          <StatCell
            label="Fitness · CTL"
            value={Math.round(fitness?.current_ctl ?? 0)}
            sub={
              (fitness?.ramp_rate ?? 0) > 0
                ? "↑ rising"
                : (fitness?.ramp_rate ?? 0) < 0
                ? "↓ easing"
                : "steady"
            }
          />
          {/* ATL */}
          <StatCell
            label="Fatigue · ATL"
            value={Math.round(fitness?.current_atl ?? 0)}
            sub="rolling 7-day"
          />
          {/* TSB */}
          <StatCell
            label="Form · TSB"
            value={tsb}
            sub={tsbLabel}
            tone={tsb > 10 ? "good" : tsb < -20 ? "warn" : "neutral"}
          />
          {/* FTP */}
          <StatCell
            label="FTP"
            value={user?.ftp ?? 0}
            sub={user?.weight_kg ? `${((user.ftp ?? 0) / user.weight_kg).toFixed(2)} W/kg` : "watts"}
            featured
            isLast
          />
        </div>
      </section>

      {/* ============ GOALS NEEDING ASSESSMENT ============ */}
      {goalsData?.goals
        .filter((g) => g.needs_assessment)
        .map((goal) => (
          <Link
            key={goal.id}
            href={`/dashboard/goals/${goal.id}/assess`}
            className="block border-2 border-vb-red bg-vb-surface px-6 py-5 transition-colors hover:bg-vb-surface-raised"
          >
            <div className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <ClipboardCheck className="h-5 w-5 shrink-0 text-vb-red" />
                <div>
                  <p className="mb-1 text-[11px] font-bold uppercase tracking-[0.18em] text-vb-red">
                    Race Report Pending
                  </p>
                  <p className="font-display text-2xl leading-none tracking-tight">
                    {goal.event_name}
                  </p>
                  <p className="mt-1 text-sm text-vb-text-dim">
                    Tell Marco how it went.
                  </p>
                </div>
              </div>
              <span className="border-2 border-vb-text px-4 py-2 text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text">
                Write report →
              </span>
            </div>
          </Link>
        ))}

      {/* ============ LATEST DEBRIEF (editorial article) ============ */}
      {latestDebrief && latestRide && (
        <section>
          <SectionHead
            rubric={`Yesterday · ${formatDate(latestRide.ride_date)}`}
            title="Marco's debrief"
            meta={
              <Link
                href={`/dashboard/rides/${latestRide.id}`}
                className="text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
              >
                Full ride →
              </Link>
            }
          />
          <article className="bg-vb-surface px-6 py-6 md:px-8 md:py-8">
            <p className="mb-3 font-display text-2xl leading-tight tracking-tight text-vb-text">
              {latestRide.title}
            </p>
            <div className="prose prose-invert max-w-none prose-p:my-2 prose-p:leading-relaxed prose-p:text-vb-text-dim prose-strong:text-vb-text prose-strong:font-bold prose-em:text-vb-text">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {latestDebrief.debrief}
              </ReactMarkdown>
            </div>
          </article>
        </section>
      )}

      {/* ============ RIDER PROFILE ============ */}
      {fitness &&
        fitness.rider_type !== "unknown" &&
        fitness.profile_scores &&
        fitness.profile_scores.length > 0 && (
          <section>
            <SectionHead
              rubric="Profile"
              title="Rider type"
              meta={
                <Link
                  href="/dashboard/performance"
                  className="text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
                >
                  Full performance →
                </Link>
              }
            />
            <div className="bg-vb-surface px-6 py-6 md:px-8 md:py-8">
              <div className="mb-6 flex flex-wrap items-baseline gap-3">
                <span className="font-display text-3xl leading-none tracking-tight capitalize">
                  {fitness.rider_type.replace("_", " ")}
                </span>
                {fitness.w_per_kg && (
                  <span className="font-mono text-sm text-vb-text-dim">
                    {fitness.w_per_kg.toFixed(2)} W/kg
                  </span>
                )}
              </div>
              <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start sm:gap-10">
                <div className="w-[200px] shrink-0 sm:w-[240px]">
                  <RiderProfileRadar
                    scores={fitness.profile_scores}
                    riderType={fitness.rider_type ?? "unknown"}
                    strengths={fitness.strengths}
                    weaknesses={fitness.weaknesses}
                    compact
                  />
                </div>
                <div className="flex flex-1 flex-col gap-4">
                  {fitness.strengths.length > 0 && (
                    <div>
                      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
                        Strengths
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {fitness.strengths.map((s) => (
                          <span
                            key={s}
                            className="border-2 border-vb-text px-3 py-1 text-[11px] font-bold uppercase tracking-[0.08em] text-vb-text"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {fitness.weaknesses.length > 0 && (
                    <div>
                      <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
                        To work on
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {fitness.weaknesses.map((w) => (
                          <span
                            key={w}
                            className="border-2 border-vb-red px-3 py-1 text-[11px] font-bold uppercase tracking-[0.08em] text-vb-red"
                          >
                            {w}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

      {/* ============ TWO-COLUMN: RECENT RIDES + GOALS / PLAN ============ */}
      <div className="grid gap-10 md:grid-cols-2">
        {/* Recent rides */}
        <section>
          <SectionHead
            rubric="Latest"
            title="Recent rides"
            meta={
              <Link
                href="/dashboard/rides"
                className="text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
              >
                All →
              </Link>
            }
          />
          {recentRides?.rides.length === 0 ? (
            <div className="border-2 border-vb-border-subtle px-5 py-8 text-center text-sm text-vb-text-dim">
              No rides yet.{" "}
              <Link
                href="/dashboard/rides"
                className="text-vb-text hover:text-vb-red"
              >
                Upload your first FIT file →
              </Link>
            </div>
          ) : (
            <ul>
              {recentRides?.rides.map((ride, idx) => (
                <li
                  key={ride.id}
                  className={
                    idx > 0 ? "border-t border-vb-border-subtle" : undefined
                  }
                >
                  <Link
                    href={`/dashboard/rides/${ride.id}`}
                    className="flex items-baseline justify-between gap-4 py-4 transition-colors hover:bg-vb-surface hover:px-3 hover:-mx-3"
                  >
                    <div className="min-w-0">
                      <p className="mb-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
                        {formatDate(ride.ride_date)}
                        {ride.duration_seconds &&
                          ` · ${formatDuration(ride.duration_seconds)}`}
                      </p>
                      <p className="truncate font-sans font-bold text-vb-text">
                        {ride.title}
                      </p>
                    </div>
                    <div className="flex shrink-0 items-baseline gap-6 font-mono text-vb-text">
                      {ride.normalized_power != null && (
                        <span className="text-sm">
                          {Math.round(ride.normalized_power)}
                          <span className="ml-0.5 text-[10px] text-vb-text-dim">W</span>
                        </span>
                      )}
                      {ride.tss != null && (
                        <span className="text-sm">
                          {Math.round(ride.tss)}
                          <span className="ml-0.5 text-[10px] text-vb-text-dim">TSS</span>
                        </span>
                      )}
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Goals + Plan */}
        <div className="space-y-10">
          {/* Goals */}
          <section>
            <SectionHead
              rubric="Calendar"
              title="Active goals"
              meta={
                <Link
                  href="/dashboard/goals"
                  className="text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
                >
                  All →
                </Link>
              }
            />
            {!goalsData ||
            goalsData.goals.filter((g) => g.status === "upcoming").length === 0 ? (
              <div className="border-2 border-vb-border-subtle px-5 py-8 text-center text-sm text-vb-text-dim">
                No upcoming goals.{" "}
                <Link
                  href="/dashboard/goals"
                  className="text-vb-text hover:text-vb-red"
                >
                  Add one →
                </Link>
              </div>
            ) : (
              <ul>
                {goalsData.goals
                  .filter((g) => g.status === "upcoming")
                  .slice(0, 3)
                  .map((goal, idx) => (
                    <li
                      key={goal.id}
                      className={cn(
                        "flex items-baseline justify-between gap-4 py-4",
                        idx > 0 && "border-t border-vb-border-subtle"
                      )}
                    >
                      <div className="min-w-0">
                        <p className="mb-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
                          {formatDate(goal.event_date)} ·{" "}
                          <span>{goal.priority.replace("_", "-")}</span>
                        </p>
                        <p className="truncate font-sans font-bold text-vb-text">
                          {goal.event_name}
                        </p>
                      </div>
                      {goal.days_until != null && goal.days_until > 0 && (
                        <span className="shrink-0 border-2 border-vb-text px-3 py-1 font-mono text-xs text-vb-text">
                          {goal.days_until}d
                        </span>
                      )}
                    </li>
                  ))}
              </ul>
            )}
          </section>

          {/* Active plan */}
          {plans && plans.plans.length > 0 && (
            <section>
              <SectionHead rubric="In flight" title="Active plan" />
              {plans.plans
                .filter((p) => p.status === "active")
                .slice(0, 1)
                .map((plan) => (
                  <div
                    key={plan.id}
                    className="border-l-4 border-vb-text bg-vb-surface px-5 py-5"
                  >
                    <p className="mb-2 font-display text-2xl leading-tight tracking-tight">
                      {plan.name}
                    </p>
                    <p className="font-mono text-xs text-vb-text-dim">
                      {formatDate(plan.start_date)} – {formatDate(plan.end_date)}
                      <br />
                      {plan.total_weeks} weeks · {plan.phase_count} phases
                    </p>
                    <Link
                      href="/dashboard/training"
                      className="mt-4 inline-block text-[11px] font-bold uppercase tracking-[0.10em] text-vb-text hover:text-vb-red"
                    >
                      View calendar →
                    </Link>
                  </div>
                ))}
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

// ============ COMPONENT: stat cell in the editorial strip ============

function StatCell({
  label,
  value,
  sub,
  tone,
  featured,
  isLast,
}: {
  label: string;
  value: number | string;
  sub?: string;
  tone?: "good" | "warn" | "neutral";
  featured?: boolean;
  isLast?: boolean;
}) {
  const valueColor = featured
    ? "text-vb-red"
    : tone === "warn"
    ? "text-vb-red"
    : tone === "good"
    ? "text-vb-text"
    : "text-vb-text";

  return (
    <div
      className={cn(
        "px-5 py-5 md:px-6 md:py-7",
        !isLast && "border-r-0 md:border-r-2 md:border-vb-border-subtle",
        "border-b-2 border-vb-border-subtle md:border-b-0",
        "[&:nth-child(2)]:border-r-0 md:[&:nth-child(2)]:border-r-2"
      )}
    >
      <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
        {label}
      </p>
      <p
        className={cn(
          "font-display text-5xl leading-none tracking-tight tabular-nums md:text-6xl",
          valueColor
        )}
      >
        {value}
      </p>
      {sub && (
        <p className="mt-3 font-mono text-[11px] text-vb-text-dim">{sub}</p>
      )}
    </div>
  );
}

// ============ COMPONENT: editorial section header ============

function SectionHead({
  rubric,
  title,
  meta,
}: {
  rubric: string;
  title: string;
  meta?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex items-baseline justify-between gap-4 border-b-2 border-vb-text pb-3">
      <div>
        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
          {rubric}
        </p>
        <h2 className="mt-1 font-display text-2xl leading-none tracking-tight md:text-3xl">
          {title}
        </h2>
      </div>
      {meta && <div className="shrink-0">{meta}</div>}
    </div>
  );
}

// ============ tiny cn re-export so this file stays self-contained ============
function cn(...classes: Array<string | undefined | boolean | null>): string {
  return classes.filter(Boolean).join(" ");
}
