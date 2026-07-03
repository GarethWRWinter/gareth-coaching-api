"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Bike, BarChart3, Brain, Calendar, Zap, Target } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen bg-vb-bg">
      {/* Hero */}
      <header className="border-b border-vb-border-subtle">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-vb-forest">
              <Bike className="h-5 w-5 text-white" />
            </div>
            <span className="font-display text-lg font-medium tracking-[0.18em] text-vb-text">MARCO</span>
          </div>
          <div className="flex gap-3">
            <Link
              href="/login"
              className="rounded-sm px-4 py-2 text-sm font-medium text-vb-text-dim hover:text-vb-text"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-sm bg-vb-forest px-4 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* Hero section */}
        <section className="mx-auto max-w-4xl px-6 py-24 text-center">
          <p className="mb-5 text-[11px] font-medium uppercase tracking-[0.16em] text-vb-forest">
            The coach who remembers
          </p>
          <h1 className="font-display text-5xl font-light tracking-[-0.02em] text-vb-text md:text-6xl">
            A coach who knows{" "}
            <span className="text-vb-forest">every ride you&apos;ve ever done.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-vb-text-dim">
            Marco builds your plan, rides every session with you, and remembers
            everything — your goals, your weaknesses, your breakthroughs, your
            life. The longer you ride together, the better he coaches you.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link
              href="/register"
              className="rounded-sm bg-vb-forest px-6 py-3 text-base font-medium text-white hover:bg-vb-forest-soft"
            >
              Start Free
            </Link>
            <Link
              href="/login"
              className="rounded-sm border border-vb-border px-6 py-3 text-base font-medium text-vb-forest hover:bg-vb-surface"
            >
              Log In
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="border-t border-vb-border-subtle bg-vb-surface py-20">
          <div className="mx-auto max-w-6xl px-6">
            <h2 className="text-center font-display text-3xl font-light tracking-[-0.02em] text-vb-text">
              Everything You Need to Level Up
            </h2>
            <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  icon: BarChart3,
                  title: "Performance Analytics",
                  desc: "Track CTL, ATL, TSB with a full Performance Management Chart. See your fitness trends over time.",
                },
                {
                  icon: Calendar,
                  title: "Periodized Training Plans",
                  desc: "Auto-generated plans with base, build, peak, and race phases. Traditional, polarized, or sweet spot.",
                },
                {
                  icon: Brain,
                  title: "AI Coach",
                  desc: "Chat with a coach that knows your FTP, fitness, goals, and training history. Get personalised advice.",
                },
                {
                  icon: Zap,
                  title: "Structured Workouts",
                  desc: "Ride structured workouts on your smart trainer. Export to Zwift (ZWO) or Garmin (FIT).",
                },
                {
                  icon: Target,
                  title: "Goal Tracking",
                  desc: "Set race goals with A/B/C priorities. Plans auto-structure to peak at the right time.",
                },
                {
                  icon: Bike,
                  title: "Ride Analysis",
                  desc: "Upload FIT files or sync from Strava. Full power, HR, cadence analysis with NP, IF, TSS.",
                },
              ].map((f) => (
                <div
                  key={f.title}
                  className="rounded-md border border-vb-border-subtle bg-vb-surface p-6"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-sm bg-vb-sage-tint">
                    <f.icon className="h-5 w-5 text-vb-forest" />
                  </div>
                  <h3 className="mt-4 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
                    {f.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-vb-text-dim">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
