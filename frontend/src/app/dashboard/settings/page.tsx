"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef } from "react";
import {
  Save,
  Link2,
  Unlink,
  RefreshCw,
  Plus,
  Trash2,
  FolderSync,
  HardDrive,
  Pencil,
  Upload,
  ExternalLink,
  MapPin,
  Mountain,
  X,
} from "lucide-react";
import { users, strava, dropbox, goals as goalsApi, metrics } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate, cn } from "@/lib/utils";
import type { GoalEvent, StravaStatus } from "@/lib/api";
import Link from "next/link";

const EVENT_TYPES = [
  { value: "road_race", label: "Road Race" },
  { value: "crit", label: "Criterium" },
  { value: "time_trial", label: "Time Trial" },
  { value: "gran_fondo", label: "Gran Fondo" },
  { value: "sportive", label: "Sportive" },
  { value: "gravel", label: "Gravel" },
  { value: "mtb", label: "MTB" },
  { value: "hill_climb", label: "Hill Climb" },
  { value: "stage_race", label: "Stage Race" },
  { value: "charity_ride", label: "Charity Ride" },
  { value: "century", label: "Century" },
];

const PRIORITIES = [
  { value: "a_race", label: "A Race (Primary)" },
  { value: "b_race", label: "B Race (Secondary)" },
  { value: "c_race", label: "C Race (Low Priority)" },
];

interface GoalFormData {
  event_name: string;
  event_date: string;
  event_type: string;
  priority: string;
  target_duration_minutes: string;
  notes: string;
  route_url: string;
}

const emptyGoalForm: GoalFormData = {
  event_name: "",
  event_date: "",
  event_type: "road_race",
  priority: "a_race",
  target_duration_minutes: "",
  notes: "",
  route_url: "",
};

function goalToFormData(goal: GoalEvent): GoalFormData {
  return {
    event_name: goal.event_name,
    event_date: goal.event_date,
    event_type: goal.event_type,
    priority: goal.priority,
    target_duration_minutes: goal.target_duration_minutes?.toString() || "",
    notes: goal.notes || "",
    route_url: goal.route_url || "",
  };
}

