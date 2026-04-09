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
  Timer,
  X,
  Check,
  AlertTriangle,
  List,
  ChevronRight,
  Volume2,
  VolumeX,
  Radio,
} from "lucide-react";
import { training } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDuration, cn } from "@/lib/utils";
import { getZoneFromPct, getZoneColors, ZONE_COLORS } from "@/lib/trainingZones";
import { useBluetooth } from "@/hooks/useBluetooth";
import { useCoachRadio } from "@/hooks/useCoachRadio";
import {
  useTrainingSession,
  type SessionStep,
} from "@/hooks/useTrainingSession";

const STEP_COLORS: Record<string, string> = {
  warmup: "bg-green-500",
  steady_state: "bg-blue-500",
  interval_on: "bg-red-500",
  interval_off: "bg-slate-500",
  cooldown: "bg-cyan-500",
  free_ride: "bg-purple-500",
  ramp: "bg-yellow-500",
};

const STEP_BG_COLORS: Record<string, string> = {
  warmup: "bg-green-500/20",
  steady_state: "bg-blue-500/20",
  interval_on: "bg-red-500/20",
  interval_off: "bg-slate-500/20",
  cooldown: "bg-cyan-500/20",
  free_ride: "bg-purple-500/20",
  ramp: "bg-yellow-500/20",
};

const STEP_TEXT_COLORS: Record<string, string> = {
  warmup: "text-green-400",
  steady_state: "text-blue-400",
  interval_on: "text-red-400",
  interval_off: "text-slate-400",
  cooldown: "text-cyan-400",
  free_ride: "text-purple-400",
  ramp: "text-yellow-400",
};

