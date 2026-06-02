"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { RefreshCw, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/sidebar";
import { useAuth } from "@/lib/auth-context";
import { useStravaAutoSync } from "@/hooks/useStravaAutoSync";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  // Auto-sync Strava once per session (and at most every 15 minutes) so new
  // rides appear without the user having to click anything. Runs in the
  // background; any errors are swallowed inside the hook.
  const { syncing, lastSyncedCount, lastError } = useStravaAutoSync({
    enabled: !!user && !loading,
  });

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-slate-900 pt-14 md:pt-0">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 sm:py-6">
          {children}
        </div>
      </main>

      {/* Subtle auto-sync toast — appears in the corner while syncing,
          briefly after a successful sync that imported new rides, or
          (persistently) when auto-sync is failing so the user knows
          something is wrong. */}
      {(syncing || (lastSyncedCount != null && lastSyncedCount > 0) || lastError) && (
        <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/95 px-4 py-2 text-xs text-slate-200 shadow-lg backdrop-blur-sm">
          {syncing ? (
            <>
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-blue-400" />
              <span>Syncing Strava…</span>
            </>
          ) : lastError ? (
            <Link
              href="/dashboard/settings"
              className="flex items-center gap-2 text-amber-300 hover:text-amber-200"
              title={lastError}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Strava sync failed — open settings</span>
            </Link>
          ) : (
            <>
              <RefreshCw className="h-3.5 w-3.5 text-green-400" />
              <span>
                Imported {lastSyncedCount} new ride
                {lastSyncedCount === 1 ? "" : "s"}
              </span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
