"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft,
  Play,
  Pause,
  Square,
  SkipForward,
  SkipBack,
  Bluetooth,
  BluetoothConnected,
  Heart,
  Zap,
  Activity,
  Gauge,
  X,
  Check,
  AlertTriangle,
  List,
  ChevronRight,
  Volume2,
  VolumeX,
  Radio,
} from "lucide-react";
import { rides, training } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDuration, cn } from "@/lib/utils";
import { getZoneFromPct, getZoneColors, ZONE_COLORS } from "@/lib/trainingZones";
import { useBluetooth } from "@/hooks/useBluetooth";
import { useCoachRadio } from "@/hooks/useCoachRadio";
import { useTelemetryBuffer } from "@/hooks/useTelemetryBuffer";
import {
  useTrainingSession,
  type SessionStep,
} from "@/hooks/useTrainingSession";

const STEP_COLORS: Record<string, string> = {
  warmup: "bg-vb-forest/50",
  steady_state: "bg-vb-forest/70",
  interval_on: "bg-vb-clay",
  interval_off: "bg-vb-sunken",
  cooldown: "bg-vb-forest/40",
  free_ride: "bg-vb-forest/60",
  ramp: "bg-vb-forest/80",
};

const STEP_BG_COLORS: Record<string, string> = {
  warmup: "bg-vb-sage-tint",
  steady_state: "bg-vb-sage-tint",
  interval_on: "bg-vb-clay/15",
  interval_off: "bg-vb-sunken",
  cooldown: "bg-vb-sage-tint",
  free_ride: "bg-vb-sage-tint",
  ramp: "bg-vb-sage-tint",
};

const STEP_TEXT_COLORS: Record<string, string> = {
  warmup: "text-vb-forest",
  steady_state: "text-vb-forest",
  interval_on: "text-vb-clay",
  interval_off: "text-vb-text-muted",
  cooldown: "text-vb-forest",
  free_ride: "text-vb-forest",
  ramp: "text-vb-forest",
};

const STEP_BORDER_COLORS: Record<string, string> = {
  warmup: "border-vb-forest/40",
  steady_state: "border-vb-forest/40",
  interval_on: "border-vb-clay/40",
  interval_off: "border-vb-border-subtle",
  cooldown: "border-vb-forest/40",
  free_ride: "border-vb-forest/40",
  ramp: "border-vb-forest/40",
};

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0)
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// Auto-pause/resume timeout (seconds with no power before auto-pausing)
const AUTO_PAUSE_DELAY = 15;
// Minimum power reading to consider "riding"
const MIN_POWER_THRESHOLD = 10;

