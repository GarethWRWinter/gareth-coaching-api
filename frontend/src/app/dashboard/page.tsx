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
 * ALMANAC-styled dashboard.
 *
 * Editorial-but-warm: a quiet premium cycling journal. Light humanist sans,
 * generous air, forest accent, a single clay highlight, and Marco's notes
 * signed by hand. VoiceBox's editorial bones, Arket's Scandinavian skin.
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
  const tsbLabel =
    tsb > 10 ? "Fresh — good day to go hard" : tsb < -20 ? "Fatigued — absorb it" : "Productive strain";

  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  const hour = new Date().getHours();
  const greeting =
    hour < 5 ? "Up early" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  const nextGoal = goalsData?.goals
    ?.filter((g) => g.status === "upcoming" && g.days_until != null && g.days_until > 0)
    ?.sort((a, b) => (a.days_until ?? 0) - (b.days_until ?? 0))?.[0];

  const firstName = user?.full_name?.split(" ")[0] || "Rider";

  return (
    <div className="space-y-14">
      {/* ============ MASTHEAD ============ */}
      <header>
        <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
          {today}
          {nextGoal && (
            <span className="text-vb-text-muted">
              {" "}· {nextGoal.days_until} days to {nextGoal.event_name}
            </span>
          )}
        </p>
        <h1 className="mt-3 font-display text-5xl font-light leading-[1.04] tracking-[-0.02em] md:text-6xl">
          {greeting}, {firstName}.
        </h1>
      </header>

      {/* ============ A NOTE FROM MARCO ============ */}
      {nudge && (
        <section className="max-w-3xl border-b border-vb-border-subtle pb-10">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
              A note from {user?.coach_name || "Marco"}
            </p>
            <Link
              href="/dashboard/coach"
              className="text-[11px] font-medium uppercase tracking-[0.10em] text-vb-text-muted transition-colors hover:text-vb-forest"
            >
              Reply →
            </Link>
          </div>
          <p className="mt-3 font-light text-2xl leading-[1.55] tracking-[-0.01em] text-vb-text md:text-[26px]">
            {nudge.nudge}
          </p>
          <div className="mt-5 flex items-baseline gap-3">
            <span className="font-script text-3xl leading-none text-vb-forest">
              {user?.coach_name || "Marco"}
            </span>
            <span className="text-xs tracking-[0.04em] text-vb-text-muted">your coach</span>
          </div>
        </section>
      )}

      {/* ============ FITNESS STAT STRIP ============ */}
      <section className="overflow-hidden rounded-md border border-vb-border-subtle bg-vb-border-subtle">
        <div className="grid grid-cols-2 gap-px md:grid-cols-4">
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
          <StatCell
            label="Fatigue · ATL"
            value={Math.round(fitness?.current_atl ?? 0)}
            sub="rolling 7-day"
          />
          <StatCell label="Form · TSB" value={tsb} sub={tsbLabel} featured />
          <StatCell
            label="FTP"
            value={user?.ftp ?? 0}
            unit="w"
            sub={
              user?.weight_kg
                ? `${((user.ftp ?? 0) / user.weight_kg).toFixed(2)} W/kg`
                : "watts"
            }
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
            className="block rounded-md border border-vb-border-subtle border-l-[3px] border-l-vb-clay bg-vb-surface px-6 py-5 transition-colors hover:bg-vb-surface-raised"
          >
            <div className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <ClipboardCheck className="h-5 w-5 shrink-0 text-vb-clay" />
                <div>
                  <p className="mb-1 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-clay">
                    So — how did it go?
                  </p>
                  <p className="font-display text-xl leading-tight tracking-[-0.01em]">
                    {goal.event_name}
                  </p>
                  <p className="mt-1 text-sm text-vb-text-dim">
                    Debrief with Marco — what you tell him shapes the next block.
                  </p>
                </div>
              </div>
              <span className="shrink-0 rounded-sm border border-vb-border px-4 py-2 text-[11px] font-medium uppercase tracking-[0.10em] text-vb-forest">
                Write report →
              </span>
            </div>
          </Link>
        ))}

      {/* ============ LATEST DEBRIEF (editorial article) ============ */}
      {latestDebrief && latestRide && (
        <section>
          <AlmanacRule />
          <SectionHead
            rubric={`${user?.coach_name || "Marco"}'s debrief · ${formatDate(latestRide.ride_date)}`}
            title={latestRide.title}
            meta={
              <Link
                href={`/dashboard/rides/${latestRide.id}`}
                className="text-[11px] font-medium uppercase tracking-[0.10em] text-vb-text-muted hover:text-vb-forest"
              >
                Full ride →
              </Link>
            }
          />
          <article className="max-w-3xl">
            <div className="prose max-w-none font-light text-vb-text-dim prose-p:my-3 prose-p:text-[19px] prose-p:leading-[1.7] prose-strong:font-medium prose-strong:text-vb-text prose-em:text-vb-clay prose-em:not-italic">
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
                  className="text-[11px] font-medium uppercase tracking-[0.10em] text-vb-text-muted hover:text-vb-forest"
                >
                  Full performance →
                </Link>
              }
            />
            <div className="rounded-md border border-vb-border-subtle bg-vb-surface px-6 py-7 md:px-8">
              <div className="mb-6 flex flex-wrap items-baseline gap-3">
                <span className="font-display text-2xl font-light capitalize leading-none tracking-[-0.01em]">
                  {fitness.rider_type.replace("_", " ")}
                </span>
                {fitness.w_per_kg && (
                  <span className="text-sm text-vb-text-dim">
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
                      <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                        Strengths
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {fitness.strengths.map((s) => (
                          <span
                            key={s}
                            className="rounded-full bg-vb-sage-tint px-3 py-1 text-[11px] font-medium uppercase tracking-[0.08em] text-vb-forest"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {fitness.weaknesses.length > 0 && (
                    <div>
                      <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                        To work on
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {fitness.weaknesses.map((w) => (
                          <span
                            key={w}
                            className="rounded-full border border-vb-clay/40 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.08em] text-vb-clay"
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
      <div className="grid gap-12 md:grid-cols-2">
        {/* Recent rides */}
        <section>
          <SectionHead
            rubric="Latest"
            title="Recent rides"
            meta={
              <Link
                href="/dashboard/rides"
                className="text-[11px] font-medium uppercase tracking-[0.10em] text-vb-text-muted hover:text-vb-forest"
              >
                All →
              </Link>
            }
          />
          {recentRides?.rides.length === 0 ? (
            <div className="rounded-md border border-vb-border-subtle px-5 py-8 text-center text-sm text-vb-text-dim">
              No rides yet — and I&apos;d love to see what you can do.{" "}
              <Link href="/dashboard/rides" className="text-vb-forest hover:underline">
                Upload a ride or connect Strava →
              </Link>{" "}
              and I&apos;ll start building your power profile.
            </div>
          ) : (
            <ul>
              {recentRides?.rides.map((ride, idx) => (
                <li
                  key={ride.id}
                  className={idx > 0 ? "border-t border-vb-border-subtle" : undefined}
                >
                  <Link
                    href={`/dashboard/rides/${ride.id}`}
                    className="-mx-3 flex items-baseline justify-between gap-4 rounded-sm px-3 py-4 transition-colors hover:bg-vb-surface"
                  >
                    <div className="min-w-0">
                      <p className="mb-0.5 text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                        {formatDate(ride.ride_date)}
                        {ride.duration_seconds &&
                          ` · ${formatDuration(ride.duration_seconds)}`}
                      </p>
                      <p className="truncate font-medium text-vb-text">{ride.title}</p>
                    </div>
                    <div className="flex shrink-0 items-baseline gap-6 tabular-nums text-vb-text">
                      {ride.normalized_power != null && (
                        <span className="text-sm">
                          {Math.round(ride.normalized_power)}
                          <span className="ml-0.5 text-[10px] text-vb-text-muted">W</span>
                        </span>
                      )}
                      {ride.tss != null && (
                        <span className="text-sm">
                          {Math.round(ride.tss)}
                          <span className="ml-0.5 text-[10px] text-vb-text-muted">TSS</span>
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
        <div className="space-y-12">
          <section>
            <SectionHead
              rubric="Calendar"
              title="Active goals"
              meta={
                <Link
                  href="/dashboard/goals"
                  className="text-[11px] font-medium uppercase tracking-[0.10em] text-vb-text-muted hover:text-vb-forest"
                >
                  All →
                </Link>
              }
            />
            {!goalsData ||
            goalsData.goals.filter((g) => g.status === "upcoming").length === 0 ? (
              <div className="rounded-md border border-vb-border-subtle px-5 py-8 text-center text-sm text-vb-text-dim">
                Nothing on the calendar. Give me a race to aim you at —{" "}
                <Link href="/dashboard/goals" className="text-vb-forest hover:underline">
                  set a goal →
                </Link>{" "}
                and the whole plan bends around it.
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
                        <p className="mb-0.5 text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                          {formatDate(goal.event_date)} ·{" "}
                          <span>{goal.priority.replace("_", "-")}</span>
                        </p>
                        <p className="truncate font-medium text-vb-text">
                          {goal.event_name}
                        </p>
                      </div>
                      {goal.days_until != null && goal.days_until > 0 && (
                        <span className="shrink-0 rounded-full bg-vb-sage-tint px-3 py-1 text-xs tabular-nums text-vb-forest">
                          {goal.days_until}d
                        </span>
                      )}
                    </li>
                  ))}
              </ul>
            )}
          </section>

          {plans && plans.plans.length > 0 && (
            <section>
              <SectionHead rubric="In flight" title="Active plan" />
              {plans.plans
                .filter((p) => p.status === "active")
                .slice(0, 1)
                .map((plan) => (
                  <div
                    key={plan.id}
                    className="rounded-md border border-vb-border-subtle border-l-[3px] border-l-vb-forest bg-vb-surface px-5 py-5"
                  >
                    <p className="mb-2 font-display text-xl font-light leading-tight tracking-[-0.01em]">
                      {plan.name}
                    </p>
                    <p className="text-xs leading-relaxed text-vb-text-dim">
                      {formatDate(plan.start_date)} – {formatDate(plan.end_date)}
                      <br />
                      {plan.total_weeks} weeks · {plan.phase_count} phases
                    </p>
                    <Link
                      href="/dashboard/training"
                      className="mt-4 inline-block text-[11px] font-medium uppercase tracking-[0.10em] text-vb-forest hover:text-vb-forest-soft"
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
  unit,
  featured,
}: {
  label: string;
  value: number | string;
  sub?: string;
  unit?: string;
  featured?: boolean;
}) {
  return (
    <div className={cn("px-6 py-7", featured ? "bg-vb-forest" : "bg-vb-surface")}>
      <p
        className={cn(
          "text-[11px] font-medium uppercase tracking-[0.16em]",
          featured ? "text-white/70" : "text-vb-text-muted"
        )}
      >
        {label}
      </p>
      <p
        className={cn(
          "mt-4 font-display text-[44px] font-light leading-none tracking-[-0.03em] tabular-nums",
          featured ? "text-white" : "text-vb-text"
        )}
      >
        {value}
        {unit && (
          <span
            className={cn(
              "ml-1 text-base font-light tracking-normal",
              featured ? "text-white/60" : "text-vb-text-muted"
            )}
          >
            {unit}
          </span>
        )}
      </p>
      {sub && (
        <p
          className={cn(
            "mt-3.5 text-[13px]",
            featured ? "text-white/70" : "text-vb-text-dim"
          )}
        >
          {sub}
        </p>
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
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
          {rubric}
        </p>
        <h2 className="mt-1.5 font-display text-2xl font-light leading-none tracking-[-0.01em] md:text-[28px]">
          {title}
        </h2>
      </div>
      {meta && <div className="shrink-0 pb-1">{meta}</div>}
    </div>
  );
}

// ============ COMPONENT: ALMANAC route-contour divider ============

function AlmanacRule() {
  return (
    <svg
      className="almanac-rule mb-10"
      viewBox="0 0 1000 22"
      preserveAspectRatio="none"
      fill="none"
      aria-hidden
    >
      <path
        d="M0,15 C60,15 90,7 150,9 C210,11 240,18 300,16 C360,14 390,4 450,7 C510,10 540,17 600,14 C660,11 690,5 750,8 C810,11 840,15 900,12 C950,10 975,13 1000,12"
        stroke="currentColor"
        strokeWidth="1.2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

// ============ tiny cn re-export so this file stays self-contained ============
function cn(...classes: Array<string | undefined | boolean | null>): string {
  return classes.filter(Boolean).join(" ");
}
