"use client";

import { useRouter } from "next/navigation";
import { useState, useRef } from "react";
import {
  Bike,
  ChevronRight,
  Check,
  Calendar,
  Trophy,
  Link2,
  Upload,
  MapPin,
} from "lucide-react";
import { onboarding, users, goals, training } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const GOALS = [
  {
    value: "build_fitness",
    label: "Build General Fitness",
    desc: "Improve overall health and endurance",
  },
  {
    value: "target_event",
    label: "Train for an Event",
    desc: "Prepare for a specific race or sportive",
  },
  {
    value: "improve_ftp",
    label: "Increase FTP",
    desc: "Push your functional threshold power higher",
  },
  {
    value: "race",
    label: "Race Competitively",
    desc: "Train to compete and podium",
  },
  {
    value: "learn_skills",
    label: "Learn & Improve Skills",
    desc: "Pacing, nutrition, bike handling",
  },
];

const PREFERENCES = [
  { value: "indoor", label: "Indoor (Trainer)" },
  { value: "outdoor", label: "Outdoor" },
  { value: "both", label: "Both" },
];

const EVENT_TYPES = [
  { value: "road_race", label: "Road Race" },
  { value: "crit", label: "Criterium" },
  { value: "time_trial", label: "Time Trial" },
  { value: "gran_fondo", label: "Gran Fondo" },
  { value: "sportive", label: "Sportive" },
  { value: "gravel", label: "Gravel" },
  { value: "mtb", label: "Mountain Bike" },
];

