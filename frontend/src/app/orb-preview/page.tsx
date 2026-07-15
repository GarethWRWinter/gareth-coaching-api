"use client";

/**
 * TEMP preview route (no auth) — infinity-on-chalk banner lockup:
 * orb seated left on the chalk ground, full uncropped shadow, headline
 * overlaid on the right negative space (never touching the orb).
 * Delete once signed off.
 */

import { Kicker } from "@/components/ui/kicker";
import { SeatedBanner, ZoneChip } from "@/components/ui/seated-banner";
import { zoneFromIF } from "@/lib/zones";

export default function OrbPreviewPage() {
  const coach = "Forma";
  const zone = zoneFromIF(0.5);

  return (
    <div className="mx-auto max-w-5xl space-y-12 px-6 py-10">
      <header className="f-rise">
        <Kicker>Tuesday 8 July</Kicker>
        <h1 className="f-display mt-3 text-5xl leading-[1.04] md:text-6xl">
          Good afternoon, Gareth.
        </h1>
      </header>

      {/* NOTE */}
      <SeatedBanner src="/orbs/forma-rest-seated.webp">
        <Kicker flamme>A note from {coach}</Kicker>
        <p className="mt-3 max-w-md text-lg leading-relaxed text-vb-text">
          Rest day, Gareth. Your body builds fitness during recovery, not just
          during training. Enjoy the day off.
        </p>
        <p className="mt-4">
          <span className="f-signature text-2xl leading-none">{coach}</span>
          <span className="ml-2 text-xs text-vb-text-muted">your coach</span>
        </p>
      </SeatedBanner>

      {/* DEBRIEF */}
      <SeatedBanner src="/orbs/z1-rest-seated.webp">
        <ZoneChip color={zone.color}>
          {zone.name} · {zone.key.toUpperCase()}
        </ZoneChip>
        <h2 className="f-display mt-3 text-3xl leading-tight md:text-4xl">
          Morning Ride
        </h2>
        <p className="f-kicker mt-2 text-vb-text-muted">
          {coach}&apos;s debrief · 31 May 2026
        </p>
        <p className="mt-3 max-w-md text-[16px] leading-relaxed text-vb-text-dim">
          Nice work out there, Gareth. You logged 31 minutes for 14 TSS. Every
          ride counts toward your goal, so keep building.
        </p>
      </SeatedBanner>
    </div>
  );
}
