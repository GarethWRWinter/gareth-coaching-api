"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Count a number up from 0 on mount — the FORMA data-tile entrance.
 * Respects prefers-reduced-motion (renders the final value immediately).
 */
export function useCountUp(target: number, durationMs = 700): number {
  const [value, setValue] = useState(0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    // Skip the animation when it can't or shouldn't play: reduced motion,
    // or a hidden/backgrounded tab (rAF is paused there, which would leave
    // the tile stuck at 0 until the tab is fronted).
    if (
      typeof window !== "undefined" &&
      (window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
        document.visibilityState === "hidden")
    ) {
      setValue(target);
      return;
    }
    const start = performance.now();
    const from = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      setValue(from + (target - from) * eased);
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    // Safety net: if rAF stalls (tab hidden mid-animation, throttled
    // renderer), land on the real value once the duration has passed.
    const settle = window.setTimeout(() => setValue(target), durationMs + 100);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
      window.clearTimeout(settle);
    };
  }, [target, durationMs]);

  return value;
}
