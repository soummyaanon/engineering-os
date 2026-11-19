// GET /s/<score code> and /r/<redteam code> (rewritten to /api/s?s=… / ?r=…)
// A page whose og:image is the card for those numbers, so the link previews itself on X, LinkedIn, Slack, iMessage.
import {
  COLORS, REDTEAM_CMD, SCORE_CMD, SITE, parseRedteam, parseScore, plural, redteamColor,
} from "./_share.js";

export const config = { runtime: "edge" };

const esc = (s) => String(s).replace(/[&<>"']/g, (ch) => `&#${ch.charCodeAt(0)};`);

function describe(s, r) {
  if (s) {
    const cats = s.cats.map((c) => `${c.name} ${c.pct}%`).join(" · ");
    const guards = s.rt ? ` Guards stopped ${s.rt.stopped}/${s.rt.attacks} attacks.` : "";
    return {
      title: `Coding agent setup: ${s.grade} (${s.score}/100)`,
      headline: `This coding agent setup scored <b style="color:${COLORS[s.grade[0]]}">${esc(s.grade)}</b> (${s.score}/100)`,
      desc: `${cats}.${guards} Grade yours in 5 seconds; nothing leaves your machine.`,
      img: `${SITE}/api/og?s=${s.code}`,
      primary: SCORE_CMD, primaryLabel: "Grade your setup", secondary: REDTEAM_CMD, secondaryLabel: "Attack-test your guards",
    };
  }
  const fa = r.falseAlarms ? plural(r.falseAlarms, "false alarm") : "no false alarms";
  return {
    title: `Coding agent guards: ${r.stopped}/${r.attacks} attacks stopped`,
    headline: `These guards stopped <b style="color:${redteamColor(r.stopped, r.attacks)}">${r.stopped}/${r.attacks}</b> attacks`,
    desc: `rm -rf ~, curl | sh, .env sent to a webhook, live keys in source… ${r.stopped}/${r.attacks} stopped, ${fa}. `
      + "Test yours: fake tool calls, nothing runs.",
    img: `${SITE}/api/og?r=${r.code}`,
    primary: REDTEAM_CMD, primaryLabel: "Attack-test your guards", secondary: SCORE_CMD, secondaryLabel: "Grade your whole setup",
  };
}

function page(d, url) {
  const cmd = (id, label, c) => `
    <p class="label">${esc(label)}</p>
    <div class="cmd"><code>${esc(c)}</code><button type="button" data-copy="${esc(c)}" id="${id}">Copy</button></div>`;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(d.title)}</title>
<meta name="description" content="${esc(d.desc)}">
<link rel="canonical" href="${esc(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Engineering OS">
<meta property="og:url" content="${esc(url)}">
<meta property="og:title" content="${esc(d.title)}">
<meta property="og:description" content="${esc(d.desc)}">
<meta property="og:image" content="${esc(d.img)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(d.title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(d.title)}">
<meta name="twitter:description" content="${esc(d.desc)}">
<meta name="twitter:image" content="${esc(d.img)}">
<style>
  :root { color-scheme: dark; --bg:#161618; --panel:#1c1c1f; --line:#2e2e33; --fg:#dcdcdf; --muted:#8a8a93; --accent:#a88bfa; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, sans-serif; }
  main { max-width: 860px; margin: 0 auto; padding: 40px 16px 64px; }
  .brand { color: var(--accent); text-decoration: none; font: 600 15px ui-monospace, SFMono-Regular, Menlo, monospace; }
  h1 { font-size: clamp(24px, 4.5vw, 34px); line-height: 1.2; margin: 18px 0 18px; letter-spacing: -0.01em; }
  img { width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--line); display: block; }
  .label { margin: 28px 0 8px; color: var(--muted); font-size: 14px; }
  .cmd { display: flex; gap: 8px; align-items: stretch; background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 6px 6px 6px 14px; }
  .cmd code { flex: 1; min-width: 0; overflow-x: auto; white-space: nowrap; align-self: center; font: 14px ui-monospace, SFMono-Regular, Menlo, monospace; }
  button { background: var(--accent); color: #161618; border: 0; border-radius: 7px; padding: 8px 14px; font-weight: 600; cursor: pointer; }
  button:focus-visible, a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .note { color: var(--muted); font-size: 14px; margin-top: 28px; }
  .note a { color: var(--fg); }
</style>
</head>
<body>
<main>
  <a class="brand" href="${SITE}">engineering os</a>
  <h1>${d.headline}</h1>
  <img src="${esc(d.img)}" width="1200" height="630" alt="${esc(d.title)}">
  ${cmd("c1", d.primaryLabel + " (read-only, nothing leaves your machine)", d.primary)}
  ${cmd("c2", d.secondaryLabel, d.secondary)}
  <p class="note">The numbers in this link were reported by whoever shared it; run the command to get your own.
  Python 3, no install. <a href="${SITE}">What is Engineering OS?</a> · <a href="https://github.com/soummyaanon/engineering-os">GitHub</a></p>
</main>
<script>
  for (const b of document.querySelectorAll("button[data-copy]")) {
    b.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = "Copied"; }
      catch { b.textContent = "Select it"; }
      setTimeout(() => (b.textContent = "Copy"), 1600);
    });
  }
</script>
</body>
</html>`;
}

export default function handler(req) {
  const u = new URL(req.url);
  const s = parseScore(u.searchParams.get("s"));
  const r = s ? null : parseRedteam(u.searchParams.get("r"));
  if (!s && !r) return Response.redirect(`${SITE}/#score`, 302);
  const url = `${SITE}/${s ? "s" : "r"}/${(s || r).code}`;
  return new Response(page(describe(s, r), url), {
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=86400" },
  });
}
