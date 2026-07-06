"use client";

import { useCallback, useEffect, useRef } from "react";
import type { BluetoothState } from "@/hooks/useBluetooth";
import type { RideDataPoint } from "@/lib/api";

/**
 * Telemetry buffer for in-app indoor sessions.
 *
 * Samples live BLE state at 1Hz (one data point per second of session-elapsed time)
 * while the session is running, into an in-memory buffer. Persists the buffer
 * to localStorage every PERSIST_INTERVAL_MS so a tab refresh / crash doesn't
 * lose the ride.
 *
 * Buffer shape matches the backend `RideRecordRequest.data_points` schema —
 * post directly via `rides.record(...)` on session complete.
 */

export const SESSION_BUFFER_PREFIX = "forma:session-buffer:";
/** Pre-rebrand key — read once for migration, never written. */
const LEGACY_PREFIX = "marco:session-buffer:";
const PERSIST_INTERVAL_MS = 5000;

export interface BufferedSession {
  workoutId: string;
  startedAt: string; // ISO
  lastUpdatedAt: string; // ISO
  dataPoints: RideDataPoint[];
}

export interface TelemetryBufferActions {
  /** Reset and start a fresh buffer. Called when the session begins. */
  start: () => void;
  /** Force a final persist to localStorage. Called when the session ends. */
  flush: () => void;
  /** Wipe the buffer + localStorage entry. Called after a successful save or discard. */
  clear: () => void;
  /** Snapshot of the current buffer (defensive copy). */
  getBuffer: () => RideDataPoint[];
  /** When the session was started, or null if never started. */
  getStartTime: () => Date | null;
  /** True if a buffered (unfinished) session for this workout exists in localStorage. */
  hasStored: () => boolean;
  /** Load a previously persisted buffer back into memory. Returns the loaded session, or null. */
  restore: () => BufferedSession | null;
}

interface UseTelemetryBufferArgs {
  workoutId: string;
  elapsedSeconds: number;
  btState: BluetoothState;
  running: boolean;
}

export function useTelemetryBuffer({
  workoutId,
  elapsedSeconds,
  btState,
  running,
}: UseTelemetryBufferArgs): TelemetryBufferActions {
  const buffer = useRef<RideDataPoint[]>([]);
  const startedAt = useRef<Date | null>(null);
  const lastSampledSecond = useRef<number>(-1);
  const persistTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  const storageKey = `${SESSION_BUFFER_PREFIX}${workoutId}`;
  const legacyKey = `${LEGACY_PREFIX}${workoutId}`;

  const persist = useCallback(() => {
    if (!startedAt.current) return;
    if (typeof window === "undefined") return;
    if (buffer.current.length === 0) return;
    try {
      const payload: BufferedSession = {
        workoutId,
        startedAt: startedAt.current.toISOString(),
        lastUpdatedAt: new Date().toISOString(),
        dataPoints: buffer.current,
      };
      window.localStorage.setItem(storageKey, JSON.stringify(payload));
    } catch (e) {
      // localStorage full / disabled / quota exceeded — non-fatal, keep recording in memory
      console.warn("Failed to persist telemetry buffer:", e);
    }
  }, [storageKey, workoutId]);

  // Sample one data point per elapsed-second tick, while running.
  // The session hook ticks elapsedSeconds at 1Hz when status === running, so
  // this effect fires once per session-second naturally — no separate timer needed.
  useEffect(() => {
    if (!running) return;
    if (elapsedSeconds <= 0) return;
    if (elapsedSeconds === lastSampledSecond.current) return;

    if (!startedAt.current) {
      // Session started running but we never saw a `start()` call — initialise lazily.
      startedAt.current = new Date();
    }

    lastSampledSecond.current = elapsedSeconds;
    buffer.current.push({
      elapsed_seconds: elapsedSeconds,
      power: btState.power.value ?? null,
      heart_rate: btState.heartRate.value ?? null,
      cadence: btState.cadence.value ?? null,
      speed: null,
      distance: null,
      altitude: null,
    });
  }, [
    running,
    elapsedSeconds,
    btState.power.value,
    btState.heartRate.value,
    btState.cadence.value,
  ]);

  // Periodic persistence to localStorage while running.
  useEffect(() => {
    if (!running) {
      if (persistTimer.current) {
        clearInterval(persistTimer.current);
        persistTimer.current = null;
      }
      return;
    }
    persistTimer.current = setInterval(persist, PERSIST_INTERVAL_MS);
    return () => {
      if (persistTimer.current) {
        clearInterval(persistTimer.current);
        persistTimer.current = null;
      }
    };
  }, [running, persist]);

  const start = useCallback(() => {
    buffer.current = [];
    startedAt.current = new Date();
    lastSampledSecond.current = -1;
  }, []);

  const flush = useCallback(() => {
    persist();
  }, [persist]);

  const clear = useCallback(() => {
    buffer.current = [];
    startedAt.current = null;
    lastSampledSecond.current = -1;
    if (typeof window !== "undefined") {
      try {
        window.localStorage.removeItem(storageKey);
        window.localStorage.removeItem(legacyKey);
      } catch {
        // ignore
      }
    }
  }, [storageKey, legacyKey]);

  const getBuffer = useCallback(() => buffer.current.slice(), []);

  const getStartTime = useCallback(() => startedAt.current, []);

  const hasStored = useCallback(() => {
    if (typeof window === "undefined") return false;
    try {
      return (
        window.localStorage.getItem(storageKey) !== null ||
        window.localStorage.getItem(legacyKey) !== null
      );
    } catch {
      return false;
    }
  }, [storageKey, legacyKey]);

  const restore = useCallback((): BufferedSession | null => {
    if (typeof window === "undefined") return null;
    try {
      let raw = window.localStorage.getItem(storageKey);
      if (!raw) {
        // Migrate a pre-rebrand buffer forward, once.
        raw = window.localStorage.getItem(legacyKey);
        if (raw) {
          window.localStorage.setItem(storageKey, raw);
          window.localStorage.removeItem(legacyKey);
        }
      }
      if (!raw) return null;
      const parsed = JSON.parse(raw) as BufferedSession;
      if (!Array.isArray(parsed.dataPoints)) return null;
      buffer.current = parsed.dataPoints;
      startedAt.current = new Date(parsed.startedAt);
      const last = parsed.dataPoints[parsed.dataPoints.length - 1];
      lastSampledSecond.current = last?.elapsed_seconds ?? -1;
      return parsed;
    } catch (e) {
      console.warn("Failed to restore telemetry buffer:", e);
      return null;
    }
  }, [storageKey, legacyKey]);

  return { start, flush, clear, getBuffer, getStartTime, hasStored, restore };
}
