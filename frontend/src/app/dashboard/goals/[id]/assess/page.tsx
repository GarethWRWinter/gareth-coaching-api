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
  { value: "completed", label: "Completed", icon: Trophy, color: "border-green-500 bg-green-900/20 text-green-400" },
  { value: "dnf", label: "DNF", icon: Frown, color: "border-amber-500 bg-amber-900/20 text-amber-400" },
  { value: "dns", label: "DNS", icon: Ban, color: "border-red-500 bg-red-900/20 text-red-400" },
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
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!goal) {
    return <div className="py-20 text-center text-slate-400">Goal not found</div>;
  }

  // Success screen
  if (submitted) {
    return (
      <div className="mx-auto max-w-lg space-y-6 py-8">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-600/20">
            <Check className="h-8 w-8 text-green-400" />
          </div>
          <h1 className="mt-4 text-2xl font-bold text-white">
            Assessment Complete
          </h1>
          <p className="mt-1 text-slate-400">
            Your race report for{" "}
            <span className="font-medium text-white">{goal.event_name}</span>{" "}
            has been saved.
          </p>
          <div className="mt-5 flex flex-col items-center gap-2">
            <Link
              href={`/dashboard/coach?goal_id=${goalId}&debrief=true`}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-500"
            >
              <MessageCircle className="h-4 w-4" />
              Debrief with Coach Marco
            </Link>
          </div>
        </div>

        {/* What's next — invite user to plan their next block */}
        <div className="rounded-xl border border-blue-500/40 bg-blue-900/10 p-5">
          <h2 className="text-base font-semibold text-white">What&apos;s next?</h2>
          <p className="mt-1 text-xs text-slate-400">
            Keep momentum going — pick your next target and we&apos;ll build a plan
            around it, or start a fresh training block to keep building fitness.
          </p>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            <Link
              href="/dashboard/goals?new=1"
              className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-800/60 p-3 hover:border-blue-500/60 hover:bg-slate-800"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-500/20">
                <Target className="h-4 w-4 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">Add a new goal</p>
                <p className="text-[11px] text-slate-400">Plan peaks for your next race</p>
              </div>
            </Link>
            <Link
              href="/dashboard/training"
              className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-800/60 p-3 hover:border-blue-500/60 hover:bg-slate-800"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-500/20">
                <Calendar className="h-4 w-4 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">New training block</p>
                <p className="text-[11px] text-slate-400">Generate a 12-week plan</p>
              </div>
            </Link>
          </div>
          <Link
            href={`/dashboard/goals/${goalId}`}
            className="mt-4 block text-center text-xs text-slate-500 hover:text-slate-300"
          >
            Or view goal details
          </Link>
        </div>
      </div>
    );
  }

  const inputClasses =
    "w-full rounded-lg border border-slate-600 bg-slate-700 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none";

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {/* Header */}
      <div>
        <Link
          href={`/dashboard/goals/${goalId}`}
          className="mb-2 inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" /> Back to goal
        </Link>
        <h1 className="text-2xl font-bold text-white">
          How did {goal.event_name} go?
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          {formatDate(goal.event_date)} &middot;{" "}
          {goal.event_type.replace(/_/g, " ")}
        </p>
      </div>

      {/* Section 1: Result Status */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">Result</h2>
        <div className="grid grid-cols-3 gap-3">
          {STATUS_OPTIONS.map((opt) => {
            const Icon = opt.icon;
            const isSelected = status === opt.value;
            return (
              <button
                key={opt.value}
                onClick={() => setStatus(opt.value)}
                className={cn(
                  "flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all",
                  isSelected ? opt.color : "border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600"
                )}
              >
                <Icon className="h-6 w-6" />
                <span className="text-sm font-medium">{opt.label}</span>
              </button>
            );
          })}
        </div>

        {/* Finish time + position — only for completed */}
        {status === "completed" && (
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
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
                <span className="text-slate-500">:</span>
                <input
                  type="number"
                  value={finishMinutes}
                  onChange={(e) => setFinishMinutes(e.target.value)}
                  placeholder="m"
                  min="0"
                  max="59"
                  className={`${inputClasses} w-16 text-center`}
                />
                <span className="text-slate-500">:</span>
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
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
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
                <span className="text-slate-500">/</span>
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
        <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
          <h2 className="mb-1 text-lg font-semibold text-white">
            Link Your Ride
          </h2>
          <p className="mb-4 text-xs text-slate-400">
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
                  "flex w-full items-center justify-between rounded-lg border-2 p-3 text-left transition-all",
                  selectedRideId === ride.id
                    ? "border-green-500 bg-green-900/10"
                    : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
                )}
              >
                <div>
                  <p className="text-sm font-medium text-white">{ride.title}</p>
                  <p className="text-xs text-slate-400">
                    {ride.ride_date}
                    {ride.duration_seconds && ` · ${formatDuration(ride.duration_seconds)}`}
                  </p>
                </div>
                <div className="flex items-center gap-3 text-right">
                  {ride.normalized_power && (
                    <div>
                      <p className="text-sm font-medium text-white">{Math.round(ride.normalized_power)}W</p>
                      <p className="text-[10px] text-slate-500">NP</p>
                    </div>
                  )}
                  {ride.tss && (
                    <div>
                      <p className="text-sm font-medium text-white">{ride.tss}</p>
                      <p className="text-[10px] text-slate-500">TSS</p>
                    </div>
                  )}
                  {selectedRideId === ride.id && (
                    <Check className="h-5 w-5 text-green-400" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Section 3: Ratings */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          How Did It Go?
        </h2>
        <div className="space-y-5">
          {/* Satisfaction */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">
                Overall Satisfaction
              </label>
              <span className="text-lg font-bold text-white">{satisfaction}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={satisfaction}
              onChange={(e) => setSatisfaction(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="mt-1 flex justify-between text-[10px] text-slate-600">
              <span>Disappointed</span>
              <span>Delighted</span>
            </div>
          </div>

          {/* RPE */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-sm font-medium text-slate-300">
                Perceived Exertion (RPE)
              </label>
              <span className="text-lg font-bold text-white">{exertion}/10</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={exertion}
              onChange={(e) => setExertion(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="mt-1 flex justify-between text-[10px] text-slate-600">
              <span>Very easy</span>
              <span>Maximal</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 4: Self-Assessment */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">
          Self-Assessment
        </h2>
        <div className="space-y-5">
          {/* Physical */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
                Legs Rating (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={legsRating}
                onChange={(e) => setLegsRating(parseInt(e.target.value))}
                className="w-full accent-blue-500"
              />
              <div className="mt-0.5 flex justify-between text-[10px] text-slate-600">
                <span>Heavy</span>
                <span className="font-medium text-slate-400">{legsRating}</span>
                <span>Flying</span>
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
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
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
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
              <label className="mb-1.5 block text-xs font-medium text-slate-400">
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
            <label className="mb-1.5 block text-xs font-medium text-slate-400">
              Pre-Race Confidence
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preRaceConfidence}
              onChange={(e) => setPreRaceConfidence(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
            <div className="mt-0.5 flex justify-between text-[10px] text-slate-600">
              <span>Very nervous</span>
              <span className="font-medium text-slate-400">{preRaceConfidence}</span>
              <span>Very confident</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 5: Takeaways */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">Takeaways</h2>
        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-green-400">
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
            <label className="mb-1.5 block text-xs font-medium text-amber-400">
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
          className="flex-1 rounded-xl bg-green-600 px-6 py-3.5 text-sm font-semibold text-white hover:bg-green-500 disabled:opacity-50"
        >
          {submitMutation.isPending ? "Saving..." : "Submit Race Report"}
        </button>
        <Link
          href={`/dashboard/goals/${goalId}`}
          className="rounded-xl border border-slate-700 px-6 py-3.5 text-sm text-slate-300 hover:bg-slate-800"
        >
          Cancel
        </Link>
      </div>
    </div>
  );
}
