"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { strava } from "@/lib/api";

/**
 * useStravaAutoSync — silently pull any new rides from Strava whenever the
 * app is opened or the tab regains focus.
 *
 * Behaviour:
 *  - Runs on mount (gated by a min-interval so we don't hammer the API on
 *    every re-render or quick navigation).
 *  - Also runs when the tab becomes visible again (`visibilitychange`) — this
 *    covers the common "I left the app open and just finished a ride" flow.
 *  - The min-interval (SYNC_INTERVAL_MS) is tracked via localStorage so it
 *    survives reloads and applies across tabs.
 *  - Skipped entirely if the user isn't authenticated or Strava isn't
 *    connected.
 *  - Non-blocking: errors are swallowed (logged to console) so a failed sync
 *    never breaks the dashboard.
 *  - Invalidates every query that depends on ride data on success.
 */

const LAST_SYNC_KEY = "strava:auto-sync:last";
const SYNC_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

interface UseStravaAutoSyncOptions {
  /** Only run the sync when true (e.g. after auth + user are loaded). */
  enabled?: boolean;
}

export function useStravaAutoSync({ enabled = true }: UseStravaAutoSyncOptions = {}) {
  const queryClient = useQueryClient();
  const [syncing, setSyncing] = useState(false);
  const [lastSyncedCount, setLastSyncedCount] = useState<number | null>(null);
  const inFlightRef = useRef(false);

  useEffect(() => {
    if (!enabled) return;
    if (typeof window === "undefined") return;

    let cancelled = false;

    const runSync = async (reason: "mount" | "visibility") => {
      // Guard against concurrent runs (React StrictMode, rapid visibility
      // events, etc.).
      if (inFlightRef.current) return;

      const lastSyncRaw = localStorage.getItem(LAST_SYNC_KEY);
      const lastSyncAt = lastSyncRaw ? parseInt(lastSyncRaw, 10) : 0;
      const fresh = Date.now() - lastSyncAt < SYNC_INTERVAL_MS;
      if (fresh) return;

      inFlightRef.current = true;

      try {
        // Check connection first — cheap GET that avoids calling sync on
        // users who haven't connected Strava yet.
        const status = await strava.getStatus();
        if (!status?.connected) return;

        if (cancelled) return;
        setSyncing(true);
        const result = await strava.sync();
        if (cancelled) return;

        localStorage.setItem(LAST_SYNC_KEY, Date.now().toString());
        setLastSyncedCount(result.synced ?? 0);

        // Invalidate every query that depends on ride data so the UI
        // refreshes automatically.
        if ((result.synced ?? 0) > 0) {
          queryClient.invalidateQueries({ queryKey: ["rides"] });
          queryClient.invalidateQueries({ queryKey: ["recent-rides"] });
          queryClient.invalidateQueries({ queryKey: ["fitness-summary"] });
          queryClient.invalidateQueries({ queryKey: ["fitness-summary-quick"] });
          queryClient.invalidateQueries({ queryKey: ["pmc"] });
          queryClient.invalidateQueries({ queryKey: ["weekly-load"] });
          queryClient.invalidateQueries({ queryKey: ["power-profile"] });
          queryClient.invalidateQueries({ queryKey: ["zones"] });
          queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
        }
      } catch (err) {
        // Swallow errors — auto-sync is best-effort. The user can still use
        // the manual "Sync Recent" button in settings if something goes wrong.
        console.debug(`Strava auto-sync (${reason}) failed:`, err);
      } finally {
        inFlightRef.current = false;
        if (!cancelled) setSyncing(false);
      }
    };

    // Initial sync on mount.
    runSync("mount");

    // Re-sync whenever the tab regains focus / becomes visible — catches the
    // "I left the app open and just finished a ride" case.
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        runSync("visibility");
      }
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      cancelled = true;
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [enabled, queryClient]);

  return { syncing, lastSyncedCount };
}
