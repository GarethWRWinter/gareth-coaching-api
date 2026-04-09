"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, Bike } from "lucide-react";
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
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Rides</h1>
          <p className="mt-1 text-sm text-slate-400">
            {data?.total ?? 0} total rides
          </p>
        </div>
        <div>
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
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            <Upload className="h-4 w-4" />
            {uploading ? "Uploading..." : "Upload FIT File"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Rides List */}
      <div className="-mx-4 overflow-x-auto sm:mx-0">
        <div className="min-w-[600px] overflow-hidden rounded-xl border border-slate-800 bg-slate-800/50 sm:min-w-0">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3">Ride</th>
              <th className="px-3 py-3">Duration</th>
              <th className="px-3 py-3">Distance</th>
              <th className="hidden px-3 py-3 md:table-cell">Avg Power</th>
              <th className="hidden px-3 py-3 md:table-cell">NP</th>
              <th className="px-3 py-3">TSS</th>
              <th className="hidden px-3 py-3 lg:table-cell">IF</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading && (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-sm text-slate-500">
                  Loading rides...
                </td>
              </tr>
            )}
            {data?.rides.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-sm text-slate-500">
                  No rides yet. Upload a FIT file to get started.
                </td>
              </tr>
            )}
            {data?.rides.map((ride) => (
              <tr key={ride.id} className="hover:bg-slate-800/50">
                <td className="px-5 py-3">
                  <Link
                    href={`/dashboard/rides/${ride.id}`}
                    className="block"
                  >
                    <p className="text-sm font-medium text-white hover:text-blue-400">
                      {ride.title}
                    </p>
                    <p className="text-xs text-slate-400">
                      {formatDate(ride.ride_date)}
                      {ride.source === "strava" && " \u00B7 Strava"}
                    </p>
                  </Link>
                </td>
                <td className="px-3 py-3 text-sm text-slate-300">
                  {ride.duration_seconds
                    ? formatDuration(ride.duration_seconds)
                    : "-"}
                </td>
                <td className="px-3 py-3 text-sm text-slate-300">
                  {ride.distance_meters
                    ? `${(ride.distance_meters / 1000).toFixed(1)} km`
                    : "-"}
                </td>
                <td className="hidden px-3 py-3 text-sm text-slate-300 md:table-cell">
                  {formatPower(ride.average_power)}
                </td>
                <td className="hidden px-3 py-3 text-sm text-slate-300 md:table-cell">
                  {formatPower(ride.normalized_power)}
                </td>
                <td className="px-3 py-3 text-sm font-medium text-white">
                  {formatTSS(ride.tss)}
                </td>
                <td className="hidden px-3 py-3 text-sm text-slate-300 lg:table-cell">
                  {ride.intensity_factor
                    ? ride.intensity_factor.toFixed(2)
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      </div>

      {/* Pagination */}
      {data && data.total > 20 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-slate-400">
            Page {page} of {Math.ceil(data.total / 20)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= data.total}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
