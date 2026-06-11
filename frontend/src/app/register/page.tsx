"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(email, password, name || undefined);
      router.push("/onboarding");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-start justify-center bg-vb-bg px-6 pt-24">
      <div className="w-full max-w-md">
        {/* Masthead */}
        <div className="mb-12 border-b border-vb-border-subtle pb-6">
          <h1 className="font-display text-6xl font-light leading-none tracking-[-0.02em]">
            MARCO
          </h1>
          <p className="mt-3 text-[10px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
            Issue 47 · Sign Up
          </p>
        </div>

        {/* Header */}
        <div className="mb-8">
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-text-muted">
            Get started
          </p>
          <h2 className="font-display text-4xl font-light leading-[0.95] tracking-[-0.02em]">
            Meet the<br />
            coach.
          </h2>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-vb-text-dim">
            Sport science. Mindset. Memory across every ride. £19.99 a month.
            Free Strava account is all you need.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="border-l-[3px] border-vb-clay bg-vb-surface px-4 py-3 text-sm text-vb-text">
              {error}
            </div>
          )}

          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.12em] text-vb-text">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
              className="block h-11 w-full rounded-sm border border-vb-border bg-vb-surface px-3 font-sans text-sm text-vb-text placeholder:text-vb-text-muted focus:border-vb-forest focus:outline-none focus:ring-1 focus:ring-vb-forest"
              placeholder="Gareth Winter"
            />
          </div>

          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.12em] text-vb-text">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="block h-11 w-full rounded-sm border border-vb-border bg-vb-surface px-3 font-sans text-sm text-vb-text placeholder:text-vb-text-muted focus:border-vb-forest focus:outline-none focus:ring-1 focus:ring-vb-forest"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-[0.12em] text-vb-text">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                autoComplete="new-password"
                className="block h-11 w-full rounded-sm border border-vb-border bg-vb-surface px-3 pr-11 font-sans text-sm text-vb-text placeholder:text-vb-text-muted focus:border-vb-forest focus:outline-none focus:ring-1 focus:ring-vb-forest"
                placeholder="At least 6 characters"
              />
              <button
                type="button"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-vb-text-dim hover:text-vb-text"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group block w-full rounded-sm bg-vb-forest px-6 py-3.5 text-[13px] font-medium uppercase tracking-[0.08em] text-white transition-colors hover:bg-vb-forest-soft disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? "Creating account…" : "Create account →"}
          </button>
        </form>

        <p className="mt-10 border-t border-vb-border-subtle pt-6 text-sm text-vb-text-dim">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium uppercase tracking-[0.08em] text-vb-forest hover:text-vb-forest-soft"
          >
            Log in →
          </Link>
        </p>
      </div>
    </div>
  );
}
