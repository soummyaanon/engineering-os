// Shared by /api/og (the preview image) and /api/s (the share page).
// A share link carries only numbers; nothing is stored server-side. Codes are validated strictly
// (digits, dots, dashes, bounded, internally consistent) before anything is rendered.

export const SITE = "https://engineering-os-hazel.vercel.app";
export const SCORE_CMD = "curl -fsSL engineering-os-hazel.vercel.app/score | python3 -";
export const REDTEAM_CMD = SCORE_CMD + " redteam";

const GRADES = [[95, "A+"], [90, "A"], [80, "B"], [70, "C"], [60, "D"], [0, "F"]];
export const COLORS = { A: "#5bb974", B: "#a88bfa", C: "#e0a53b", D: "#e5484d", F: "#e5484d" };
// same order as bin/eos_score.py
export const SCORE_CATS = ["Guardrails", "Working rules", "Skills", "Feedback loops"];
export const REDTEAM_CATS = [
  "Wipe your home dir or disk", "Destroy work or data", "Rewrite git history", "Run remote code unread",
  "Leak secrets off the machine", "Ship or change prod", "Write keys into source",
];

export const gradeFor = (score) => GRADES.find(([t]) => score >= t)[1];
export const redteamColor = (k, n) => (k === n ? COLORS.A : k >= 0.7 * n ? COLORS.C : COLORS.F);

const nums = (s) => s.split(".").map(Number);

// score code: <score>-<g>.<r>.<k>.<l>[-<stopped>.<attacks>.<falseAlarms>]   e.g. 97-100.100.90.100-51.51.0
export function parseScore(code) {
  const m = /^(\d{1,3})-(\d{1,3}(?:\.\d{1,3}){3})(?:-(\d{1,3}\.\d{1,3}\.\d{1,3}))?$/.exec(code || "");
  if (!m) return null;
  const score = Number(m[1]);
  const pcts = nums(m[2]);
  if (score > 100 || pcts.some((p) => p > 100)) return null;
  let rt = null;
  if (m[3]) {
    const [stopped, attacks, falseAlarms] = nums(m[3]);
    if (!attacks || stopped > attacks) return null;
    rt = { stopped, attacks, falseAlarms };
  }
  return { code, score, grade: gradeFor(score), cats: SCORE_CATS.map((name, i) => ({ name, pct: pcts[i] })), rt };
}

// redteam code: <stopped>-<attacks>-<falseAlarms>-<everyday>-<s1>.<t1>.….<s7>.<t7>   e.g. 51-51-0-35-11.11.9.9.…
export function parseRedteam(code) {
  const m = /^(\d{1,3})-(\d{1,3})-(\d{1,3})-(\d{1,3})-(\d{1,3}(?:\.\d{1,3}){13})$/.exec(code || "");
  if (!m) return null;
  const [stopped, attacks, falseAlarms, everyday] = m.slice(1, 5).map(Number);
  const pairs = nums(m[5]);
  const cats = REDTEAM_CATS.map((name, i) => ({ name, stopped: pairs[2 * i], total: pairs[2 * i + 1] }));
  const ok = attacks > 0 && stopped <= attacks && falseAlarms <= everyday
    && cats.every((c) => c.total > 0 && c.stopped <= c.total)
    && cats.reduce((a, c) => a + c.stopped, 0) === stopped && cats.reduce((a, c) => a + c.total, 0) === attacks;
  return ok ? { code, stopped, attacks, falseAlarms, everyday, cats } : null;
}

export const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
