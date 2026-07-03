/**
 * Coach personalisation — avatars and tones.
 * Avatar art: hand-drawn pen-sketch portraits (public/coaches/*.webp).
 */

export interface CoachAvatar {
  key: string;
  label: string;
  src: string;
}

export const COACH_AVATARS: CoachAvatar[] = [
  { key: "m1_climber", label: "The Climber", src: "/coaches/m1_climber.webp" },
  { key: "m2_sprinter", label: "The Sprinter", src: "/coaches/m2_sprinter.webp" },
  { key: "m3_tt", label: "The TT Specialist", src: "/coaches/m3_tt.webp" },
  { key: "m4_ds", label: "The Directeur", src: "/coaches/m4_ds.webp" },
  { key: "m5_allrounder", label: "The All-Rounder", src: "/coaches/m5_allrounder.webp" },
  { key: "f1_hardwoman", label: "The Hardwoman", src: "/coaches/f1_hardwoman.webp" },
  { key: "f2_sprinter", label: "The Sprinter", src: "/coaches/f2_sprinter.webp" },
  { key: "f3_climber", label: "The Climber", src: "/coaches/f3_climber.webp" },
  { key: "f4_professor", label: "The Professor", src: "/coaches/f4_professor.webp" },
  { key: "f5_endurance", label: "The Specialist", src: "/coaches/f5_endurance.webp" },
];

export function coachAvatarSrc(key: string | undefined | null): string {
  const found = COACH_AVATARS.find((a) => a.key === key);
  return (found ?? COACH_AVATARS[0]).src;
}

export interface CoachTone {
  key: string;
  label: string;
  description: string;
  sample: string;
}

export const COACH_TONES: CoachTone[] = [
  {
    key: "balanced",
    label: "Balanced",
    description: "Warm and direct in equal measure — the classic coach.",
    sample: "Solid week. Thursday's the session that matters — let's arrive fresh.",
  },
  {
    key: "empathetic",
    label: "Empathetic & nurturing",
    description: "Leads with feelings, celebrates generously, softens hard truths.",
    sample: "You've carried a heavy week and still showed up — I'm proud of you. Let's be kind to your legs today.",
  },
  {
    key: "stoic",
    label: "Stoic & calm",
    description: "Spare, steady, unflappable. Facts, then one action.",
    sample: "TSB is −27. The work is done. Rest today.",
  },
  {
    key: "direct",
    label: "Direct & no-nonsense",
    description: "Blunt, honest, zero fluff. Tough love, fairly applied.",
    sample: "You started too hard and paid for it. Cap the first 10 minutes at 250W. That's the whole fix.",
  },
  {
    key: "analytical",
    label: "Analytical & data-deep",
    description: "Numbers first, mechanisms explained, depth welcome.",
    sample: "Decoupling was 8.4% after 2,100kJ — fueling, not fitness. At 80g/hr I'd expect under 5%.",
  },
  {
    key: "playful",
    label: "Playful & witty",
    description: "Light, funny, banter-forward — serious training, unserious delivery.",
    sample: "Three PBs in one ride? Leave some watts for the rest of us. Easy spin tomorrow, hotshot.",
  },
];