const STEP_BORDER_COLORS: Record<string, string> = {
  warmup: "border-green-500/40",
  steady_state: "border-blue-500/40",
  interval_on: "border-red-500/40",
  interval_off: "border-slate-500/40",
  cooldown: "border-cyan-500/40",
  free_ride: "border-purple-500/40",
  ramp: "border-yellow-500/40",
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
      <div className="flex h-screen items-center justify-center bg-slate-950">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!workout || !workout.steps || workout.steps.length === 0) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-slate-950 text-slate-400">
        <p>Workout not found or has no steps</p>
        <Link
          href={`/dashboard/training/${workoutId}`}
          className="mt-4 text-blue-400"
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
    <div className="fixed inset-0 z-50 flex flex-col bg-slate-950">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
        <div className="flex items-center gap-4">
          {session.status === "idle" && (
            <Link
              href={`/dashboard/training/${workoutId}`}
              className="text-slate-400 hover:text-white"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
          )}
          <div>
            <h1 className="text-lg font-bold text-white">{workout.title}</h1>
            <p className="text-xs text-slate-400">{workout.description}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Step list toggle */}
          {isActive && (
            <button
              onClick={() => setShowStepList(!showStepList)}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
                showStepList
                  ? "bg-slate-700 text-white"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
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
                "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
                coach.muted
                  ? "bg-slate-800 text-slate-500 hover:bg-slate-700"
                  : "bg-blue-600/20 text-blue-400"
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
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
              connectedDeviceCount > 0
                ? "bg-blue-600/20 text-blue-400"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
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
              <p className="text-[10px] uppercase text-slate-500">Elapsed</p>
              <p className="font-mono text-white">
                {formatTime(session.totalElapsedSeconds)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] uppercase text-slate-500">Remaining</p>
              <p className="font-mono text-slate-400">
                {formatTime(totalRemaining)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Workout Progress Bar */}
      <div className="relative h-12 border-b border-slate-800 bg-slate-900">
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
                  "relative flex items-center justify-center border-r border-slate-800/50 transition-all",
                  isDone
                    ? `${getZoneColors(step.powerTargetPct).bgSolid} opacity-60`
                    : isActiveStep
                      ? `${getZoneColors(step.powerTargetPct).bg} ring-1 ring-inset ring-white/30`
                      : "bg-slate-900/50"
                )}
                style={{ width: `${widthPct}%`, minWidth: "2px" }}
              >
                {widthPct > 3 && (
                  <span
                    className={cn(
                      "text-[9px] font-medium truncate px-0.5",
                      isDone || isActiveStep ? "text-white" : "text-slate-600"
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
          <div className="w-72 border-r border-slate-800 bg-slate-900/30 overflow-y-auto">
            <div className="px-4 py-3 border-b border-slate-800">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Workout Steps
              </h3>
            </div>
            <div className="divide-y divide-slate-800/50">
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
                              ? "text-white"
                              : isDone
                                ? "text-slate-500"
                                : "text-slate-300"
                          )}
                        >
                          {step.stepType.replace("_", " ")}
                        </span>
                        {step.isInterval && (
                          <span className="text-[9px] text-slate-500">
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
                        <p className="text-[10px] text-slate-500 truncate">
                          {step.notes}
                        </p>
                      )}
                    </div>

                    <div className="text-right shrink-0">
                      <p
                        className={cn(
                          "text-xs font-medium tabular-nums",
                          isCurrentStep ? "text-white" : "text-slate-400"
                        )}
                      >
                        {targetW}W
                      </p>
                      <p className="text-[10px] text-slate-500 tabular-nums">
                        {formatTime(step.durationSeconds)}
                      </p>
                    </div>

                    {/* Current step indicator */}
                    {isCurrentStep && (
                      <ChevronRight className="h-3 w-3 text-white shrink-0" />
                    )}
                    {isDone && (
                      <Check className="h-3 w-3 text-slate-600 shrink-0" />
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
            <div className="flex items-center gap-3 rounded-lg bg-amber-900/20 border border-amber-500/30 px-5 py-3">
              <Pause className="h-5 w-5 text-amber-400 shrink-0" />
              <div>
                <p className="text-sm font-medium text-amber-400">
                  Auto-paused — no power detected
                </p>
                <p className="text-xs text-amber-400/60">
                  Start pedalling to resume automatically
                </p>
              </div>
            </div>
          )}

          {/* Auto-pause countdown */}
          {autoPauseCountdown !== null && session.status === "running" && (
            <div className="flex items-center gap-2 text-xs text-amber-400/60">
              <AlertTriangle className="h-3 w-3" />
              <span>
                No power — auto-pausing in {autoPauseCountdown}s
              </span>
            </div>
          )}

          {/* Current Step Info */}
          {session.status === "idle" && !deviceSetupDone ? (
            /* === Device Setup Screen === */
            <div className="w-full max-w-lg text-center">
              <h2 className="text-2xl font-bold text-white mb-1">
                {workout.title}
              </h2>
              <p className="text-slate-400 mb-8">
                {formatDuration(session.totalDurationSeconds)} &middot;{" "}
                {session.steps.length} steps
              </p>

              <div className="rounded-xl border border-slate-700 bg-slate-800/50 overflow-hidden mb-6">
                <div className="border-b border-slate-700 px-5 py-3">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Bluetooth className="h-4 w-4 text-blue-400" />
                    Connect Your Devices
                  </h3>
                </div>

                {!btState.isSupported ? (
                  <div className="p-5">
                    <div className="flex items-center gap-3 rounded-lg bg-amber-900/20 border border-amber-500/30 p-4">
                      <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
                      <div className="text-left">
                        <p className="text-sm font-medium text-amber-400">
                          Bluetooth Not Available
                        </p>
                        <p className="text-xs text-amber-400/70 mt-1">
                          Web Bluetooth requires Chrome or Edge. Safari and Firefox are not supported.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-700">
                    <DeviceRow
                      icon={<Zap className="h-5 w-5 text-yellow-400" />}
                      label="Power Meter"
                      connected={btState.power.connected}
                      name={btState.power.name}
                      value={btState.power.value ? `${btState.power.value}W` : undefined}
                      onConnect={btActions.connectPower}
                      onDisconnect={() => btActions.disconnectDevice("power")}
                    />
                    <DeviceRow
                      icon={<Heart className="h-5 w-5 text-red-400" />}
                      label="Heart Rate Monitor"
                      connected={btState.heartRate.connected}
                      name={btState.heartRate.name}
                      value={btState.heartRate.value ? `${btState.heartRate.value} bpm` : undefined}
                      onConnect={btActions.connectHeartRate}
                      onDisconnect={() => btActions.disconnectDevice("heartRate")}
                    />
                    <DeviceRow
                      icon={<Gauge className="h-5 w-5 text-green-400" />}
                      label="Smart Trainer (ERG)"
                      description="Controls resistance automatically"
                      connected={btState.trainer.connected}
                      name={btState.trainer.name}
                      value={btState.trainer.connected ? (btState.trainer.ergMode ? "ERG Mode" : "Connected") : undefined}
                      onConnect={btActions.connectTrainer}
                      onDisconnect={() => btActions.disconnectDevice("trainer")}
                    />
                    <DeviceRow
                      icon={<Activity className="h-5 w-5 text-cyan-400" />}
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
                className="flex items-center gap-2 rounded-full bg-blue-600 px-8 py-4 text-lg font-bold text-white hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/30 mx-auto"
              >
                <Play className="h-6 w-6" />
                {connectedDeviceCount > 0 ? "Continue to Start" : "Continue Without Devices"}
              </button>

              {connectedDeviceCount === 0 && btState.isSupported && (
                <p className="mt-3 text-xs text-slate-500">
                  Connect at least a power meter for the best experience
                </p>
              )}
            </div>
          ) : session.status === "idle" && deviceSetupDone ? (
            <div className="text-center">
              <p className="text-lg text-slate-400 mb-2">Ready to start</p>
              <h2 className="text-3xl font-bold text-white mb-1">
                {workout.title}
              </h2>
              <p className="text-slate-400 mb-2">
                {formatDuration(session.totalDurationSeconds)} &middot;{" "}
                {session.steps.length} steps
              </p>
              {connectedDeviceCount > 0 && (
                <p className="text-sm text-blue-400 mb-4">
                  <BluetoothConnected className="inline h-4 w-4 mr-1" />
                  {connectedDeviceCount} device{connectedDeviceCount > 1 ? "s" : ""} connected
                </p>
              )}
            </div>
          ) : session.status === "completed" ? (
            <div className="text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 mx-auto">
                <Check className="h-8 w-8 text-green-400" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Workout Complete!
              </h2>
              <p className="text-slate-400 mb-4">
                Total time: {formatTime(session.totalElapsedSeconds)}
              </p>
              {coach.currentMessage && (
                <div className="max-w-md mx-auto mb-6">
                  <div className="bg-slate-800/80 backdrop-blur rounded-xl px-6 py-3 border border-slate-700">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Radio className="h-3 w-3 text-blue-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-400">
                        Marco &mdash; Race Radio
                      </span>
                    </div>
                    <p className="text-sm text-slate-200 italic">
                      &ldquo;{coach.currentMessage}&rdquo;
                    </p>
                  </div>
                </div>
              )}
              <Link
                href={`/dashboard/training/${workoutId}`}
                className="mt-2 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-500 transition-colors"
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
                          "rounded-full px-2.5 py-1 text-xs font-bold",
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
                  <p className="mt-2 text-sm text-slate-400">
                    {currentStep.notes}
                  </p>
                )}
              </div>

              {/* Target Power - big display */}
              <div className="text-center">
                <p className="text-6xl font-bold text-white tabular-nums">
                  {session.currentTargetWatts}
                  <span className="text-2xl text-slate-400 ml-1">W</span>
                </p>
                <p className={cn(
                  "text-lg mt-1",
                  getZoneColors(currentStep.powerTargetPct).text
                )}>
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

              {/* Coach Message Overlay */}
              {coach.currentMessage && (
                <div className="animate-pulse w-full max-w-lg">
                  <div className="bg-slate-800/80 backdrop-blur rounded-xl px-6 py-3 border border-slate-700 text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <Radio className="h-3 w-3 text-blue-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-400">
                        Marco &mdash; Race Radio
                      </span>
                    </div>
                    <p className="text-sm text-slate-200 italic">
                      &ldquo;{coach.currentMessage}&rdquo;
                    </p>
                  </div>
                </div>
              )}

              {/* Next step preview */}
              {nextStep && (
                <div className="flex items-center gap-2 text-sm text-slate-500">
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
                className="flex items-center gap-2 rounded-full bg-blue-600 px-8 py-4 text-lg font-bold text-white hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/30"
              >
                <Play className="h-6 w-6" /> Start Workout
              </button>
            )}

            {session.status === "running" && (
              <>
                <button
                  onClick={sessionActions.prevStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600 transition-colors"
                  title="Previous Step / Restart"
                >
                  <SkipBack className="h-5 w-5" />
                </button>
                <button
                  onClick={sessionActions.pause}
                  className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600 transition-colors"
                  title="Pause"
                >
                  <Pause className="h-6 w-6" />
                </button>
                <button
                  onClick={sessionActions.skipStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600 transition-colors"
                  title="Skip Step"
                >
                  <SkipForward className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setShowConfirmStop(true)}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-red-900/50 text-red-400 hover:bg-red-900 transition-colors"
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
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600 transition-colors"
                  title="Previous Step / Restart"
                >
                  <SkipBack className="h-5 w-5" />
                </button>
                <button
                  onClick={() => {
                    sessionActions.resume();
                    setAutoPaused(false);
                  }}
                  className="flex items-center gap-2 rounded-full bg-blue-600 px-8 py-4 text-lg font-bold text-white hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/30"
                >
                  <Play className="h-6 w-6" /> Resume
                </button>
                <button
                  onClick={sessionActions.skipStep}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-700 text-white hover:bg-slate-600 transition-colors"
                  title="Skip Step"
                >
                  <SkipForward className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setShowConfirmStop(true)}
                  className="flex h-12 w-12 items-center justify-center rounded-full bg-red-900/50 text-red-400 hover:bg-red-900 transition-colors"
                  title="Stop"
                >
                  <Square className="h-5 w-5" />
                </button>
              </>
            )}
          </div>
        </div>

        {/* Right Sidebar: Live Metrics */}
        {isActive && (
          <div className="w-64 border-l border-slate-800 bg-slate-900/50 p-4 space-y-4 overflow-y-auto">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Live Metrics
            </h3>

            {/* Power */}
            <MetricCard
              icon={<Zap className="h-5 w-5 text-yellow-400" />}
              label="Power"
              value={livePower}
              unit="W"
              target={session.currentTargetWatts}
              color={
                livePower > 0
                  ? livePower > session.currentTargetWatts * 1.05
                    ? "text-red-400"
                    : livePower < session.currentTargetWatts * 0.95
                      ? "text-blue-400"
                      : "text-green-400"
                  : "text-slate-500"
              }
            />

            {/* Heart Rate */}
            <MetricCard
              icon={<Heart className="h-5 w-5 text-red-400" />}
              label="Heart Rate"
              value={liveHR}
              unit="bpm"
              color={liveHR > 0 ? "text-red-400" : "text-slate-500"}
            />

            {/* Cadence */}
            <MetricCard
              icon={<Activity className="h-5 w-5 text-cyan-400" />}
              label="Cadence"
              value={liveCadence}
              unit="rpm"
              target={session.currentCadenceTarget ?? undefined}
              color={liveCadence > 0 ? "text-cyan-400" : "text-slate-500"}
            />

            {/* ERG Mode Status */}
            {btState.trainer.connected && (
              <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
                <div className="flex items-center gap-2">
                  <Gauge className="h-4 w-4 text-green-400" />
                  <span className="text-xs font-medium text-green-400">
                    ERG Mode Active
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  Target: {session.currentTargetWatts}W
                </p>
                <p className="text-xs text-slate-500">
                  {btState.trainer.name}
                </p>
              </div>
            )}

            {/* Timer */}
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
              <div className="flex items-center gap-2 mb-2">
                <Timer className="h-4 w-4 text-slate-400" />
                <span className="text-xs font-medium text-slate-400">
                  Session Time
                </span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Elapsed</span>
                  <span className="font-mono text-white">
                    {formatTime(session.totalElapsedSeconds)}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Remaining</span>
                  <span className="font-mono text-slate-400">
                    {formatTime(totalRemaining)}
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-slate-700 mt-2">
                  <div
                    className="h-full rounded-full bg-blue-500 transition-all"
                    style={{ width: `${Math.min(100, workoutProgress)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Device Panel Modal */}
      {showDevicePanel && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-800 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700 px-5 py-4">
              <h2 className="text-lg font-semibold text-white">
                Connect Devices
              </h2>
              <button
                onClick={() => setShowDevicePanel(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {!btState.isSupported ? (
              <div className="p-5">
                <div className="flex items-center gap-3 rounded-lg bg-amber-900/20 border border-amber-500/30 p-4">
                  <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-amber-400">
                      Bluetooth Not Available
                    </p>
                    <p className="text-xs text-amber-400/70 mt-1">
                      Web Bluetooth requires Chrome or Edge browser. Safari and
                      Firefox are not supported.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-slate-700">
                <DeviceRow
                  icon={<Heart className="h-5 w-5 text-red-400" />}
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
                  icon={<Zap className="h-5 w-5 text-yellow-400" />}
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
                  icon={<Activity className="h-5 w-5 text-cyan-400" />}
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
                  icon={<Gauge className="h-5 w-5 text-green-400" />}
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

            <div className="border-t border-slate-700 px-5 py-3">
              <button
                onClick={() => setShowDevicePanel(false)}
                className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 transition-colors"
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
          <div className="w-full max-w-sm rounded-xl border border-slate-700 bg-slate-800 p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-2">
              End Workout?
            </h3>
            <p className="text-sm text-slate-400 mb-6">
              Are you sure you want to stop? Your progress will not be saved.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmStop(false)}
                className="flex-1 rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowConfirmStop(false);
                  sessionActions.stop();
                  btActions.stopTrainer();
                }}
                className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500 transition-colors"
              >
                End Workout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// === Sub-Components ===

function MetricCard({
  icon,
  label,
  value,
  unit,
  target,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  unit: string;
  target?: number;
  color?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs font-medium text-slate-400">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span
          className={cn("text-2xl font-bold tabular-nums", color || "text-white")}
        >
          {value || "--"}
        </span>
        <span className="text-xs text-slate-500">{unit}</span>
      </div>
      {target !== undefined && target > 0 && (
        <p className="text-[10px] text-slate-500 mt-0.5">
          Target: {target} {unit}
        </p>
      )}
    </div>
  );
}

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
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-700/50">
        {icon}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-white">{label}</p>
        {connected && name ? (
          <p className="text-xs text-green-400">
            {name} {value && `· ${value}`}
          </p>
        ) : description ? (
          <p className="text-xs text-slate-500">{description}</p>
        ) : null}
      </div>
      {connected ? (
        fromTrainer ? (
          <span className="rounded-lg bg-green-600/20 px-3 py-1.5 text-xs font-medium text-green-400">
            Via Trainer
          </span>
        ) : (
          <button
            onClick={onDisconnect}
            className="rounded-lg border border-slate-600 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-700 transition-colors"
          >
            Disconnect
          </button>
        )
      ) : (
        <button
          onClick={handleConnect}
          disabled={connecting}
          className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition-colors disabled:opacity-50"
        >
          {connecting ? "Scanning..." : "Connect"}
        </button>
      )}
    </div>
  );
}
