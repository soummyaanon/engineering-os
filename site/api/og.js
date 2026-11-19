// GET /api/og?s=<score code> | ?r=<redteam code>  →  1200×630 PNG preview card (cached forever: the URL is the content).
import { ImageResponse } from "@vercel/og";
import {
  COLORS, REDTEAM_CMD, SCORE_CMD, parseRedteam, parseScore, plural, redteamColor,
} from "./_share.js";

export const config = { runtime: "edge" };

const FONT = (w) => `https://cdn.jsdelivr.net/fontsource/fonts/jetbrains-mono@5.2.8/latin-${w}-normal.ttf`;
let fontsPromise;
function loadFonts() {
  fontsPromise ??= Promise.all([400, 700].map(async (weight) => {
    const r = await fetch(FONT(weight));
    if (!r.ok) throw new Error(`font ${weight}: ${r.status}`);
    return { name: "JetBrains Mono", data: await r.arrayBuffer(), weight, style: "normal" };
  })).catch(() => (fontsPromise = undefined)); // fall back to the built-in font, retry next request
  return fontsPromise;
}

// tiny element builder so this file needs no JSX build step
const h = (style, ...children) => ({ type: "div", props: { style: { display: "flex", ...style }, children } });
const text = (style, s) => h(style, String(s));

const MUTED = "#6f6f78";
const FG = "#dcdcdf";

function frame(title, left, right, footer) {
  return h({ width: 1200, height: 630, background: "#161618", padding: 24, fontFamily: "JetBrains Mono" },
    h({ flex: 1, flexDirection: "column", justifyContent: "space-between", background: "#1c1c1f",
      border: "2px solid #2e2e33", borderRadius: 14, padding: "44px 48px 36px" },
      h({ justifyContent: "space-between", alignItems: "center" },
        text({ fontSize: 26, color: MUTED }, title),
        text({ fontSize: 24, color: "#a88bfa" }, "engineering os")),
      h({ justifyContent: "space-between", alignItems: "center" }, left, right),
      text({ fontSize: 21, color: MUTED }, footer)));
}

function bars(rows, color, width = 500) {
  return h({ flexDirection: "column", width, gap: 18 },
    ...rows.map(({ label, value, frac }) => h({ flexDirection: "column", gap: 9 },
      h({ justifyContent: "space-between" },
        text({ fontSize: 22, color: FG }, label),
        text({ fontSize: 22, color: MUTED }, value)),
      h({ height: 10, borderRadius: 5, background: "#26262a" },
        h({ width: Math.round(width * frac), height: 10, borderRadius: 5, background: color })))));
}

function scoreCard(s) {
  const color = COLORS[s.grade[0]];
  const left = h({ flexDirection: "column" },
    text({ fontSize: 220, fontWeight: 700, color, lineHeight: 1 }, s.grade),
    text({ fontSize: 44, fontWeight: 700, color: FG, marginTop: 12 }, `${s.score}/100`),
    ...(s.rt ? [text({ fontSize: 24, color: redteamColor(s.rt.stopped, s.rt.attacks), marginTop: 14 },
      `guards stopped ${s.rt.stopped}/${s.rt.attacks} attacks`)] : []));
  const right = bars(s.cats.map((c) => ({ label: c.name, value: `${c.pct}%`, frac: c.pct / 100 })), color, 520);
  return frame("my coding agent setup", left, right, `score yours: ${SCORE_CMD}`);
}

function redteamCard(r) {
  const color = redteamColor(r.stopped, r.attacks);
  const left = h({ flexDirection: "column" },
    text({ fontSize: 140, fontWeight: 700, color, lineHeight: 1 }, `${r.stopped}/${r.attacks}`),
    text({ fontSize: 36, fontWeight: 700, color: FG, marginTop: 16 }, "attacks stopped"),
    text({ fontSize: 27, color: r.falseAlarms ? COLORS.C : COLORS.A, marginTop: 22 },
      r.falseAlarms ? plural(r.falseAlarms, "false alarm") : "no false alarms"),
    text({ fontSize: 22, color: MUTED, marginTop: 6 }, `on ${r.everyday} everyday commands`));
  const right = h({ flexDirection: "column", gap: 0 },
    bars(r.cats.map((c) => ({ label: c.name, value: `${c.stopped}/${c.total}`, frac: c.stopped / c.total })), color, 480));
  return frame(`my coding agent's guards vs. ${r.attacks} attacks`, left, right,
    `test yours: ${REDTEAM_CMD.replace("curl -fsSL ", "curl ")}`);
}

function fallbackCard() {
  return frame("grade your coding agent setup",
    text({ fontSize: 64, fontWeight: 700, color: FG, width: 1000 }, "Lighthouse for coding agents"),
    h({}), `score yours: ${SCORE_CMD}`);
}

export default async function handler(req) {
  const q = new URL(req.url).searchParams;
  const s = parseScore(q.get("s"));
  const r = s ? null : parseRedteam(q.get("r"));
  const fonts = await loadFonts();
  return new ImageResponse(s ? scoreCard(s) : r ? redteamCard(r) : fallbackCard(), {
    width: 1200,
    height: 630,
    ...(fonts ? { fonts } : {}),
    headers: { "cache-control": s || r ? "public, max-age=31536000, immutable" : "public, max-age=3600" },
  });
}
