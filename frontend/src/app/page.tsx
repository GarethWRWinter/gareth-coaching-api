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
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <Bike className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-white">Cycling Coach</span>
          </div>
          <div className="flex gap-3">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-300 hover:text-white"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* Hero section */}
        <section className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h1 className="text-5xl font-bold tracking-tight text-white">
            Train Smarter with{" "}
            <span className="text-blue-400">AI-Powered Coaching</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
            Upload your rides, track your fitness, generate periodized training
            plans, and get personalised advice from an AI coach that understands
            your data.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-6 py-3 text-base font-semibold text-white hover:bg-blue-500"
            >
              Start Free
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-slate-700 px-6 py-3 text-base font-semibold text-slate-300 hover:border-slate-500 hover:text-white"
            >
              Log In
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="border-t border-slate-800 bg-slate-900/50 py-20">
          <div className="mx-auto max-w-6xl px-6">
            <h2 className="text-center text-3xl font-bold text-white">
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
                  className="rounded-xl border border-slate-800 bg-slate-900 p-6"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/10">
                    <f.icon className="h-5 w-5 text-blue-400" />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-white">
                    {f.title}
                  </h3>
                  <p className="mt-2 text-sm text-slate-400">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