const PRIORITIES = [
  { value: "a_race", label: "A Race", desc: "Your main target event" },
  { value: "b_race", label: "B Race", desc: "Important but not the top priority" },
  { value: "c_race", label: "C Race", desc: "Training race or lower priority" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const gpxInputRef = useRef<HTMLInputElement>(null);

  // Wizard step (0=goal, 1=event details if target_event, 2=experience, 3=physical)
  const [step, setStep] = useState(0);
  const [goal, setGoal] = useState("");

  // Event details (only shown when goal === "target_event")
  const [eventName, setEventName] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [eventType, setEventType] = useState("");
  const [eventPriority, setEventPriority] = useState("a_race");
  const [eventDuration, setEventDuration] = useState("");
  const [eventNotes, setEventNotes] = useState("");
  const [routeUrl, setRouteUrl] = useState("");
  const [gpxFile, setGpxFile] = useState<File | null>(null);

  // Experience details
  const [weeklyHours, setWeeklyHours] = useState("6");
  const [yearsCycling, setYearsCycling] = useState("1");
  const [preference, setPreference] = useState("both");

  // Training schedule
  const [hardDays, setHardDays] = useState<number[]>([5, 6]); // Sat/Sun default
  const [restDays, setRestDays] = useState<number[]>([]);

  // Physical stats
  const [ftp, setFtp] = useState("");
  const [weight, setWeight] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Whether event step is needed
  const isEventGoal = goal === "target_event";

  // Total steps: 3 normally, 4 if training for event
  const totalSteps = isEventGoal ? 4 : 3;

  // Map display step to actual step index
  const getActualStep = (displayStep: number) => {
    if (!isEventGoal) return displayStep;
    return displayStep;
  };

  const handleNext = () => {
    if (step === 0 && isEventGoal) {
      setStep(1); // Go to event details
    } else if (step === 0) {
      setStep(2); // Skip event details
    } else {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step === 2 && !isEventGoal) {
      setStep(0);
    } else {
      setStep(step - 1);
    }
  };

  const handleGpxSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.name.toLowerCase().endsWith(".gpx")) {
      setGpxFile(file);
    }
  };

  const handleFinish = async () => {
    setLoading(true);
    setError("");
    try {
      // 1. Submit onboarding quiz
      await onboarding.submitQuiz({
        primary_goal: goal,
        current_weekly_volume_hours: parseFloat(weeklyHours),
        years_cycling: parseInt(yearsCycling),
        indoor_outdoor_preference: preference,
      });

      // 2. Update profile with FTP, weight, and schedule preferences
      const profileData: Record<string, number | number[]> = {};
      if (ftp) profileData.ftp = parseInt(ftp);
      if (weight) profileData.weight_kg = parseFloat(weight);
      profileData.preferred_hard_days = hardDays;
      profileData.rest_days = restDays;
      await users.updateProfile(profileData);

      // 3. If training for event, create the goal event
      let createdGoalId: string | null = null;
      if (isEventGoal && eventName && eventDate && eventType) {
        const createdGoal = await goals.create({
          event_name: eventName,
          event_date: eventDate,
          event_type: eventType,
          priority: eventPriority,
          target_duration_minutes: eventDuration
            ? parseInt(eventDuration)
            : undefined,
          notes: eventNotes || undefined,
          route_url: routeUrl || undefined,
        });
        createdGoalId = createdGoal?.id ?? null;

        // 4. If GPX file was selected, upload it
        if (gpxFile && createdGoal?.id) {
          try {
            await goals.uploadGpx(createdGoal.id, gpxFile);
          } catch (gpxErr) {
            console.error("GPX upload failed:", gpxErr);
            // Don't block onboarding for GPX upload failure
          }
        }
      }

      // 5. Auto-generate a training plan
      //    - If the user has a target event, build it around that goal so the
      //      plan peaks on race day.
      //    - Otherwise still generate a default 12-week plan so the user lands
      //      on the dashboard with something to do.
      try {
        await training.generatePlan({
          goal_event_id: createdGoalId ?? undefined,
          periodization_model: "traditional",
        });
      } catch (planErr) {
        console.error("Plan generation failed during onboarding:", planErr);
        // Don't block onboarding — user can generate manually from the
        // training page if something went wrong here.
      }

      await refreshUser();
      router.push("/dashboard");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      setError(message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Progress bar calculation
  const currentProgress = (() => {
    if (!isEventGoal) {
      return step === 0 ? 0 : step === 2 ? 1 : 2;
    }
    return step;
  })();

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-lg">
        {/* Progress */}
        <div className="mb-8 flex items-center justify-center gap-2">
          {Array.from({ length: totalSteps }).map((_, s) => (
            <div
              key={s}
              className={cn(
                "h-1.5 w-16 rounded-full transition-colors",
                s <= currentProgress ? "bg-blue-500" : "bg-slate-700"
              )}
            />
          ))}
        </div>

        {/* Step 0: Goal Selection */}
        {step === 0 && (
          <div>
            <h2 className="text-center text-2xl font-bold text-white">
              What&apos;s your main goal?
            </h2>
            <p className="mt-2 text-center text-sm text-slate-400">
              We&apos;ll tailor your experience around this
            </p>

            <div className="mt-8 space-y-3">
              {GOALS.map((g) => (
                <button
                  key={g.value}
                  onClick={() => setGoal(g.value)}
                  className={cn(
                    "flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-colors",
                    goal === g.value
                      ? "border-blue-500 bg-blue-600/10"
                      : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border",
                      goal === g.value
                        ? "border-blue-500 bg-blue-500"
                        : "border-slate-600"
                    )}
                  >
                    {goal === g.value && (
                      <Check className="h-3 w-3 text-white" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{g.label}</p>
                    <p className="text-xs text-slate-400">{g.desc}</p>
                  </div>
                </button>
              ))}
            </div>

            <button
              onClick={handleNext}
              disabled={!goal}
              className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
            >
              Continue <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Step 1: Event Details (only when target_event selected) */}
        {step === 1 && isEventGoal && (
          <div>
            <h2 className="text-center text-2xl font-bold text-white">
              Tell us about your event
            </h2>
            <p className="mt-2 text-center text-sm text-slate-400">
              The more detail you give, the better your AI coach can prepare you
            </p>

            <div className="mt-6 space-y-4">
              {/* Event Name */}
              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium text-slate-300">
                  <Trophy className="h-4 w-4 text-amber-400" />
                  Event Name
                </label>
                <input
                  type="text"
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="e.g. Etape du Tour, London to Brighton"
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              {/* Event Date */}
              <div>
                <label className="mb-1.5 flex items-center gap-2 text-sm font-medium text-slate-300">
                  <Calendar className="h-4 w-4 text-blue-400" />
                  Event Date
                </label>
                <input
                  type="date"
                  value={eventDate}
                  onChange={(e) => setEventDate(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              {/* Event Type */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  Event Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {EVENT_TYPES.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => setEventType(t.value)}
                      className={cn(
                        "rounded-lg border px-3 py-2 text-xs font-medium transition-colors",
                        eventType === t.value
                          ? "border-blue-500 bg-blue-600/10 text-blue-400"
                          : "border-slate-700 text-slate-400 hover:border-slate-600"
                      )}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Priority */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  Priority
                </label>
                <div className="flex gap-2">
                  {PRIORITIES.map((p) => (
                    <button
                      key={p.value}
                      onClick={() => setEventPriority(p.value)}
                      className={cn(
                        "flex-1 rounded-lg border py-2 text-center text-xs font-medium transition-colors",
                        eventPriority === p.value
                          ? "border-blue-500 bg-blue-600/10 text-blue-400"
                          : "border-slate-700 text-slate-400 hover:border-slate-600"
                      )}
                      title={p.desc}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Expected Duration */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  Expected Duration (minutes, optional)
                </label>
                <input
                  type="number"
                  value={eventDuration}
                  onChange={(e) => setEventDuration(e.target.value)}
                  placeholder="e.g. 180"
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              {/* Route / Challenge Info Section */}
              <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
                <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                  <MapPin className="h-4 w-4 text-green-400" />
                  Route &amp; Challenge Details
                </h3>
                <p className="mb-3 text-xs text-slate-400">
                  Help your AI coach understand the challenge. Share a route URL
                  or upload a GPX file.
                </p>

                {/* Route URL */}
                <div className="mb-3">
                  <label className="mb-1.5 flex items-center gap-2 text-xs font-medium text-slate-400">
                    <Link2 className="h-3.5 w-3.5" />
                    Strava Route / Segment / Race Website URL
                  </label>
                  <input
                    type="url"
                    value={routeUrl}
                    onChange={(e) => setRouteUrl(e.target.value)}
                    placeholder="e.g. https://www.strava.com/routes/123456"
                    className="w-full rounded-lg border border-slate-600 bg-slate-700 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>

                {/* GPX Upload */}
                <div>
                  <label className="mb-1.5 flex items-center gap-2 text-xs font-medium text-slate-400">
                    <Upload className="h-3.5 w-3.5" />
                    Upload GPX Route File
                  </label>
                  <input
                    ref={gpxInputRef}
                    type="file"
                    accept=".gpx"
                    onChange={handleGpxSelect}
                    className="hidden"
                  />
                  <button
                    onClick={() => gpxInputRef.current?.click()}
                    className={cn(
                      "w-full rounded-lg border border-dashed py-3 text-center text-xs transition-colors",
                      gpxFile
                        ? "border-green-500/50 bg-green-500/10 text-green-400"
                        : "border-slate-600 text-slate-400 hover:border-slate-500 hover:text-slate-300"
                    )}
                  >
                    {gpxFile ? (
                      <span className="flex items-center justify-center gap-2">
                        <Check className="h-3.5 w-3.5" />
                        {gpxFile.name}
                      </span>
                    ) : (
                      "Click to select a .gpx file"
                    )}
                  </button>
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  Notes about the challenge (optional)
                </label>
                <textarea
                  value={eventNotes}
                  onChange={(e) => setEventNotes(e.target.value)}
                  placeholder="e.g. 3 big climbs in the last 50km, expect headwinds on the coast..."
                  rows={2}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={handleBack}
                className="rounded-lg border border-slate-700 px-6 py-3 text-sm text-slate-300 hover:bg-slate-800"
              >
                Back
              </button>
              <button
                onClick={() => setStep(2)}
                disabled={!eventName || !eventDate || !eventType}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
              >
                Continue <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Experience */}
        {step === 2 && (
          <div>
            <h2 className="text-center text-2xl font-bold text-white">
              Tell us about your cycling
            </h2>

            <div className="mt-8 space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  How many hours per week can you train?
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="2"
                    max="20"
                    step="1"
                    value={weeklyHours}
                    onChange={(e) => setWeeklyHours(e.target.value)}
                    className="flex-1 accent-blue-500"
                  />
                  <span className="w-16 text-right text-lg font-bold text-white">
                    {weeklyHours}h
                  </span>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Years of cycling experience
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0"
                    max="20"
                    step="1"
                    value={yearsCycling}
                    onChange={(e) => setYearsCycling(e.target.value)}
                    className="flex-1 accent-blue-500"
                  />
                  <span className="w-16 text-right text-lg font-bold text-white">
                    {yearsCycling}y
                  </span>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Where do you prefer to ride?
                </label>
                <div className="flex gap-3">
                  {PREFERENCES.map((p) => (
                    <button
                      key={p.value}
                      onClick={() => setPreference(p.value)}
                      className={cn(
                        "flex-1 rounded-lg border py-2.5 text-sm font-medium transition-colors",
                        preference === p.value
                          ? "border-blue-500 bg-blue-600/10 text-blue-400"
                          : "border-slate-700 text-slate-400 hover:border-slate-600"
                      )}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Your training schedule
                </label>
                <p className="mb-3 text-xs text-slate-400">
                  Tap to set each day. Hard days get intensity sessions, rest days have no training.
                </p>
                <div className="grid grid-cols-7 gap-2">
                  {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => {
                    const isHard = hardDays.includes(idx);
                    const isRest = restDays.includes(idx);
                    return (
                      <div key={day} className="text-center">
                        <p className="mb-1 text-[10px] font-medium text-slate-500">{day}</p>
                        <button
                          type="button"
                          onClick={() => {
                            if (isRest) {
                              setRestDays(restDays.filter(d => d !== idx));
                              setHardDays([...hardDays, idx]);
                            } else if (isHard) {
                              setHardDays(hardDays.filter(d => d !== idx));
                            } else {
                              setRestDays([...restDays, idx]);
                            }
                          }}
                          className={cn(
                            "w-full rounded-lg py-2.5 text-xs font-medium transition-colors",
                            isHard
                              ? "bg-orange-500/20 text-orange-400 border border-orange-500/40"
                              : isRest
                                ? "bg-slate-800 text-slate-500 border border-slate-700"
                                : "bg-blue-500/15 text-blue-400 border border-blue-500/30"
                          )}
                        >
                          {isHard ? "Hard" : isRest ? "Rest" : "Easy"}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="mt-8 flex gap-3">
              <button
                onClick={handleBack}
                className="rounded-lg border border-slate-700 px-6 py-3 text-sm text-slate-300 hover:bg-slate-800"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white hover:bg-blue-500"
              >
                Continue <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Physical stats */}
        {step === 3 && (
          <div>
            <h2 className="text-center text-2xl font-bold text-white">
              Physical stats (optional)
            </h2>
            <p className="mt-2 text-center text-sm text-slate-400">
              These help us calculate your power-to-weight ratio and zones
            </p>

            <div className="mt-8 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  FTP (Functional Threshold Power)
                </label>
                <input
                  type="number"
                  value={ftp}
                  onChange={(e) => setFtp(e.target.value)}
                  placeholder="e.g. 250"
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
                <p className="mt-1 text-xs text-slate-500">
                  Don&apos;t know? You can do an FTP test later.
                </p>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  Body Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  placeholder="e.g. 75"
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            {error && (
              <p className="mt-4 text-center text-sm text-red-400">{error}</p>
            )}

            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setStep(2)}
                className="rounded-lg border border-slate-700 px-6 py-3 text-sm text-slate-300 hover:bg-slate-800"
              >
                Back
              </button>
              <button
                onClick={handleFinish}
                disabled={loading}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-green-600 py-3 text-sm font-semibold text-white hover:bg-green-500 disabled:opacity-50"
              >
                {loading ? "Setting up..." : "Start Training"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
