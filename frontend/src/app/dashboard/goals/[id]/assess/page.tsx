"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import {
  ArrowLeft,
  Check,
  Trophy,
  Frown,
  Ban,
  MessageCircle,
  Target,
  Calendar,
} from "lucide-react";
import { goals as goalsApi } from "@/lib/api";
import { formatDate, formatDuration, cn } from "@/lib/utils";
import type { CandidateRide, GoalAssessmentSubmit } from "@/lib/api";

const STATUS_OPTIONS = [
  { value: "completed", label: "Completed", icon: Trophy, color: "border-vb-forest bg-vb-sage-tint text-vb-forest" },
  { value: "dnf", label: "DNF", icon: Frown, color: "border-vb-clay bg-vb-clay/10 text-vb-clay" },
  { value: "dns", label: "DNS", icon: Ban, color: "border-vb-clay bg-vb-clay/10 text-vb-clay" },
];

export default function AssessPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const goalId = params.id as string;

  const [status, setStatus] = useState("completed");
  const [selectedRideId, setSelectedRideId] = useState<string | null>(null);
  const [finishHours, setFinishHours] = useState("");
  const [finishMinutes, setFinishMinutes] = useState("");
  const [finishSeconds, setFinishSeconds] = useState("");
  const [finishPosition, setFinishPosition] = useState("");
  const [finishPositionTotal, setFinishPositionTotal] = useState("");
  const [satisfaction, setSatisfaction] = useState<number>(7);
  const [exertion, setExertion] = useState<number>(7);
  const [submitted, setSubmitted] = useState(false);

  // Self-assessment sections
  const [legsRating, setLegsRating] = useState<number>(5);
  const [fatigueOnset, setFatigueOnset] = useState("last_30min");
  const [followedPlan, setFollowedPlan] = useState("mostly");
  const [fuelingWorked, setFuelingWorked] = useState("yes");
  const [preRaceConfidence, setPreRaceConfidence] = useState<number>(7);
  const [wentWell, setWentWell] = useState("");
  const [toImprove, setToImprove] = useState("");

  const { data: goal, isLoading } = useQuery({
    queryKey: ["goal", goalId],
    queryFn: () => goalsApi.get(goalId),
  });

  const { data: candidateRidesData } = useQuery({
    queryKey: ["candidate-rides", goalId],
    queryFn: () => goalsApi.getCandidateRides(goalId),
    enabled: !!goal,
  });

  const submitMutation = useMutation({
    mutationFn: (data: GoalAssessmentSubmit) =>
      goalsApi.submitAssessment(goalId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goal", goalId] });
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setSubmitted(true);
    },
  });

  function handleSubmit() {
    let finishTimeSecs: number | null = null;
    if (finishHours || finishMinutes || finishSeconds) {
      finishTimeSecs =
        (parseInt(finishHours || "0") * 3600) +
        (parseInt(finishMinutes || "0") * 60) +
        parseInt(finishSeconds || "0");
    }

    const assessmentData: Record<string, unknown> = {};
    if (legsRating) assessmentData.legs_rating = legsRating;
    if (fatigueOnset) assessmentData.fatigue_onset = fatigueOnset;
    if (followedPlan) assessmentData.followed_plan = followedPlan;
    if (fuelingWorked) assessmentData.fueling_worked = fuelingWorked;
    if (preRaceConfidence) assessmentData.pre_race_confidence = preRaceConfidence;
    if (wentWell.trim()) assessmentData.went_well = wentWell.trim();
    if (toImprove.trim()) assessmentData.to_improve = toImprove.trim();

    submitMutation.mutate({
      status,
      actual_ride_id: selectedRideId,
      finish_time_seconds: finishTimeSecs,
      finish_position: finishPosition ? parseInt(finishPosition) : null,
      finish_position_total: finishPositionTotal ? parseInt(finishPositionTotal) : null,
      overall_satisfaction: satisfaction,
      perceived_exertion: exertion,
      assessment_data: Object.keys(assessmentData).length > 0 ? assessmentData : null,
    });
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border border-vb-border-subtle border-t-vb-forest" />
      </div>
    );
  }

  if (!goal) {
    return <div className="py-20 text-center text-vb-text-dim">Goal not found</div>;
  }

  // Success screen
  if (submitted) {
    return (
      <div className="mx-auto max-w-lg space-y-6 py-8">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-vb-sage-tint">
            <Check className="h-8 w-8 text-vb-forest" />
          </div>
          <h1 className="mt-4 font-display text-2xl font-light tracking-[-0.01em] text-vb-text">
            Assessment Complete
          </h1>
          <p className="mt-1 text-vb-text-dim">
            Your race report for{" "}
            <span className="font-medium text-vb-text">{goal.event_name}</span>{" "}
            has been saved.
          </p>
          <div className="mt-5 flex flex-col items-center gap-2">
            <Link
              href={`/dashboard/coach?goal_id=${goalId}&debrief=true`}
              className="flex items-center gap-2 rounded-sm bg-vb-forest px-6 py-3 text-sm font-medium text-white hover:bg-vb-forest-soft"
            >
              <MessageCircle className="h-4 w-4" />
              Debrief with Coach Marco
            </Link>
          </div>
        </div>

        {/* What's next, invite user to plan their next block */}
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
          <h2 className="font-display text-lg font-light tracking-[-0.01em] text-vb-text">What&apos;s next?</h2>
          <p className="mt-1 text-xs text-vb-text-dim">
            Keep momentum going, pick your next target and we&apos;ll build a plan
            around it, or start a fresh training block to keep building fitness.
          </p>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            <Link
              href="/dashboard/goals?new=1"
              className="flex items-center gap-3 rounded-sm border border-vb-border-subtle bg-vb-bg p-3 hover:bg-vb-surface-raised"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-vb-sage-tint">
                <Target className="h-4 w-4 text-vb-forest" />
              </div>
              <div>
                <p className="text-sm font-medium text-vb-text">Add a new goal</p>
                <p className="text-[11px] text-vb-text-muted">Plan peaks for your next race</p>
              </div>
            </Link>
            <Link
              href="/dashboard/training"
              className="flex items-center gap-3 rounded-sm border border-vb-border-subtle bg-vb-bg p-3 hover:bg-vb-surface-raised"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-vb-sage-tint">
                <Calendar className="h-4 w-4 text-vb-forest" />
              </div>
              <div>
                <p className="text-sm font-medium text-vb-text">New training block</p>
                <p className="text-[11px] text-vb-text-muted">Generate a 12-week plan</p>
              </div>
            </Link>
          </div>
          <Link
            href={`/dashboard/goals/${goalId}`}
            className="mt-4 block text-center text-xs text-vb-text-muted hover:text-vb-forest"
          >
            Or view goal details
          </Link>
        </div>
      </div>
    );
  }

  const inputClasses =
    "w-full rounded-sm border border-vb-border-subtle bg-vb-bg px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none";

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {/* Header */}
      <div>
        <Link
          href={`/dashboard/goals/${goalId}`}
          className="mb-2 inline-flex items-center gap-1 text-sm text-vb-text-dim hover:text-vb-forest"
        >
          <ArrowLeft className="h-4 w-4" /> Back to goal
        </Link>
        <h1 className="font-display text-3xl font-light tracking-[-0.01em] text-vb-text">
          How did {goal.event_name} go?
        </h1>
        <p className="mt-1 text-sm text-vb-text-dim">
          {formatDate(goal.event_date)} &middot;{" "}
          {goal.event_type.replace(/_/g, " ")}
        </p>
      </div>

      {/* Section 1: Result Status */}
      <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
        <h2 className="mb-4 font-display text-xl font-light tracking-[-0.01em] text-vb-text">Result</h2>
        <div className="grid grid-cols-3 gap-3">
          {STATUS_OPTIONS.map((opt) => {
            const Icon = opt.icon;
            const isSelected = status === opt.value;
            return (
              <button
                key={opt.value}
                onClick={() => setStatus(opt.value)}
                className={cn(
                  "flex flex-col items-center gap-2 rounded-sm border p-4 transition-all",
                  isSelected ? opt.color : "border-vb-border-subtle bg-vb-bg text-vb-text-dim hover:border-vb-border"
                )}
              >
                <Icon className="h-6 w-6" />
                <span className="text-sm font-medium">{opt.label}</span>
              </button>
            );
          })}
        </div>

        {/* Finish time + position, only for completed */}
        {status === "completed" && (
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Finish Time
              </label>
              <div className="flex items-center gap-1.5">
                <input
                  type="number"
                  value={finishHours}
                  onChange={(e) => setFinishHours(e.target.value)}
                  placeholder="h"
                  min="0"
                  className={`${inputClasses} w-16 text-center`}
                />
                <span className="text-vb-text-muted">:</span>
                <input
                  type="number"
                  value={finishMinutes}
                  onChange={(e) => setFinishMinutes(e.target.value)}
                  placeholder="m"
                  min="0"
                  max="59"
                  className={`${inputClasses} w-16 text-center`}
                />
                <span className="text-vb-text-muted">:</span>
                <input
                  type="number"
                  value={finishSeconds}
                  onChange={(e) => setFinishSeconds(e.target.value)}
                  placeholder="s"
                  min="0"
                  max="59"
                  className={`${inputClasses} w-16 text-center`}
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Position (optional)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  value={finishPosition}
                  onChange={(e) => setFinishPosition(e.target.value)}
                  placeholder="Place"
                  min="1"
                  className={`${inputClasses} w-20`}
                />
                <span className="text-vb-text-muted">/</span>
                <input
                  type="number"
                  value={finishPositionTotal}
                  onChange={(e) => setFinishPositionTotal(e.target.value)}
                  placeholder="Total"
                  min="1"
                  className={`${inputClasses} w-20`}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Section 2: Link Ride */}
      {candidateRidesData && candidateRidesData.rides.length > 0 && (
        <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
          <h2 className="mb-1 font-display text-xl font-light tracking-[-0.01em] text-vb-text">
            Link Your Ride
          </h2>
          <p className="mb-4 text-xs text-vb-text-dim">
            Select the ride file from race day for detailed analysis
          </p>
          <div className="space-y-2">
            {candidateRidesData.rides.map((ride: CandidateRide) => (
              <button
                key={ride.id}
                onClick={() =>
                  setSelectedRideId(selectedRideId === ride.id ? null : ride.id)
                }
                className={cn(
                  "flex w-full items-center justify-between rounded-sm border p-3 text-left transition-all",
                  selectedRideId === ride.id
                    ? "border-vb-forest bg-vb-sage-tint"
                    : "border-vb-border-subtle bg-vb-bg hover:border-vb-border"
                )}
              >
                <div>
                  <p className="text-sm font-medium text-vb-text">{ride.title}</p>
                  <p className="text-xs text-vb-text-dim">
                    {ride.ride_date}
                    {ride.duration_seconds && ` · ${formatDuration(ride.duration_seconds)}`}
                  </p>
                </div>
                <div className="flex items-center gap-3 text-right">
                  {ride.normalized_power && (
                    <div>
                      <p className="text-sm font-medium tabular-nums text-vb-text">{Math.round(ride.normalized_power)}W</p>
                      <p className="text-[10px] text-vb-text-muted">NP</p>
                    </div>
                  )}
                  {ride.tss && (
                    <div>
                      <p className="text-sm font-medium tabular-nums text-vb-text">{ride.tss}</p>
                      <p className="text-[10px] text-vb-text-muted">TSS</p>
                    </div>
                  )}
                  {selectedRideId === ride.id && (
                    <Check className="h-5 w-5 text-vb-forest" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Section 3: Ratings */}
      <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
        <h2 className="mb-4 font-display text-xl font-light tracking-[-0.01em] text-vb-text">
          How Did It Go?
        </h2>
        <div className="space-y-5">
          {/* Satisfaction */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-vb-text-dim">
                Overall Satisfaction
              </label>
              <span className="font-display text-lg font-light tabular-nums text-vb-text">{satisfaction}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={satisfaction}
              onChange={(e) => setSatisfaction(parseInt(e.target.value))}
              className="w-full accent-vb-forest"
            />
            <div className="mt-1 flex justify-between text-[10px] text-vb-text-muted">
              <span>Disappointed</span>
              <span>Delighted</span>
            </div>
          </div>

          {/* RPE */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-vb-text-dim">
                Perceived Exertion (RPE)
              </label>
              <span className="font-display text-lg font-light tabular-nums text-vb-text">{exertion}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={exertion}
              onChange={(e) => setExertion(parseInt(e.target.value))}
              className="w-full accent-vb-forest"
            />
            <div className="mt-1 flex justify-between text-[10px] text-vb-text-muted">
              <span>Very easy</span>
              <span>Maximal</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 4: Self-Assessment */}
      <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
        <h2 className="mb-4 font-display text-xl font-light tracking-[-0.01em] text-vb-text">
          Self-Assessment
        </h2>
        <div className="space-y-5">
          {/* Physical */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Legs Rating (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={legsRating}
                onChange={(e) => setLegsRating(parseInt(e.target.value))}
                className="w-full accent-vb-forest"
              />
              <div className="mt-0.5 flex justify-between text-[10px] text-vb-text-muted">
                <span>Heavy</span>
                <span className="font-medium tabular-nums text-vb-text-dim">{legsRating}</span>
                <span>Flying</span>
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Fatigue Onset
              </label>
              <select
                value={fatigueOnset}
                onChange={(e) => setFatigueOnset(e.target.value)}
                className={inputClasses}
              >
                <option value="early">Early (first third)</option>
                <option value="middle">Middle</option>
                <option value="last_30min">Last 30 minutes</option>
                <option value="never">Never really fatigued</option>
              </select>
            </div>
          </div>

          {/* Pacing + Nutrition */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Followed Pacing Plan?
              </label>
              <select
                value={followedPlan}
                onChange={(e) => setFollowedPlan(e.target.value)}
                className={inputClasses}
              >
                <option value="yes">Yes, nailed it</option>
                <option value="mostly">Mostly</option>
                <option value="no">No, went off plan</option>
                <option value="no_plan">Had no plan</option>
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
                Fueling / Nutrition
              </label>
              <select
                value={fuelingWorked}
                onChange={(e) => setFuelingWorked(e.target.value)}
                className={inputClasses}
              >
                <option value="yes">Worked well</option>
                <option value="some_issues">Some issues</option>
                <option value="no">Didn&apos;t work</option>
              </select>
            </div>
          </div>

          {/* Mental */}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-vb-text-muted">
              Pre-Race Confidence
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preRaceConfidence}
              onChange={(e) => setPreRaceConfidence(parseInt(e.target.value))}
              className="w-full accent-vb-forest"
            />
            <div className="mt-0.5 flex justify-between text-[10px] text-vb-text-muted">
              <span>Very nervous</span>
              <span className="font-medium tabular-nums text-vb-text-dim">{preRaceConfidence}</span>
              <span>Very confident</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 5: Takeaways */}
      <div className="rounded-md border border-vb-border-subtle bg-vb-surface p-5">
        <h2 className="mb-4 font-display text-xl font-light tracking-[-0.01em] text-vb-text">Takeaways</h2>
        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-vb-forest">
              What went well?
            </label>
            <textarea
              value={wentWell}
              onChange={(e) => setWentWell(e.target.value)}
              placeholder="e.g. Pacing was consistent, fueling strategy worked, strong on climbs..."
              rows={2}
              className={`${inputClasses} resize-none`}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-vb-clay">
              What would you improve?
            </label>
            <textarea
              value={toImprove}
              onChange={(e) => setToImprove(e.target.value)}
              placeholder="e.g. Started too fast, need more climbing practice, forgot gels..."
              rows={2}
              className={`${inputClasses} resize-none`}
            />
          </div>
        </div>
      </div>

      {/* Submit */}
      <div className="flex gap-3">
        <button
          onClick={handleSubmit}
          disabled={submitMutation.isPending}
          className="flex-1 rounded-sm bg-vb-forest px-6 py-3.5 text-sm font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
        >
          {submitMutation.isPending ? "Saving..." : "Submit Race Report"}
        </button>
        <Link
          href={`/dashboard/goals/${goalId}`}
          className="rounded-sm border border-vb-border px-6 py-3.5 text-sm text-vb-forest hover:bg-vb-surface"
        >
          Cancel
        </Link>
      </div>
    </div>
  );
}