export default function TrainingSessionPage() {
  const params = useParams();
  const router = useRouter();
  const workoutId = params.id as string;
  const { user } = useAuth();
  const ftp = user?.ftp || 200;
  const [showDevicePanel, setShowDevicePanel] = useState(false);
  const [showConfirmStop, setShowConfirmStop] = useState(false);
  const [showStepList, setShowStepList] = useState(true);
  const [autoPaused, setAutoPaused] = useState(false);
  const [deviceSetupDone, setDeviceSetupDone] = useState(false);
  const [autoPauseCountdown, setAutoPauseCountdown] = useState<number | null>(
    null
  );

  // Save flow state
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [resumePrompt, setResumePrompt] = useState<{
    startedAt: string;
    dataPointCount: number;
  } | null>(null);
  const startedSavingRef = useRef(false);

  const { data: workout, isLoading } = useQuery({
    queryKey: ["workout", workoutId],
    queryFn: () => training.getWorkout(workoutId),
  });

  const [btState, btActions] = useBluetooth();

  const handleTargetPowerChange = useCallback(
    async (watts: number) => {
      if (btState.trainer.connected && btState.trainer.ergMode) {
        await btActions.setTargetPower(watts);
      }
    },
    [btState.trainer.connected, btState.trainer.ergMode, btActions]
  );

  const [session, sessionActions] = useTrainingSession(
    workout?.steps || [],
    ftp,
    handleTargetPowerChange
  );

  // === Telemetry buffering ===
  const buffer = useTelemetryBuffer({
    workoutId,
    elapsedSeconds: session.totalElapsedSeconds,
    btState,
    running: session.status === "running",
  });

  // Initialise buffer when the session leaves "idle" for the first time.
  // The buffer hook also lazy-inits on first sample, but doing it here keeps
  // startedAt tied to the user's actual "Start" click rather than the first
  // BLE tick.
  const sessionStartedRef = useRef(false);
  useEffect(() => {
    if (session.status !== "idle" && !sessionStartedRef.current) {
      sessionStartedRef.current = true;
      buffer.start();
    }
  }, [session.status, buffer]);

  // Check for a resumable buffered session on mount.
  useEffect(() => {
    if (!buffer.hasStored()) return;
    if (session.status !== "idle") return;
    const stored = window.localStorage.getItem(
      `marco:session-buffer:${workoutId}`
    );
    if (!stored) return;
    try {
      const parsed = JSON.parse(stored) as {
        startedAt: string;
        dataPoints: unknown[];
      };
      setResumePrompt({
        startedAt: parsed.startedAt,
        dataPointCount: parsed.dataPoints?.length ?? 0,
      });
    } catch {
      // ignore — corrupted entry, will be overwritten on next start
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // === Save flow ===
  const saveSession = useCallback(async () => {
    if (startedSavingRef.current) return;
    startedSavingRef.current = true;
    setSaving(true);
    setSaveError(null);

    try {
      buffer.flush();
      const dataPoints = buffer.getBuffer();
      const startedAt = buffer.getStartTime() ?? new Date();

      if (dataPoints.length === 0) {
        // Nothing to save — discard quietly and bail
        buffer.clear();
        router.push(`/dashboard/training/${workoutId}`);
        return;
      }

      const ride = await rides.record({
        title: workout?.title || "Indoor Session",
        ride_date: startedAt.toISOString(),
        workout_id: workoutId,
        data_points: dataPoints,
      });

      buffer.clear();
      router.push(`/dashboard/rides/${ride.id}`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setSaveError(msg);
      startedSavingRef.current = false;
    } finally {
      setSaving(false);
    }
  }, [buffer, router, workout?.title, workoutId]);

  // Auto-save when the session naturally completes.
  useEffect(() => {
    if (session.status === "completed" && !startedSavingRef.current) {
      void saveSession();
    }
  }, [session.status, saveSession]);

  // === Coach Radio ===
  const currentStep_ = session.steps[session.currentStepIndex];
  const nextStep_ = session.steps[session.currentStepIndex + 1];
  const coach = useCoachRadio({
    status: session.status,
    currentStepIndex: session.currentStepIndex,
    stepElapsedSeconds: session.stepElapsedSeconds,
    totalElapsedSeconds: session.totalElapsedSeconds,
    currentTargetWatts: session.currentTargetWatts,
    currentTargetPct: session.currentTargetPct,
    currentStep: currentStep_,
    nextStep: nextStep_,
    ftp,
    livePower: btState.power.value ?? 0,
    enabled: true,
  });

  // === Auto-pause when no power detected ===
  const lastPowerTime = useRef<number>(Date.now());
  const autoPauseTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  // Track when power is being recorded
  useEffect(() => {
    if (btState.power.value && btState.power.value > MIN_POWER_THRESHOLD) {
      lastPowerTime.current = Date.now();
      setAutoPauseCountdown(null);

      // Auto-resume if we were auto-paused
      if (autoPaused && session.status === "paused") {
        sessionActions.resume();
        setAutoPaused(false);
      }
    }
  }, [btState.power.value, autoPaused, session.status, sessionActions]);

  // Check for power dropout periodically
  useEffect(() => {
    if (
      session.status !== "running" ||
      !btState.power.connected
    ) {
      if (autoPauseTimer.current) {
        clearInterval(autoPauseTimer.current);
        autoPauseTimer.current = null;
      }
      setAutoPauseCountdown(null);
      return;
    }

    autoPauseTimer.current = setInterval(() => {
      const elapsed = (Date.now() - lastPowerTime.current) / 1000;
      if (elapsed >= AUTO_PAUSE_DELAY) {
        // Auto-pause
        sessionActions.pause();
        setAutoPaused(true);
        setAutoPauseCountdown(null);
      } else if (elapsed >= 5) {
        // Show countdown
        setAutoPauseCountdown(Math.ceil(AUTO_PAUSE_DELAY - elapsed));
      } else {
        setAutoPauseCountdown(null);
      }
    }, 1000);

    return () => {
      if (autoPauseTimer.current) {
        clearInterval(autoPauseTimer.current);
        autoPauseTimer.current = null;
      }
    };
  }, [session.status, btState.power.connected, sessionActions]);

  // Prevent accidental navigation
  useEffect(() => {
    if (session.status === "running" || session.status === "paused") {
      const handleBeforeUnload = (e: BeforeUnloadEvent) => {
        e.preventDefault();
      };
      window.addEventListener("beforeunload", handleBeforeUnload);
      return () =>
        window.removeEventListener("beforeunload", handleBeforeUnload);
    }
  }, [session.status]);

  // Cleanup trainer on unmount
  useEffect(() => {
    return () => {
      btActions.disconnectAll();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Scroll active step into view in step list
  const activeStepRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (activeStepRef.current) {
      activeStepRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [session.currentStepIndex]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-vb-bg">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-vb-forest border-t-transparent" />
      </div>
    );
  }

  if (!workout || !workout.steps || workout.steps.length === 0) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-vb-bg text-vb-text-dim">
        <p>Workout not found or has no steps</p>
        <Link
          href={`/dashboard/training/${workoutId}`}
          className="mt-4 text-vb-forest"
        >
          Back to workout
        </Link>
      </div>
    );
  }

  const currentStep = session.steps[session.currentStepIndex];
  const nextStep = session.steps[session.currentStepIndex + 1];
  const stepRemaining = currentStep
    ? Math.max(0, currentStep.durationSeconds - session.stepElapsedSeconds)
    : 0;
  const totalRemaining = Math.max(
    0,
    session.totalDurationSeconds - session.totalElapsedSeconds
  );

  // Calculate progress
  const elapsedBeforeCurrentStep = session.steps
    .slice(0, session.currentStepIndex)
    .reduce((sum, s) => sum + s.durationSeconds, 0);
  const workoutProgress =
    ((elapsedBeforeCurrentStep + session.stepElapsedSeconds) /
      session.totalDurationSeconds) *
    100;

  // Live metrics
  const livePower = btState.power.value ?? 0;
  const liveHR = btState.heartRate.value ?? 0;
  const liveCadence = btState.cadence.value ?? 0;

  const connectedDeviceCount = [
    btState.heartRate.connected,
    btState.power.connected,
    btState.cadence.connected,
    btState.trainer.connected,
  ].filter(Boolean).length;

  const isActive =
    session.status === "running" || session.status === "paused";

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-vb-bg">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-vb-border-subtle px-6 py-3">
        <div className="flex items-center gap-4">
          {session.status === "idle" && (
            <Link
              href={`/dashboard/training/${workoutId}`}
              className="text-vb-text-dim hover:text-vb-forest"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
          )}
          <div>
            <h1 className="font-display text-lg font-light tracking-[-0.01em] text-vb-text">{workout.title}</h1>
            <p className="text-xs text-vb-text-dim">{workout.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Step list toggle */}
          {isActive && (
            <button
              onClick={() => setShowStepList(!showStepList)}
              className={cn(
                "flex items-center gap-1.5 rounded-sm px-3 py-1.5 text-sm transition-colors",
                showStepList
                  ? "bg-vb-sunken text-vb-text"
                  : "bg-vb-surface text-vb-text-dim hover:bg-vb-surface-raised"
              )}
            >
              <List className="h-4 w-4" />
              Steps
            </button>
          )}

          {/* Coach Radio mute toggle */}
          {isActive && (
            <button
              onClick={() => coach.setMuted(!coach.muted)}
              className={cn(
                "flex items-center gap-1.5 rounded-sm px-3 py-1.5 text-sm transition-colors",
                coach.muted
                  ? "bg-vb-surface text-vb-text-muted hover:bg-vb-surface-raised"
                  : "bg-vb-sage-tint text-vb-forest"
              )}
              title={coach.muted ? "Unmute Coach" : "Mute Coach"}
            >
              {coach.muted ? (
                <VolumeX className="h-4 w-4" />
              ) : (
                <Volume2 className="h-4 w-4" />
              )}
              Radio
            </button>
          )}

          {/* Device connection button */}
          <button
            onClick={() => setShowDevicePanel(!showDevicePanel)}
            className={cn(
              "flex items-center gap-1.5 rounded-sm px-3 py-1.5 text-sm transition-colors",
              connectedDeviceCount > 0
                ? "bg-vb-sage-tint text-vb-forest"
                : "bg-vb-surface text-vb-text-dim hover:bg-vb-surface-raised"
            )}
          >
            {connectedDeviceCount > 0 ? (
              <BluetoothConnected className="h-4 w-4" />
            ) : (
              <Bluetooth className="h-4 w-4" />
            )}
            {connectedDeviceCount > 0
              ? `${connectedDeviceCount} device${connectedDeviceCount > 1 ? "s" : ""}`
              : "Connect"}
          </button>

          {/* Elapsed / Remaining time */}
          <div className="flex items-center gap-4 text-sm">
            <div className="text-center">
              <p className="text-[10px] uppercase text-vb-text-muted">Elapsed</p>
              <p className="font-display font-light tabular-nums text-vb-text">
                {formatTime(session.totalElapsedSeconds)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] uppercase text-vb-text-muted">Remaining</p>
              <p className="font-display font-light tabular-nums text-vb-text-dim">
                {formatTime(totalRemaining)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Workout Progress Bar */}
      <div className="relative h-12 border-b border-vb-border-subtle bg-vb-surface">
        <div className="flex h-full">
          {session.steps.map((step, idx) => {
            const widthPct =
              (step.durationSeconds / session.totalDurationSeconds) * 100;
            const isActiveStep = idx === session.currentStepIndex;
            const isDone = idx < session.currentStepIndex;

            return (
              <div
                key={idx}
                className={cn(
                  "relative flex items-center justify-center border-r border-vb-border-subtle transition-all",
                  isDone
                    ? `${getZoneColors(step.powerTargetPct).bgSolid} opacity-60`
                    : isActiveStep
                      ? `${getZoneColors(step.powerTargetPct).bg} ring-1 ring-inset ring-white/30`
                      : "bg-vb-sunken"
                )}
                style={{ width: `${widthPct}%`, minWidth: "2px" }}
              >
                {widthPct > 3 && (
                  <span
                    className={cn(
                      "text-[9px] font-medium truncate px-0.5",
                      isDone || isActiveStep ? "text-white" : "text-vb-text-muted"
                    )}
                  >
                    {step.stepType === "interval_on"
                      ? "ON"
                      : step.stepType === "interval_off"
                        ? "OFF"
                        : widthPct > 6
                          ? `Z${getZoneFromPct(step.powerTargetPct).zone}`
                          : ""}
                  </span>
                )}

                {/* Active step progress fill */}
                {isActiveStep && session.status !== "idle" && (
                  <div
                    className={cn(
                      "absolute inset-y-0 left-0",
                      getZoneColors(step.powerTargetPct).bgSolid,
                      "opacity-40"
                    )}
                    style={{
                      width: `${Math.min(100, (session.stepElapsedSeconds / step.durationSeconds) * 100)}%`,
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Step List (visible during session) */}
        {isActive && showStepList && (
          <div className="w-72 border-r border-vb-border-subtle bg-vb-surface overflow-y-auto">
            <div className="px-4 py-3 border-b border-vb-border-subtle">
              <h3 className="text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Workout Steps
              </h3>
            </div>
            <div className="divide-y divide-vb-border-subtle">
              {session.steps.map((step, idx) => {
                const isCurrentStep = idx === session.currentStepIndex;
                const isDone = idx < session.currentStepIndex;
                const targetW = Math.round(step.powerTargetPct * ftp);
                const stepZone = getZoneFromPct(step.powerTargetPct);
                const stepZoneColors = ZONE_COLORS[stepZone.zone];

                return (
                  <div
                    key={idx}
                    ref={isCurrentStep ? activeStepRef : undefined}
                    className={cn(
                      "flex items-center gap-3 px-4 py-2.5 transition-colors",
                      isCurrentStep
                        ? `${stepZoneColors.bg} border-l-2 ${stepZoneColors.border}`
                        : isDone
                          ? "opacity-40"
                          : "opacity-70"
                    )}
                  >
                    {/* Step color indicator */}
                    <div
                      className={cn(
                        "h-6 w-1 rounded-full shrink-0",
                        stepZoneColors.bgSolid,
                        isDone && "opacity-50"
                      )}
                    />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={cn(
                            "text-xs font-medium capitalize",
                            isCurrentStep
                              ? "text-vb-text"
                              : isDone
                                ? "text-vb-text-muted"
                                : "text-vb-text-dim"
                          )}
                        >
                          {step.stepType.replace("_", " ")}
                        </span>
                        {step.isInterval && (
                          <span className="text-[9px] text-vb-text-muted">
                            {step.repeatIndex}/{step.repeatTotal}
                          </span>
                        )}
                        <span
                          className={cn(
                            "text-[9px] font-semibold rounded px-1 py-0.5",
                            stepZoneColors.bg,
                            stepZoneColors.text
                          )}
                        >
                          Z{stepZone.zone}
                        </span>
                      </div>
                      {step.notes && (
                        <p className="text-[10px] text-vb-text-muted truncate">
                          {step.notes}
                        </p>
                      )}
                    </div>

                    <div className="text-right shrink-0">
                      <p
                        className={cn(
                          "font-display text-xs font-light tabular-nums",
                          isCurrentStep ? "text-vb-text" : "text-vb-text-dim"
                        )}
                      >
                        {targetW}W
                      </p>
                      <p className="text-[10px] text-vb-text-muted tabular-nums">
                        {formatTime(step.durationSeconds)}
                      </p>
                    </div>

                    {/* Current step indicator */}
                    {isCurrentStep && (
                      <ChevronRight className="h-3 w-3 text-vb-forest shrink-0" />
                    )}
                    {isDone && (
                      <Check className="h-3 w-3 text-vb-text-muted shrink-0" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Center: Current Step & Controls */}
        <div className="flex flex-1 flex-col items-center justify-center gap-8 p-8">
          {/* Auto-pause banner */}
          {autoPaused && session.status === "paused" && (
            <div className="flex items-center gap-3 rounded-sm bg-vb-clay/10 border border-vb-clay/30 px-5 py-3">
              <Pause className="h-5 w-5 text-vb-clay shrink-0" />
              <div>
                <p className="text-sm font-medium text-vb-clay">
                  Auto-paused, no power detected
                </p>
                <p className="text-xs text-vb-clay/70">
                  Start pedalling to resume automatically
                </p>
              </div>
            </div>
          )}

          {/* Auto-pause countdown */}
          {autoPauseCountdown !== null && session.status === "running" && (
            <div className="flex items-center gap-2 text-xs text-vb-clay/70">
              <AlertTriangle className="h-3 w-3" />
              <span>
                No power, auto-pausing in {autoPauseCountdown}s
              </span>
            </div>
          )}

          {/* Current Step Info */}
          {session.status === "idle" && !deviceSetupDone ? (
            /* === Device Setup Screen === */
            <div className="w-full max-w-lg text-center">
              <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text mb-1">
                {workout.title}
              </h2>
              <p className="text-vb-text-dim mb-8">
                {formatDuration(session.totalDurationSeconds)} &middot;{" "}
                {session.steps.length} steps
              </p>

              <div className="rounded-md border border-vb-border-subtle bg-vb-surface overflow-hidden mb-6">
                <div className="border-b border-vb-border-subtle px-5 py-3">
                  <h3 className="text-sm font-medium text-vb-text flex items-center gap-2">
                    <Bluetooth className="h-4 w-4 text-vb-forest" />
                    Connect Your Devices
                  </h3>
                </div>

                {!btState.isSupported ? (
                  <div className="p-5">
                    <div className="flex items-center gap-3 rounded-sm bg-vb-clay/10 border border-vb-clay/30 p-4">
                      <AlertTriangle className="h-5 w-5 text-vb-clay shrink-0" />
                      <div className="text-left">
                        <p className="text-sm font-medium text-vb-clay">
                          Bluetooth not available in this browser
                        </p>
                        <p className="text-xs text-vb-clay/70 mt-1">
                          Use <strong>Chrome</strong>, <strong>Edge</strong>, or
                          <strong> Brave</strong> on a Mac, PC, or Android.{" "}
                          <strong>iPhone and iPad aren&apos;t supported</strong>:
                          every iOS browser (including Chrome) runs on Safari&apos;s
                          engine, which doesn&apos;t have Web Bluetooth. Native
                          iOS app coming soon.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="divide-y divide-vb-border-subtle">
                    <DeviceRow
                      icon={<Zap className="h-5 w-5 text-vb-forest" />}
                      label="Power Meter"
                      connected={btState.power.connected}
                      name={btState.power.name}
                      value={btState.power.value ? `${btState.power.value}W` : undefined}
                      onConnect={btActions.connectPower}
                      onDisconnect={() => btActions.disconnectDevice("power")}
                    />
                    <DeviceRow
                      icon={<Heart className="h-5 w-5 text-vb-clay" />}
                      label="Heart Rate Monitor"
                      connected={btState.heartRate.connected}
                      name={btState.heartRate.name}
                      value={btState.heartRate.value ? `${btState.heartRate.value} bpm` : undefined}
                      onConnect={btActions.connectHeartRate}
                      onDisconnect={() => btActions.disconnectDevice("heartRate")}
                    />
                    <DeviceRow
                      icon={<Gauge className="h-5 w-5 text-vb-forest" />}
                      label="Smart Trainer (ERG)"
                      description="Controls resistance automatically"
                      connected={btState.trainer.connected}
                      name={btState.trainer.name}
                      value={btState.trainer.connected ? (btState.trainer.ergMode ? "ERG Mode" : "Connected") : undefined}
                      onConnect={btActions.connectTrainer}
                      onDisconnect={() => btActions.disconnectDevice("trainer")}
                    />
                    <DeviceRow
                      icon={<Activity className="h-5 w-5 text-vb-forest" />}
                      label="Cadence Sensor"
                      description={btState.trainer.connected ? "Available from trainer" : undefined}
                      connected={btState.cadence.connected}
                      name={btState.cadence.name}
                      value={btState.cadence.value ? `${btState.cadence.value} rpm` : undefined}
                      onConnect={btActions.connectCadence}
                      onDisconnect={() => btActions.disconnectDevice("cadence")}
                      fromTrainer={btState.cadence.connected && !!btState.cadence.name?.includes("(cadence)")}
                    />
                  </div>
                )}
              </div>

              <button
                onClick={() => setDeviceSetupDone(true)}
                className="flex items-center gap-2 rounded-full bg-vb-forest px-8 py-4 text-lg font-medium text-white hover:bg-vb-forest-soft transition-colors mx-auto"
              >
                <Play className="h-6 w-6" />
                {connectedDeviceCount > 0 ? "Continue to Start" : "Continue Without Devices"}
              </button>

              {connectedDeviceCount === 0 && btState.isSupported && (
                <p className="mt-3 text-xs text-vb-text-muted">
                  Connect at least a power meter for the best experience
                </p>
              )}
            </div>
          ) : session.status === "idle" && deviceSetupDone ? (
            <div className="text-center">
              <p className="text-lg text-vb-text-dim mb-2">Ready to start</p>
              <h2 className="font-display text-3xl font-light tracking-[-0.01em] text-vb-text mb-1">
                {workout.title}
              </h2>
              <p className="text-vb-text-dim mb-2">
                {formatDuration(session.totalDurationSeconds)} &middot;{" "}
                {session.steps.length} steps
              </p>
              {connectedDeviceCount > 0 && (
                <p className="text-sm text-vb-forest mb-4">
                  <BluetoothConnected className="inline h-4 w-4 mr-1" />
                  {connectedDeviceCount} device{connectedDeviceCount > 1 ? "s" : ""} connected
                </p>
              )}
            </div>
          ) : session.status === "completed" ? (
            <div className="text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-vb-sage-tint mx-auto">
                <Check className="h-8 w-8 text-vb-forest" />
              </div>
              <h2 className="font-display text-3xl font-light tracking-[-0.01em] text-vb-text mb-2">
                Workout Complete!
              </h2>
              <p className="text-vb-text-dim mb-4">
                Total time: {formatTime(session.totalElapsedSeconds)}
              </p>
              {coach.currentMessage && (
                <div className="max-w-md mx-auto mb-6">
                  <div className="bg-vb-surface backdrop-blur rounded-md px-6 py-3 border border-vb-border-subtle">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Radio className="h-3 w-3 text-vb-forest" />
                      <span className="text-[10px] font-medium uppercase tracking-[0.16em] text-vb-forest">
                        {user?.coach_name || "Marco"} · Race Radio
                      </span>
                    </div>
                    <p className="text-sm text-vb-text-dim italic">
                      &ldquo;{coach.currentMessage}&rdquo;
                    </p>
                  </div>
                </div>
              )}
              <Link
                href={`/dashboard/training/${workoutId}`}
                className="mt-2 inline-flex items-center gap-2 rounded-sm bg-vb-forest px-6 py-3 text-white font-medium hover:bg-vb-forest-soft transition-colors"
              >
                Back to Workout
              </Link>
            </div>
          ) : currentStep ? (
            <>
              {/* Step type label with zone */}
              <div className="text-center">
                {(() => {
                  const zone = getZoneFromPct(currentStep.powerTargetPct);
                  const zc = ZONE_COLORS[zone.zone];
                  return (
                    <div className="flex items-center justify-center gap-2">
                      <span
                        className={cn(
                          "rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider",
                          zc.bg,
                          zc.text
                        )}
                      >
                        {currentStep.stepType.replace("_", " ")}
                        {currentStep.isInterval &&
                          ` ${currentStep.repeatIndex}/${currentStep.repeatTotal}`}
                      </span>
                      <span
                        className={cn(
                          "rounded-full px-2.5 py-1 text-xs font-semibold",
                          zc.bg,
                          zc.text
                        )}
                      >
                        Z{zone.zone} {zone.name}
                      </span>
                    </div>
                  );
                })()}
                {currentStep.notes && (
                  <p className="mt-2 text-sm text-vb-text-dim">
                    {currentStep.notes}
                  </p>
                )}
              </div>

              {/* Target Power - big display (single clay highlight: the live target) */}
              <div className="text-center">
                <p className="font-display text-7xl font-bold text-vb-clay tabular-nums tracking-[-0.02em]">
                  {session.currentTargetWatts}
                  <span className="text-2xl text-vb-text-muted ml-1.5 font-light">W</span>
                </p>
                <p className="text-lg mt-1 text-vb-text-dim tabular-nums">
                  {Math.round(session.currentTargetPct * 100)}% FTP
                </p>
              </div>

              {/* Interval Progress Bar */}
              <div className="w-full max-w-lg">
                {(() => {
                  const zone = getZoneFromPct(currentStep.powerTargetPct);
                  const zc = ZONE_COLORS[zone.zone];
                  const progressPct = Math.min(
                    100,
                    (session.stepElapsedSeconds / currentStep.durationSeconds) * 100
                  );
                  return (
                    <div>
                      {/* Main progress bar */}
                      <div className={cn("relative h-6 rounded-full overflow-hidden", zc.bg)}>
                        <div
                          className={cn(
                            "absolute inset-y-0 left-0 rounded-full transition-all duration-500",
                            zc.bgSolid,
                            "opacity-70"
                          )}
                          style={{ width: `${progressPct}%` }}
                        />
                        <div className="absolute inset-0 flex items-center justify-between px-3 text-[11px] font-mono font-semibold text-white">
                          <span>{formatTime(session.stepElapsedSeconds)}</span>
                          <span>{formatTime(stepRemaining)}</span>
                        </div>
                      </div>

                      {/* Upcoming steps preview */}
                      {(() => {
                        const upcoming = session.steps.slice(
                          session.currentStepIndex + 1,
                          session.currentStepIndex + 4
                        );
                        if (upcoming.length === 0) return null;
                        const totalUpcoming = upcoming.reduce(
                          (s, st) => s + st.durationSeconds,
                          0
                        );
                        return (
                          <div className="flex gap-1 mt-2 h-5 rounded overflow-hidden">
                            {upcoming.map((s, i) => {
                              const sz = getZoneFromPct(s.powerTargetPct);
                              const szc = ZONE_COLORS[sz.zone];
                              const w = (s.durationSeconds / totalUpcoming) * 100;
                              return (
                                <div
                                  key={i}
                                  className={cn(
                                    "flex items-center justify-center rounded-sm",
                                    szc.bg
                                  )}
                                  style={{ width: `${w}%`, minWidth: "30px" }}
                                >
                                  <span
                                    className={cn(
                                      "text-[9px] font-medium truncate px-1",
                                      szc.text
                                    )}
                                  >
                                    Z{sz.zone} {formatTime(s.durationSeconds)}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        );
                      })()}
                    </div>
                  );
                })()}
              </div>

              {/* Live metrics strip: rider numbers front and centre */}
              <div className="w-full max-w-lg rounded-md border border-vb-border-subtle bg-vb-surface px-5 py-4">
                <div className="grid grid-cols-5 gap-2">
                  <div className="text-center">
                    <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                      Power
                    </p>
                    <p
                      className={cn(
                        "mt-1 font-display text-2xl font-semibold tabular-nums",
                        livePower > 0
                          ? livePower > session.currentTargetWatts * 1.05
                            ? "text-vb-clay"
                            : livePower < session.currentTargetWatts * 0.95
                              ? "text-vb-text-dim"
                              : "text-vb-forest"
                          : "text-vb-text-muted"
                      )}
                    >
                      {livePower}
                      <span className="ml-0.5 text-xs font-normal text-vb-text-muted">
                        W
                      </span>
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                      Heart Rate
                    </p>
                    <p
                      className={cn(
                        "mt-1 font-display text-2xl font-semibold tabular-nums",
                        liveHR > 0 ? "text-vb-clay" : "text-vb-text-muted"
                      )}
                    >
                      {liveHR}
                      <span className="ml-0.5 text-xs font-normal text-vb-text-muted">
                        bpm
                      </span>
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                      Cadence
                    </p>
                    <p
                      className={cn(
                        "mt-1 font-display text-2xl font-semibold tabular-nums",
                        liveCadence > 0 ? "text-vb-forest" : "text-vb-text-muted"
                      )}
                    >
                      {liveCadence}
                      <span className="ml-0.5 text-xs font-normal text-vb-text-muted">
                        rpm
                      </span>
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                      Elapsed
                    </p>
                    <p className="mt-1 font-display text-2xl font-semibold tabular-nums text-vb-text">
                      {formatTime(session.totalElapsedSeconds)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium uppercase tracking-[0.14em] text-vb-text-muted">
                      Remaining
                    </p>
                    <p className="mt-1 font-display text-2xl font-semibold tabular-nums text-vb-text-dim">
                      {formatTime(totalRemaining)}
                    </p>
                  </div>
                </div>
                <div className="mt-3 h-1.5 rounded-full bg-vb-sunken">
                  <div
                    className="h-full rounded-full bg-vb-forest transition-all"
                    style={{ width: `${Math.min(100, workoutProgress)}%` }}
                  />
                </div>
                {btState.trainer.connected && (
                  <p className="mt-2.5 text-center text-[10px] font-medium uppercase tracking-[0.14em] text-vb-forest">
                    ERG active · {btState.trainer.name} · holding{" "}
                    {session.currentTargetWatts}W
                  </p>
                )}
              </div>

              {/* Coach Message Overlay */}
              {coach.currentMessage && (
                <div className="animate-pulse w-full max-w-lg">
                  <div className="bg-vb-surface backdrop-blur rounded-md px-6 py-3 border border-vb-border-subtle text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Radio className="h-3 w-3 text-vb-forest" />
                      <span className="text-[10px] font-medium uppercase tracking-[0.16em] text-vb-forest">
                        {user?.coach_name || "Marco"} · Race Radio
                      </span>
                    </div>
                    <p className="text-sm text-vb-text-dim italic">
                      &ldquo;{coach.currentMessage}&rdquo;
                    </p>
                  </div>
                </div>
              )}

              {/* Next step preview */}
              {nextStep && (
                <div className="flex items-center gap-2 text-sm text-vb-text-muted">
                  <span>Next:</span>
                  {(() => {
                    const nz = getZoneFromPct(nextStep.powerTargetPct);
                    const nzc = ZONE_COLORS[nz.zone];
                    return (
                      <>
                        <span
                          className={cn(
                            "rounded px-2 py-0.5 text-xs font-medium",
                            nzc.bg,
                            nzc.text
                          )}
                        >
                          Z{nz.zone} {nextStep.stepType.replace("_", " ")}
                        </span>
                        <span>
                          {Math.round(nextStep.powerTargetPct * ftp)}W &middot;{" "}
                          {formatTime(nextStep.durationSeconds)}
                        </span>
                      </>
                    );
                  })()}
                </div>
              )}
            </>
          ) : null}

          {/* Controls */}
          <div className="flex items-center gap-4">
            {session.status === "idle" && (
              <button
                onClick={sessionActions.start}
                className="flex items-center gap-2 rounded-full bg-vb-forest px-8 py-4 text-lg font-medium text-white hover:bg-vb-forest-soft transition-colors"
              >
                <Play className="h-6 w-6" /> Start Workout
              </button>
            )}

            {session.status === "running" && (
              <>
                <button
                  onClick={sessionActions.prevStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-sunken text-vb-text hover:bg-vb-border-subtle transition-colors"
                  title="Previous Step / Restart"
                >
                  <SkipBack className="h-5 w-5" />
                </button>
                <button
                  onClick={sessionActions.pause}
                  className="flex h-14 w-14 items-center justify-center rounded-full bg-vb-sunken text-vb-text hover:bg-vb-border-subtle transition-colors"
                  title="Pause"
                >
                  <Pause className="h-6 w-6" />
                </button>
                <button
                  onClick={sessionActions.skipStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-sunken text-vb-text hover:bg-vb-border-subtle transition-colors"
                  title="Skip Step"
                >
                  <SkipForward className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setShowConfirmStop(true)}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-clay/15 text-vb-clay hover:bg-vb-clay/25 transition-colors"
                  title="Stop"
                >
                  <Square className="h-5 w-5" />
                </button>
              </>
            )}

            {session.status === "paused" && (
              <>
                <button
                  onClick={sessionActions.prevStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-sunken text-vb-text hover:bg-vb-border-subtle transition-colors"
                  title="Previous Step / Restart"
                >
                  <SkipBack className="h-5 w-5" />
                </button>
                <button
                  onClick={() => {
                    sessionActions.resume();
                    setAutoPaused(false);
                  }}
                  className="flex items-center gap-2 rounded-full bg-vb-forest px-8 py-4 text-lg font-medium text-white hover:bg-vb-forest-soft transition-colors"
                >
                  <Play className="h-6 w-6" /> Resume
                </button>
                <button
                  onClick={sessionActions.skipStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-sunken text-vb-text hover:bg-vb-border-subtle transition-colors"
                  title="Skip Step"
                >
                  <SkipForward className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setShowConfirmStop(true)}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-vb-clay/15 text-vb-clay hover:bg-vb-clay/25 transition-colors"
                  title="Stop"
                >
                  <Square className="h-5 w-5" />
                </button>
              </>
            )}
          </div>
        </div>

      </div>

      {/* Device Panel Modal */}
      {showDevicePanel && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-md border border-vb-border-subtle bg-vb-surface shadow-2xl">
            <div className="flex items-center justify-between border-b border-vb-border-subtle px-5 py-4">
              <h2 className="font-display text-lg font-light tracking-[-0.01em] text-vb-text">
                Connect Devices
              </h2>
              <button
                onClick={() => setShowDevicePanel(false)}
                className="text-vb-text-dim hover:text-vb-forest"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {!btState.isSupported ? (
              <div className="p-5">
                <div className="flex items-center gap-3 rounded-sm bg-vb-clay/10 border border-vb-clay/30 p-4">
                  <AlertTriangle className="h-5 w-5 text-vb-clay shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-vb-clay">
                      Bluetooth not available in this browser
                    </p>
                    <p className="text-xs text-vb-clay/70 mt-1">
                      Use <strong>Chrome</strong>, <strong>Edge</strong>, or
                      <strong> Brave</strong> on a Mac, PC, or Android.{" "}
                      <strong>iPhone and iPad aren&apos;t supported</strong>:
                      every iOS browser (including Chrome) runs on Safari&apos;s
                      engine, which doesn&apos;t have Web Bluetooth. Native iOS
                      app coming soon.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-vb-border-subtle">
                <DeviceRow
                  icon={<Heart className="h-5 w-5 text-vb-clay" />}
                  label="Heart Rate Monitor"
                  connected={btState.heartRate.connected}
                  name={btState.heartRate.name}
                  value={
                    btState.heartRate.value
                      ? `${btState.heartRate.value} bpm`
                      : undefined
                  }
                  onConnect={btActions.connectHeartRate}
                  onDisconnect={() => btActions.disconnectDevice("heartRate")}
                />
                <DeviceRow
                  icon={<Zap className="h-5 w-5 text-vb-forest" />}
                  label="Power Meter"
                  connected={btState.power.connected}
                  name={btState.power.name}
                  value={
                    btState.power.value
                      ? `${btState.power.value}W`
                      : undefined
                  }
                  onConnect={btActions.connectPower}
                  onDisconnect={() => btActions.disconnectDevice("power")}
                  fromTrainer={
                    btState.power.connected &&
                    !!btState.power.name?.includes("(power)")
                  }
                />
                <DeviceRow
                  icon={<Activity className="h-5 w-5 text-vb-forest" />}
                  label="Cadence Sensor"
                  description={
                    btState.trainer.connected &&
                    !btState.cadence.name?.includes("Cadence")
                      ? "Available from trainer"
                      : undefined
                  }
                  connected={btState.cadence.connected}
                  name={btState.cadence.name}
                  value={
                    btState.cadence.value
                      ? `${btState.cadence.value} rpm`
                      : undefined
                  }
                  onConnect={btActions.connectCadence}
                  onDisconnect={() => btActions.disconnectDevice("cadence")}
                  fromTrainer={
                    btState.cadence.connected &&
                    !!btState.cadence.name?.includes("(cadence)")
                  }
                />
                <DeviceRow
                  icon={<Gauge className="h-5 w-5 text-vb-forest" />}
                  label="Smart Trainer (ERG)"
                  description="Controls resistance automatically"
                  connected={btState.trainer.connected}
                  name={btState.trainer.name}
                  value={
                    btState.trainer.connected
                      ? btState.trainer.ergMode
                        ? "ERG Mode"
                        : "Connected"
                      : undefined
                  }
                  onConnect={btActions.connectTrainer}
                  onDisconnect={() => btActions.disconnectDevice("trainer")}
                />
              </div>
            )}

            <div className="border-t border-vb-border-subtle px-5 py-3">
              <button
                onClick={() => setShowDevicePanel(false)}
                className="w-full rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Stop Modal */}
      {showConfirmStop && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-md border border-vb-border-subtle bg-vb-surface p-6 shadow-2xl">
            <h3 className="font-display text-lg font-light tracking-[-0.01em] text-vb-text mb-2">
              End Workout?
            </h3>
            <p className="text-sm text-vb-text-dim mb-2">
              You&apos;ve recorded {buffer.getBuffer().length} seconds of data
              so far.
            </p>
            <p className="text-sm text-vb-text-dim mb-6">
              Save the ride, or discard and exit?
            </p>
            {saveError && (
              <div className="mb-4 rounded-sm border border-vb-clay/40 bg-vb-clay/10 px-3 py-2 text-xs text-vb-clay">
                Save failed: {saveError}. Your data is still buffered, try
                again.
              </div>
            )}
            <div className="flex flex-col gap-2">
              <button
                disabled={saving}
                onClick={async () => {
                  sessionActions.stop();
                  await btActions.stopTrainer();
                  await saveSession();
                  setShowConfirmStop(false);
                }}
                className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft transition-colors disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save ride & end"}
              </button>
              <button
                disabled={saving}
                onClick={() => {
                  setShowConfirmStop(false);
                  sessionActions.stop();
                  btActions.stopTrainer();
                  buffer.clear();
                  router.push(`/dashboard/training/${workoutId}`);
                }}
                className="rounded-sm border border-vb-clay/40 px-4 py-2 text-sm text-vb-clay hover:bg-vb-clay/10 transition-colors disabled:opacity-50"
              >
                Discard & end
              </button>
              <button
                disabled={saving}
                onClick={() => setShowConfirmStop(false)}
                className="rounded-sm border border-vb-border px-4 py-2 text-sm text-vb-text-dim hover:bg-vb-surface-raised transition-colors disabled:opacity-50"
              >
                Keep going
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Resume previous session prompt */}
      {resumePrompt && session.status === "idle" && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-md border border-vb-border-subtle bg-vb-surface p-6 shadow-2xl">
            <h3 className="font-display text-lg font-light tracking-[-0.01em] text-vb-text mb-2">
              Unfinished session found
            </h3>
            <p className="text-sm text-vb-text-dim mb-2">
              You have a buffered session for this workout from{" "}
              {new Date(resumePrompt.startedAt).toLocaleString()} with{" "}
              {resumePrompt.dataPointCount} seconds of data.
            </p>
            <p className="text-sm text-vb-text-dim mb-6">
              Save what you recorded, or discard and start fresh?
            </p>
            {saveError && (
              <div className="mb-4 rounded-sm border border-vb-clay/40 bg-vb-clay/10 px-3 py-2 text-xs text-vb-clay">
                Save failed: {saveError}
              </div>
            )}
            <div className="flex flex-col gap-2">
              <button
                disabled={saving}
                onClick={async () => {
                  buffer.restore();
                  await saveSession();
                  setResumePrompt(null);
                }}
                className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft transition-colors disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save buffered ride"}
              </button>
              <button
                disabled={saving}
                onClick={() => {
                  buffer.clear();
                  setResumePrompt(null);
                }}
                className="rounded-sm border border-vb-clay/40 px-4 py-2 text-sm text-vb-clay hover:bg-vb-clay/10 transition-colors disabled:opacity-50"
              >
                Discard & start fresh
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// === Sub-Components ===

function DeviceRow({
  icon,
  label,
  description,
  connected,
  name,
  value,
  onConnect,
  onDisconnect,
  fromTrainer,
}: {
  icon: React.ReactNode;
  label: string;
  description?: string;
  connected: boolean;
  name: string | null;
  value?: string;
  onConnect: () => Promise<void>;
  onDisconnect: () => void;
  fromTrainer?: boolean;
}) {
  const [connecting, setConnecting] = useState(false);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      await onConnect();
    } catch (e) {
      console.error(`Failed to connect ${label}:`, e);
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="flex items-center gap-4 px-5 py-4">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-vb-sunken">
        {icon}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-vb-text">{label}</p>
        {connected && name ? (
          <p className="text-xs text-vb-forest">
            {name} {value && `· ${value}`}
          </p>
        ) : description ? (
          <p className="text-xs text-vb-text-muted">{description}</p>
        ) : null}
      </div>
      {connected ? (
        fromTrainer ? (
          <span className="rounded-sm bg-vb-sage-tint px-3 py-1.5 text-xs font-medium text-vb-forest">
            Via Trainer
          </span>
        ) : (
          <button
            onClick={onDisconnect}
            className="rounded-sm border border-vb-border px-3 py-1.5 text-xs text-vb-text-dim hover:bg-vb-surface-raised transition-colors"
          >
            Disconnect
          </button>
        )
      ) : (
        <button
          onClick={handleConnect}
          disabled={connecting}
          className="rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft transition-colors disabled:opacity-50"
        >
          {connecting ? "Scanning..." : "Connect"}
        </button>
      )}
    </div>
  );
}