function formatDurationMinutes(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h > 0) return m > 0 ? `${h}h ${m}m` : `${h}h`;
  return `${m}m`;
}

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const queryClient = useQueryClient();
  const gpxInputRef = useRef<HTMLInputElement>(null);

  // Profile form state
  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    weight_kg: user?.weight_kg?.toString() || "",
    height_cm: user?.height_cm?.toString() || "",
    ftp: user?.ftp?.toString() || "",
    max_hr: user?.max_hr?.toString() || "",
    resting_hr: user?.resting_hr?.toString() || "",
    weekly_hours_available: user?.weekly_hours_available?.toString() || "",
    preferred_hard_days: user?.preferred_hard_days ?? [],
    rest_days: user?.rest_days ?? [],
  });
  const [saved, setSaved] = useState(false);

  // Goals state
  const [showGoalForm, setShowGoalForm] = useState(false);
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null);
  const [goalForm, setGoalForm] = useState<GoalFormData>(emptyGoalForm);
  const [gpxUploadingId, setGpxUploadingId] = useState<string | null>(null);

  // FTP test state
  const [ftpTestPower, setFtpTestPower] = useState("");
  const [ftpResult, setFtpResult] = useState<string | null>(null);

  // Dropbox folder edit state
  const [editingFolder, setEditingFolder] = useState(false);
  const [folderPath, setFolderPath] = useState("");

  // Queries
  const { data: stravaStatus } = useQuery({
    queryKey: ["strava-status"],
    queryFn: () => strava.getStatus(),
    refetchInterval: (query) => {
      const data = query.state.data as StravaStatus | undefined;
      const status = data?.backfill?.status;
      // Poll fast while actively running, slow while paused (long waits)
      if (status === "running") return 3000;
      if (status === "paused") return 30_000; // 30s while in 15-min pause
      if (status === "paused_daily") return 5 * 60_000; // 5min while in daily pause
      return false;
    },
  });

  const { data: dropboxStatus } = useQuery({
    queryKey: ["dropbox-status"],
    queryFn: () => dropbox.getStatus(),
  });

  const { data: goalsData } = useQuery({
    queryKey: ["goals"],
    queryFn: () => goalsApi.list(),
  });

  // Mutations
  const saveProfile = useMutation({
    mutationFn: () => {
      const data: Record<string, string | number | boolean | number[]> = {};
      if (form.full_name) data.full_name = form.full_name;
      if (form.weight_kg) data.weight_kg = parseFloat(form.weight_kg);
      if (form.height_cm) data.height_cm = parseFloat(form.height_cm);
      if (form.ftp) data.ftp = parseInt(form.ftp);
      if (form.max_hr) data.max_hr = parseInt(form.max_hr);
      if (form.resting_hr) data.resting_hr = parseInt(form.resting_hr);
      if (form.weekly_hours_available)
        data.weekly_hours_available = parseFloat(form.weekly_hours_available);
      data.preferred_hard_days = form.preferred_hard_days;
      data.rest_days = form.rest_days;
      return users.updateProfile(data);
    },
    onSuccess: () => {
      refreshUser();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  const saveGoal = useMutation({
    mutationFn: () => {
      const data: Record<string, unknown> = {
        event_name: goalForm.event_name,
        event_date: goalForm.event_date,
        event_type: goalForm.event_type,
        priority: goalForm.priority,
      };
      if (goalForm.target_duration_minutes) {
        data.target_duration_minutes = parseInt(goalForm.target_duration_minutes);
      }
      if (goalForm.notes) data.notes = goalForm.notes;
      if (goalForm.route_url) data.route_url = goalForm.route_url;

      if (editingGoalId) {
        return goalsApi.update(editingGoalId, data as Parameters<typeof goalsApi.update>[1]);
      }
      return goalsApi.create(data as Parameters<typeof goalsApi.create>[0]);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setShowGoalForm(false);
      setEditingGoalId(null);
      setGoalForm(emptyGoalForm);
    },
  });

  const deleteGoal = useMutation({
    mutationFn: (id: string) => goalsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });

  const uploadGpx = useMutation({
    mutationFn: ({ goalId, file }: { goalId: string; file: File }) =>
      goalsApi.uploadGpx(goalId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
      setGpxUploadingId(null);
    },
    onError: () => {
      setGpxUploadingId(null);
    },
  });

  const submitFTPTest = useMutation({
    mutationFn: () => metrics.submitFTPTest(parseInt(ftpTestPower)),
    onSuccess: (data) => {
      setFtpResult(`New FTP: ${data.new_ftp}W`);
      refreshUser();
      setFtpTestPower("");
    },
  });

  const syncStrava = useMutation({
    mutationFn: () => strava.sync(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["rides"] });
      alert(`Synced ${data.synced} rides from Strava`);
    },
  });

  const syncDropbox = useMutation({
    mutationFn: () => dropbox.sync(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["rides"] });
      queryClient.invalidateQueries({ queryKey: ["dropbox-status"] });
      alert(`Synced ${data.synced} ride(s) from Dropbox`);
    },
  });

  const updateDropboxFolder = useMutation({
    mutationFn: (path: string) => dropbox.updateFolder(path),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dropbox-status"] });
      setEditingFolder(false);
    },
  });

  function openAddGoal() {
    setEditingGoalId(null);
    setGoalForm(emptyGoalForm);
    setShowGoalForm(true);
  }

  function openEditGoal(goal: GoalEvent) {
    setEditingGoalId(goal.id);
    setGoalForm(goalToFormData(goal));
    setShowGoalForm(true);
  }

  function handleGpxUpload(goalId: string, file: File) {
    setGpxUploadingId(goalId);
    uploadGpx.mutate({ goalId, file });
  }

  const inputClasses =
    "w-full rounded-sm border border-vb-border bg-vb-surface px-2.5 py-1.5 text-sm text-vb-text focus:border-vb-forest focus:outline-none";

  return (
    <div className="mx-auto max-w-3xl space-y-10">
      {/* ============ MASTHEAD ============ */}
      <header className="border-b border-vb-border-subtle pb-5">
        <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
          The desk
        </p>
        <h1 className="font-display text-5xl font-light leading-[1.04] tracking-[-0.02em] md:text-6xl">
          Settings.
        </h1>
      </header>

      {/* Profile */}
      <section className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
        <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">Profile</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Full Name
            </label>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Weight (kg)
            </label>
            <input
              type="number"
              step="0.1"
              value={form.weight_kg}
              onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              FTP (watts)
            </label>
            <input
              type="number"
              value={form.ftp}
              onChange={(e) => setForm({ ...form, ftp: e.target.value })}
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Max HR (bpm)
            </label>
            <input
              type="number"
              value={form.max_hr}
              onChange={(e) => setForm({ ...form, max_hr: e.target.value })}
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Resting HR (bpm)
            </label>
            <input
              type="number"
              value={form.resting_hr}
              onChange={(e) => setForm({ ...form, resting_hr: e.target.value })}
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Weekly Hours Available
            </label>
            <input
              type="number"
              step="0.5"
              value={form.weekly_hours_available}
              onChange={(e) =>
                setForm({ ...form, weekly_hours_available: e.target.value })
              }
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
        </div>

        {/* Training Schedule */}
        <div className="mt-6">
          <h3 className="mb-3 text-sm font-medium text-vb-text">Training Schedule</h3>
          <p className="mb-3 text-xs text-vb-text-dim">
            Select your hard training days (weekends, etc.) and rest days. Intensity sessions will be scheduled on hard days.
          </p>
          <div className="grid grid-cols-7 gap-2">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, idx) => {
              const isHard = form.preferred_hard_days.includes(idx);
              const isRest = form.rest_days.includes(idx);
              return (
                <div key={day} className="text-center">
                  <p className="mb-1.5 text-[10px] font-medium text-vb-text-muted">{day}</p>
                  <button
                    type="button"
                    onClick={() => {
                      if (isRest) {
                        // rest → hard
                        setForm({
                          ...form,
                          rest_days: form.rest_days.filter((d: number) => d !== idx),
                          preferred_hard_days: [...form.preferred_hard_days, idx],
                        });
                      } else if (isHard) {
                        // hard → normal
                        setForm({
                          ...form,
                          preferred_hard_days: form.preferred_hard_days.filter((d: number) => d !== idx),
                        });
                      } else {
                        // normal → rest
                        setForm({
                          ...form,
                          rest_days: [...form.rest_days, idx],
                        });
                      }
                    }}
                    className={cn(
                      "w-full rounded-sm py-2 text-xs font-medium transition-colors",
                      isHard
                        ? "bg-vb-clay/15 text-vb-clay border border-vb-clay/40"
                        : isRest
                          ? "bg-vb-sunken text-vb-text-muted border border-vb-border-subtle"
                          : "bg-vb-sage-tint text-vb-forest border border-vb-border-subtle"
                    )}
                  >
                    {isHard ? "Hard" : isRest ? "Rest" : "Easy"}
                  </button>
                </div>
              );
            })}
          </div>
          <p className="mt-2 text-[10px] text-vb-text-muted">
            Click to cycle: Easy → Rest → Hard. Hard days get intensity sessions (threshold, VO2max). Easy days get endurance/recovery.
          </p>
        </div>

        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={() => saveProfile.mutate()}
            disabled={saveProfile.isPending}
            className="flex items-center gap-2 rounded-sm border border-vb-forest bg-vb-forest px-4 py-2 text-[12px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Save className="h-4 w-4" />
            {saveProfile.isPending ? "Saving..." : "Save Profile"}
          </button>
          {saved && (
            <span className="text-sm text-vb-forest">Saved!</span>
          )}
        </div>
      </section>

      {/* FTP Test */}
      <section className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
        <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">FTP Test</h2>
        <p className="mt-2 text-sm text-vb-text-dim">
          Enter your 20-minute average power to calculate FTP (95% of 20-min avg)
        </p>
        <div className="mt-4 flex items-end gap-3">
          <div className="flex-1">
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              20-min Avg Power (W)
            </label>
            <input
              type="number"
              value={ftpTestPower}
              onChange={(e) => setFtpTestPower(e.target.value)}
              placeholder="e.g. 280"
              className="w-full rounded-sm border border-vb-border bg-vb-surface px-3 py-2 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
            />
          </div>
          <button
            onClick={() => submitFTPTest.mutate()}
            disabled={!ftpTestPower || submitFTPTest.isPending}
            className="rounded-sm border border-vb-forest bg-vb-forest px-4 py-2 text-[12px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            Calculate
          </button>
        </div>
        {ftpResult && (
          <p className="mt-2 text-sm font-medium text-vb-forest">
            {ftpResult}
          </p>
        )}
      </section>

      {/* Goals */}
      <section className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">Goal Events</h2>
            <p className="mt-0.5 text-xs text-vb-text-muted">
              <Link href="/dashboard/goals" className="font-medium uppercase tracking-[0.08em] text-vb-forest hover:text-vb-forest-soft">
                View full goals page
              </Link>
            </p>
          </div>
          <button
            onClick={openAddGoal}
            className="flex items-center gap-1.5 rounded-sm border border-vb-forest bg-vb-forest px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft"
          >
            <Plus className="h-3.5 w-3.5" /> Add Goal
          </button>
        </div>

        {/* Goal Form (Add / Edit) */}
        {showGoalForm && (
          <div className="mt-4 rounded-md border border-vb-border-subtle bg-vb-bg p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-medium text-vb-text">
                {editingGoalId ? "Edit Goal" : "New Goal"}
              </h3>
              <button
                onClick={() => {
                  setShowGoalForm(false);
                  setEditingGoalId(null);
                }}
                className="rounded-sm p-1 text-vb-text-muted hover:text-vb-text"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {/* Event Name */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Event Name *
                </label>
                <input
                  value={goalForm.event_name}
                  onChange={(e) =>
                    setGoalForm({ ...goalForm, event_name: e.target.value })
                  }
                  placeholder="e.g. Mallorca 312, Tour of Wessex"
                  className={inputClasses}
                />
              </div>

              {/* Date */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Event Date *
                </label>
                <input
                  type="date"
                  value={goalForm.event_date}
                  onChange={(e) =>
                    setGoalForm({ ...goalForm, event_date: e.target.value })
                  }
                  className={inputClasses}
                />
              </div>

              {/* Type */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Event Type
                </label>
                <select
                  value={goalForm.event_type}
                  onChange={(e) =>
                    setGoalForm({ ...goalForm, event_type: e.target.value })
                  }
                  className={inputClasses}
                >
                  {EVENT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Priority */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Priority
                </label>
                <select
                  value={goalForm.priority}
                  onChange={(e) =>
                    setGoalForm({ ...goalForm, priority: e.target.value })
                  }
                  className={inputClasses}
                >
                  {PRIORITIES.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Target Duration */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Target Duration (minutes)
                </label>
                <input
                  type="number"
                  value={goalForm.target_duration_minutes}
                  onChange={(e) =>
                    setGoalForm({
                      ...goalForm,
                      target_duration_minutes: e.target.value,
                    })
                  }
                  placeholder="e.g. 240 (4 hours)"
                  className={inputClasses}
                />
              </div>

              {/* Route URL */}
              <div>
                <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                  Route / Event URL
                </label>
                <input
                  type="url"
                  value={goalForm.route_url}
                  onChange={(e) =>
                    setGoalForm({ ...goalForm, route_url: e.target.value })
                  }
                  placeholder="https://strava.com/routes/... or event website"
                  className={inputClasses}
                />
              </div>
            </div>

            {/* Notes - full width */}
            <div className="mt-3">
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                Notes
              </label>
              <textarea
                value={goalForm.notes}
                onChange={(e) =>
                  setGoalForm({ ...goalForm, notes: e.target.value })
                }
                placeholder="Course details, goals, specific targets..."
                rows={3}
                className={`${inputClasses} resize-none`}
              />
            </div>

            <div className="mt-3 flex gap-2">
              <button
                onClick={() => saveGoal.mutate()}
                disabled={
                  !goalForm.event_name ||
                  !goalForm.event_date ||
                  saveGoal.isPending
                }
                className="rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
              >
                {saveGoal.isPending
                  ? "Saving..."
                  : editingGoalId
                    ? "Update Goal"
                    : "Save Goal"}
              </button>
              <button
                onClick={() => {
                  setShowGoalForm(false);
                  setEditingGoalId(null);
                }}
                className="rounded-sm border border-vb-border px-3 py-1.5 text-xs text-vb-text-dim hover:bg-vb-surface-raised"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Hidden GPX file input */}
        <input
          ref={gpxInputRef}
          type="file"
          accept=".gpx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file && gpxUploadingId) {
              handleGpxUpload(gpxUploadingId, file);
            }
            e.target.value = "";
          }}
        />

        {/* Goal List */}
        <div className="mt-4 divide-y divide-vb-border-subtle">
          {goalsData?.goals.length === 0 && (
            <p className="py-4 text-center text-sm text-vb-text-muted">
              No goals set. Add an event to start training with purpose.
            </p>
          )}
          {goalsData?.goals.map((goal) => (
            <div key={goal.id} className="py-3">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/dashboard/goals/${goal.id}`}
                    className="text-sm font-medium text-vb-text hover:text-vb-forest"
                  >
                    {goal.event_name}
                  </Link>
                  <p className="mt-0.5 text-xs text-vb-text-dim">
                    {formatDate(goal.event_date)} &middot;{" "}
                    <span className="capitalize">
                      {goal.event_type.replace(/_/g, " ")}
                    </span>{" "}
                    &middot;{" "}
                    <span className="capitalize">
                      {goal.priority.replace(/_/g, " ")}
                    </span>
                    {goal.target_duration_minutes && (
                      <span>
                        {" "}
                        &middot; {formatDurationMinutes(goal.target_duration_minutes)}
                      </span>
                    )}
                  </p>

                  {/* Route data */}
                  {goal.route_data && !goal.route_data.error && (
                    <p className="mt-0.5 flex items-center gap-1 text-xs text-vb-forest">
                      <MapPin className="h-3 w-3" />
                      {goal.route_data.total_distance_km &&
                        `${goal.route_data.total_distance_km}km`}
                      {goal.route_data.elevation_gain_m &&
                        ` \u00B7 ${goal.route_data.elevation_gain_m}m climbing`}
                      {(goal.route_data.title || goal.route_data.name) &&
                        ` \u00B7 ${goal.route_data.title || goal.route_data.name}`}
                    </p>
                  )}

                  {/* Route URL link */}
                  {goal.route_url && (
                    <a
                      href={goal.route_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-0.5 inline-flex items-center gap-1 text-xs text-vb-text-muted hover:text-vb-forest"
                    >
                      <ExternalLink className="h-3 w-3" />
                      Event link
                    </a>
                  )}

                  {/* GPX badge */}
                  {goal.gpx_file_path && (
                    <span className="ml-2 inline-flex items-center gap-1 text-xs text-vb-forest">
                      <Mountain className="h-3 w-3" />
                      GPX uploaded
                    </span>
                  )}

                  {/* Notes preview */}
                  {goal.notes && (
                    <p className="mt-1 text-xs text-vb-text-muted line-clamp-2">
                      {goal.notes}
                    </p>
                  )}
                </div>

                <div className="ml-3 flex shrink-0 items-center gap-1.5">
                  {goal.days_until != null && goal.days_until > 0 && (
                    <span className="rounded-full bg-vb-sage-tint px-2 py-0.5 text-xs text-vb-forest">
                      {goal.days_until}d
                    </span>
                  )}
                  {/* Upload GPX */}
                  <button
                    onClick={() => {
                      setGpxUploadingId(goal.id);
                      gpxInputRef.current?.click();
                    }}
                    disabled={uploadGpx.isPending && gpxUploadingId === goal.id}
                    className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-surface-raised hover:text-vb-forest"
                    title="Upload GPX file"
                  >
                    <Upload className="h-3.5 w-3.5" />
                  </button>
                  {/* Edit */}
                  <button
                    onClick={() => openEditGoal(goal)}
                    className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-surface-raised hover:text-vb-text"
                    title="Edit goal"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                  {/* Delete */}
                  <button
                    onClick={() => {
                      if (confirm(`Delete "${goal.event_name}"?`)) {
                        deleteGoal.mutate(goal.id);
                      }
                    }}
                    className="rounded-sm p-1.5 text-vb-text-muted hover:bg-vb-surface-raised hover:text-vb-clay"
                    title="Delete goal"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Strava Integration */}
      <section className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
        <h2 className="font-display text-2xl font-light tracking-[-0.01em] text-vb-text">Strava</h2>
        {stravaStatus?.connected ? (
          <div className="mt-3 space-y-3">
            <div className="flex items-center gap-2 text-sm text-vb-forest">
              <Link2 className="h-4 w-4" /> Connected (Athlete #
              {stravaStatus.athlete_id})
            </div>

            {/* Backfill Progress */}
            {stravaStatus.backfill?.status === "running" && (
              <div className="rounded-md border border-vb-border-subtle bg-vb-sage-tint p-3">
                <div className="flex items-center gap-2 text-sm font-medium text-vb-forest">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Importing ride history...
                </div>
                {stravaStatus.backfill.total ? (
                  <>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-vb-sunken">
                      <div
                        className="h-full rounded-full bg-vb-forest transition-all duration-500"
                        style={{
                          width: `${Math.round(
                            (stravaStatus.backfill.progress /
                              stravaStatus.backfill.total) *
                              100
                          )}%`,
                        }}
                      />
                    </div>
                    <p className="mt-1 text-xs text-vb-text-dim">
                      {stravaStatus.backfill.progress} / {stravaStatus.backfill.total} activities processed
                    </p>
                  </>
                ) : (
                  <p className="mt-1 text-xs text-vb-text-dim">
                    Scanning your Strava history...
                  </p>
                )}
              </div>
            )}

            {stravaStatus.backfill?.status === "completed" && (
              <div className="rounded-md border border-vb-border-subtle bg-vb-sage-tint p-3">
                <p className="text-sm text-vb-forest">
                  History import complete — {stravaStatus.backfill.total} activities processed
                </p>
                {stravaStatus.backfill.completed_at && (
                  <p className="mt-0.5 text-xs text-vb-text-muted">
                    Completed {formatDate(stravaStatus.backfill.completed_at)}
                  </p>
                )}
                <button
                  onClick={async () => {
                    await strava.startBackfill(true);
                    queryClient.invalidateQueries({ queryKey: ["strava-status"] });
                  }}
                  className="mt-2 rounded-sm border border-vb-border bg-vb-surface px-3 py-1 text-xs font-medium text-vb-forest hover:bg-vb-surface-raised"
                >
                  Re-import from Strava
                </button>
              </div>
            )}

            {stravaStatus.backfill?.status === "paused" && (
              <div className="rounded-md border border-vb-clay/30 bg-vb-clay/10 p-3">
                <div className="flex items-center gap-2 text-sm font-medium text-vb-clay">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Paused — waiting for Strava 15-min rate limit to reset
                </div>
                <p className="mt-1 text-xs text-vb-text-dim">
                  {stravaStatus.backfill.total
                    ? `${stravaStatus.backfill.progress} / ${stravaStatus.backfill.total} processed — resuming in ~15 minutes`
                    : "Resuming in ~15 minutes"}
                </p>
              </div>
            )}

            {stravaStatus.backfill?.status === "paused_daily" && (
              <div className="rounded-md border border-vb-clay/30 bg-vb-clay/10 p-3">
                <div className="flex items-center gap-2 text-sm font-medium text-vb-clay">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Paused — Strava daily limit reached
                </div>
                <p className="mt-1 text-xs text-vb-text-dim">
                  {stravaStatus.backfill.total
                    ? `${stravaStatus.backfill.progress} / ${stravaStatus.backfill.total} processed. Strava allows 1,000 requests/day — your backfill will auto-resume at midnight UTC.`
                    : "Strava allows 1,000 requests/day — your backfill will auto-resume at midnight UTC."}
                </p>
              </div>
            )}

            {stravaStatus.backfill?.status === "failed" && (
              <div className="rounded-md border border-vb-clay/30 bg-vb-clay/10 p-3">
                <p className="text-sm text-vb-clay">
                  History import failed — {stravaStatus.backfill.progress || 0} of{" "}
                  {stravaStatus.backfill.total || "?"} processed before error
                </p>
                <button
                  onClick={async () => {
                    await strava.startBackfill();
                    queryClient.invalidateQueries({ queryKey: ["strava-status"] });
                  }}
                  className="mt-2 rounded-sm bg-vb-clay px-3 py-1 text-xs font-medium text-white hover:opacity-90"
                >
                  Retry Import
                </button>
              </div>
            )}

            {!stravaStatus.backfill?.status && (
              <div className="rounded-md border border-vb-border-subtle bg-vb-bg p-3">
                <p className="text-sm text-vb-text-dim">
                  Import your full Strava history to give the coach maximum context.
                </p>
                <button
                  onClick={async () => {
                    await strava.startBackfill();
                    queryClient.invalidateQueries({ queryKey: ["strava-status"] });
                  }}
                  className="mt-2 flex items-center gap-1.5 rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Import Full History
                </button>
              </div>
            )}

            {stravaStatus.last_sync_at && (
              <p className="text-xs text-vb-text-muted">
                Last synced: {formatDate(stravaStatus.last_sync_at)}
              </p>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => syncStrava.mutate()}
                disabled={syncStrava.isPending}
                className="flex items-center gap-1.5 rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
              >
                <RefreshCw
                  className={`h-3.5 w-3.5 ${syncStrava.isPending ? "animate-spin" : ""}`}
                />
                {syncStrava.isPending ? "Syncing..." : "Sync Recent"}
              </button>
              <button
                onClick={async () => {
                  await strava.disconnect();
                  queryClient.invalidateQueries({
                    queryKey: ["strava-status"],
                  });
                }}
                className="flex items-center gap-1.5 rounded-sm border border-vb-clay px-3 py-1.5 text-xs text-vb-clay hover:bg-vb-clay/10"
              >
                <Unlink className="h-3.5 w-3.5" /> Disconnect
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-3">
            <p className="text-sm text-vb-text-dim">
              Connect Strava to automatically sync your rides and import your full training history.
            </p>
            <button
              onClick={async () => {
                const { auth_url } = await strava.getAuthUrl();
                window.location.href = auth_url;
              }}
              className="mt-3 flex items-center gap-2 rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft"
            >
              <Link2 className="h-4 w-4" /> Connect Strava
            </button>
          </div>
        )}
      </section>

      {/* Dropbox Integration */}
      <section className="rounded-md border border-vb-border-subtle bg-vb-surface p-6">
        <h2 className="flex items-center gap-2 font-display text-2xl font-light tracking-[-0.01em] text-vb-text">
          <HardDrive className="h-5 w-5 text-vb-forest" />
          Dropbox
        </h2>
        {dropboxStatus?.connected ? (
          <div className="mt-3 space-y-3">
            <div className="flex items-center gap-2 text-sm text-vb-forest">
              <Link2 className="h-4 w-4" /> Connected
              {dropboxStatus.account_id &&
                ` (${dropboxStatus.account_id})`}
            </div>

            {/* Folder path */}
            <div className="rounded-md border border-vb-border-subtle bg-vb-bg p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-vb-text-muted">
                    Sync Folder
                  </p>
                  {editingFolder ? (
                    <div className="mt-1 flex gap-2">
                      <input
                        value={folderPath}
                        onChange={(e) => setFolderPath(e.target.value)}
                        placeholder="/cycling"
                        className="rounded-sm border border-vb-border bg-vb-surface px-2 py-1 text-sm text-vb-text focus:border-vb-forest focus:outline-none"
                      />
                      <button
                        onClick={() =>
                          updateDropboxFolder.mutate(folderPath)
                        }
                        className="rounded-sm bg-vb-forest px-2 py-1 text-xs text-white hover:bg-vb-forest-soft"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingFolder(false)}
                        className="rounded-sm border border-vb-border px-2 py-1 text-xs text-vb-text-dim"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <p className="mt-0.5 flex items-center gap-1 text-sm text-vb-text">
                      <FolderSync className="h-3.5 w-3.5 text-vb-text-muted" />
                      {dropboxStatus.folder_path || "/cycling"}
                      <button
                        onClick={() => {
                          setFolderPath(
                            dropboxStatus.folder_path || "/cycling"
                          );
                          setEditingFolder(true);
                        }}
                        className="ml-2 text-xs text-vb-forest hover:text-vb-forest-soft"
                      >
                        Change
                      </button>
                    </p>
                  )}
                </div>
              </div>
              {dropboxStatus.last_sync_at && (
                <p className="mt-1 text-xs text-vb-text-muted">
                  Last synced: {formatDate(dropboxStatus.last_sync_at)}
                </p>
              )}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => syncDropbox.mutate()}
                disabled={syncDropbox.isPending}
                className="flex items-center gap-1.5 rounded-sm bg-vb-forest px-3 py-1.5 text-xs font-medium text-white hover:bg-vb-forest-soft disabled:opacity-50"
              >
                <RefreshCw
                  className={`h-3.5 w-3.5 ${syncDropbox.isPending ? "animate-spin" : ""}`}
                />
                {syncDropbox.isPending
                  ? "Syncing..."
                  : "Sync FIT Files"}
              </button>
              <button
                onClick={async () => {
                  await dropbox.disconnect();
                  queryClient.invalidateQueries({
                    queryKey: ["dropbox-status"],
                  });
                }}
                className="flex items-center gap-1.5 rounded-sm border border-vb-clay px-3 py-1.5 text-xs text-vb-clay hover:bg-vb-clay/10"
              >
                <Unlink className="h-3.5 w-3.5" /> Disconnect
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-3">
            <p className="text-sm text-vb-text-dim">
              Connect Dropbox to import FIT files from a folder. Drop your ride
              files into a Dropbox folder and sync them here.
            </p>
            <button
              onClick={async () => {
                const { auth_url } = await dropbox.getAuthUrl();
                window.location.href = auth_url;
              }}
              className="mt-3 flex items-center gap-2 rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft"
            >
              <HardDrive className="h-4 w-4" /> Connect Dropbox
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
