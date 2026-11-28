// node site/api/share.test.mjs  — parser bounds, page escaping, and PNG rendering (writes cards to $OUT if set).
import assert from "node:assert/strict";
import { writeFileSync } from "node:fs";
import { parseRedteam, parseScore } from "./_share.js";
import og from "./og.js";
import page from "./s.js";

const RT = "51-51-0-35-11.11.9.9.5.5.5.5.6.6.6.6.9.9";

// parser: valid
assert.equal(parseScore("97-100.100.90.100-51.51.0").grade, "A+");
assert.equal(parseScore("19-29.0.0.33").rt, null);
assert.equal(parseRedteam(RT).stopped, 51);
// parser: rejects junk, out-of-range and inconsistent codes
for (const bad of ["", "x", "101-1.1.1.1", "50-100.100.100.101", "50-1.1.1", "50-1.1.1.1-52.51.0", "50-1.1.1.1-0.0.0",
  "50-1.1.1.1<script>", "1-1-0-1-1.1.0.1.0.1.0.1.0.1.0.1.0.1", "51-51-0-35-11.11.9.9.5.5.5.5.6.6.6.6.9.8",
  "52-51-0-35-11.11.9.9.5.5.5.5.6.6.6.6.9.9", "51-51-36-35-11.11.9.9.5.5.5.5.6.6.6.6.9.9"]) {
  assert.equal(parseScore(bad) || parseRedteam(bad), null, bad);
}

// page: og tags, escaping, redirect on junk
const get = (path) => page(new Request("https://engineering-os-hazel.vercel.app" + path));
let res = await get("/api/s?s=97-100.100.90.100-51.51.0");
let html = await res.text();
assert.equal(res.status, 200);
assert.match(html, /<meta property="og:image" content="https:\/\/engineering-os-hazel\.vercel\.app\/api\/og\?s=97-100\.100\.90\.100-51\.51\.0">/);
assert.match(html, /summary_large_image/);
assert.match(html, /<title>Coding agent setup: A\+ \(97\/100\)<\/title>/);
res = await get("/api/s?r=" + RT);
assert.match(await res.text(), /These guards stopped/);
res = await get('/api/s?s=97-1.1.1.1"><script>alert(1)</script>');
assert.equal(res.status, 302);

// images
const out = process.env.OUT;
for (const [name, q] of [["score-a", "s=97-100.100.90.100-51.51.0"], ["score-f", "s=19-29.0.0.33-0.51.0"],
  ["redteam-full", "r=" + RT], ["redteam-old", "r=38-51-4-35-10.11.6.9.5.5.3.5.0.6.5.6.9.9"], ["fallback", "s=nope"]]) {
  const r = await og(new Request("https://x/api/og?" + q));
  assert.equal(r.status, 200, name);
  assert.equal(r.headers.get("content-type"), "image/png", name);
  const buf = Buffer.from(await r.arrayBuffer());
  assert.ok(buf.length > 10_000, name);
  if (out) writeFileSync(`${out}/${name}.png`, buf);
}
console.log("share: all checks passed");
