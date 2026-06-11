"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload } from "lucide-react";
import Link from "next/link";
import { useRef, useState } from "react";
import { rides } from "@/lib/api";
import { formatDate, formatDuration, formatPower, formatTSS } from "@/lib/utils";

export default function RidesPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [page, setPage] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["rides", page],
    queryFn: () => rides.list(page, 20),
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");
    try {
      await rides.upload(file);
      queryClient.invalidateQueries({ queryKey: ["rides"] });
      queryClient.invalidateQueries({ queryKey: ["fitness-summary"] });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload failed";
      setError(msg);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const totalPages = data ? Math.ceil(data.total / 20) : 0;

  return (
    <div className="space-y-10">
      {/* ============ MASTHEAD ============ */}
      <header className="flex items-end justify-between gap-6 border-b border-vb-border-subtle pb-5">
        <div>
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
            Archive
          </p>
          <h1 className="font-display text-5xl font-light leading-[1.04] tracking-[-0.02em] md:text-6xl">
            Rides
          </h1>
          <p className="mt-3 text-xs text-vb-text-muted">
            {data?.total ?? "—"} total · page {page}
            {totalPages > 0 && ` of ${totalPages}`}
          </p>
        </div>

        <div className="shrink-0">
          <input
            ref={fileInputRef}
            type="file"
            accept=".fit"
            onChange={handleUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-vb-forest-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Upload className="h-3.5 w-3.5" />
            {uploading ? "Uploading…" : "Upload FIT"}
          </button>
        </div>
      </header>

      {error && (
        <div className="rounded-md border border-vb-clay/40 border-l-[3px] border-l-vb-clay bg-vb-surface px-4 py-3 text-sm text-vb-text">
          {error}
        </div>
      )}

      {/* ============ RIDES LIST ============ */}
      {isLoading ? (
        <div className="rounded-md border border-vb-border-subtle px-5 py-10 text-center text-sm text-vb-text-dim">
          Loading rides…
        </div>
      ) : data?.rides.length === 0 ? (
        <div className="rounded-md border border-vb-border-subtle px-5 py-10 text-center text-sm text-vb-text-dim">
          No rides yet. Upload a FIT file or wait for the Strava backfill to catch up.
        </div>
      ) : (
        <>
          {/* Column rubric — visible on lg+ only, gives editorial structure */}
          <div className="hidden border-b border-vb-border-subtle pb-2 lg:grid lg:grid-cols-[1fr_90px_90px_90px_90px_70px_60px] lg:gap-6">
            <span className="text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Ride
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Time
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Distance
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              Avg
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              NP
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              TSS
            </span>
            <span className="text-right text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
              IF
            </span>
          </div>

          <ul>
            {data?.rides.map((ride, idx) => (
              <li
                key={ride.id}
                className={
                  idx > 0 ? "border-t border-vb-border-subtle" : undefined
                }
              >
                <Link
                  href={`/dashboard/rides/${ride.id}`}
                  className="block py-4 transition-colors hover:bg-vb-surface hover:px-3 hover:-mx-3 lg:grid lg:grid-cols-[1fr_90px_90px_90px_90px_70px_60px] lg:items-baseline lg:gap-6"
                >
                  {/* Title + rubric */}
                  <div className="min-w-0">
                    <p className="mb-0.5 text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
                      {formatDate(ride.ride_date)}
                      {ride.source === "strava" && " · Strava"}
                      {ride.source === "fit_upload" && " · Upload"}
                      {ride.source === "in_app" && " · In-app"}
                      {ride.source === "dropbox" && " · Dropbox"}
                    </p>
                    <p className="truncate font-sans text-base font-medium text-vb-text">
                      {ride.title}
                    </p>
                  </div>

                  {/* Compact numbers row — visible always, repositioned on lg */}
                  <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm tabular-nums text-vb-text lg:hidden">
                    {ride.duration_seconds != null && (
                      <NumWithLabel
                        n={formatDuration(ride.duration_seconds)}
                        label="Time"
                      />
                    )}
                    {ride.distance_meters != null && (
                      <NumWithLabel
                        n={`${(ride.distance_meters / 1000).toFixed(1)} km`}
                        label="Dist"
                      />
                    )}
                    {ride.normalized_power != null && (
                      <NumWithLabel
                        n={`${Math.round(ride.normalized_power)}W`}
                        label="NP"
                      />
                    )}
                    {ride.tss != null && (
                      <NumWithLabel n={Math.round(ride.tss)} label="TSS" />
                    )}
                  </div>

                  {/* Desktop columns */}
                  <span className="hidden text-right text-sm text-vb-text tabular-nums lg:inline">
                    {ride.duration_seconds
                      ? formatDuration(ride.duration_seconds)
                      : "—"}
                  </span>
                  <span className="hidden text-right text-sm text-vb-text tabular-nums lg:inline">
                    {ride.distance_meters
                      ? `${(ride.distance_meters / 1000).toFixed(1)} km`
                      : "—"}
                  </span>
                  <span className="hidden text-right text-sm text-vb-text tabular-nums lg:inline">
                    {ride.average_power
                      ? `${Math.round(ride.average_power)}`
                      : "—"}
                  </span>
                  <span className="hidden text-right text-sm text-vb-text tabular-nums lg:inline">
                    {ride.normalized_power
                      ? `${Math.round(ride.normalized_power)}`
                      : "—"}
                  </span>
                  <span className="hidden text-right text-sm font-medium text-vb-text tabular-nums lg:inline">
                    {ride.tss ? Math.round(ride.tss) : "—"}
                  </span>
                  <span className="hidden text-right text-sm text-vb-text tabular-nums lg:inline">
                    {ride.intensity_factor
                      ? ride.intensity_factor.toFixed(2)
                      : "—"}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}

      {/* ============ PAGINATION ============ */}
      {data && data.total > 20 && (
        <div className="flex items-center justify-between gap-4 border-t border-vb-border-subtle pt-5">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded-sm border border-vb-border px-4 py-2 text-sm font-medium text-vb-forest transition-colors hover:bg-vb-surface disabled:cursor-not-allowed disabled:border-vb-border-subtle disabled:text-vb-text-muted disabled:hover:bg-transparent"
          >
            ← Previous
          </button>
          <span className="text-xs text-vb-text-muted">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= data.total}
            className="rounded-sm border border-vb-border px-4 py-2 text-sm font-medium text-vb-forest transition-colors hover:bg-vb-surface disabled:cursor-not-allowed disabled:border-vb-border-subtle disabled:text-vb-text-muted disabled:hover:bg-transparent"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

// Small mobile-friendly "value + label" inline helper.
function NumWithLabel({ n, label }: { n: string | number; label: string }) {
  return (
    <span className="tabular-nums">
      {n}
      <span className="ml-0.5 text-[10px] uppercase tracking-[0.12em] text-vb-text-dim">
        {label}
      </span>
    </span>
  );
}
