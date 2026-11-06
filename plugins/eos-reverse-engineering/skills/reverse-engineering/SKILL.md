---
name: reverse-engineering
description: Engineering OS reverse-engineering playbook — understanding systems you didn't build: unfamiliar or legacy codebases ("how does this repo work?"), undocumented web APIs and network traffic of your own or authorized apps, competitor product teardowns (UX, pricing, stack, funnels), file formats and protocols, compiled binaries/apps for interoperability or security research, and recreating a design or behavior from observation. Use whenever the user wants to figure out how something works from the outside in, map an unknown system, document an undocumented API, or "reverse engineer" anything — and for CTF/authorized security work.
---

# Reverse Engineering Playbook

Reverse engineering is disciplined observation: form a hypothesis about how the system works, find the cheapest experiment that could disprove it, record what you learn. The output is always a **written model** of the system (map, spec, or diagram) that someone else could use.

## 0. Scope check (always first, takes 10 seconds)

Ask yourself what the target is and whether the user is entitled to probe it:

- **Green** — their own code/apps/accounts, open-source software, public web pages and public marketing material, CTFs, files they own, interoperability with software they licensed, authorized pentest scope. Proceed.
- **Needs a word** — a third party's private API or app internals. Fine for understanding and interoperability with their own account and normal client behavior; note ToS considerations in one line and stay within normal-client behavior (no auth bypass, no rate-limit evasion, no scraping of other users' data).
- **Stop** — bypassing DRM/licensing, accessing accounts or data that aren't theirs, evading detection, attacking systems outside an authorized scope. Decline that part and offer the legitimate version.

## 1. Pick the track

| Target | Track |
|---|---|
| Unfamiliar codebase | §2 Codebase archaeology |
| Web app / API behavior | §3 Network & API |
| Competitor product / marketing | §4 Product teardown (+ `reverse-engineer-marketing`, `competitor-profiling`) |
| Wire protocol / file format | §5 Protocols & formats (+ `protocol-reverse-engineering`) |
| Compiled binary / mobile app | §6 Binaries |
| A UI or design to recreate | §7 Design recreation |

## 2. Codebase archaeology

1. **Inventory**: languages, size (`git ls-files | wc -l`, `tokei`/`cloc` if present), build files, entrypoints, CI config, Dockerfiles, env examples. These tell you how it *runs*, which is truth; docs tell you how someone hoped it runs.
2. **Trace one real request/flow end-to-end** — from entrypoint to persistence and back. Use LSP go-to-definition / grep for symbols. One complete trace teaches more than skimming fifty files.
3. **History**: `git log --stat --since=6.months`, `git shortlog -sn`, `git log -S '<symbol>'` for when/why something appeared; hotspots = files with most churn (`git log --format= --name-only | sort | uniq -c | sort -rn | head`).
4. **Run it** and run the tests; a failing test suite is information.
5. For big repos, fan out read-only exploration (Explore / `feature-dev:code-explorer` agents) per subsystem and merge the conclusions.
6. **Deliverable**: `ARCHITECTURE.md`-style map — components, data flow diagram (mermaid), key entrypoints with `file:line`, external dependencies, how to run/test/deploy, and a "dragons" list (surprising or fragile code). Offer to turn it into the project's CLAUDE.md.

## 3. Network & API (web apps)

1. Drive the app with Playwright (`playwright` plugin) and capture traffic: `browser_network_requests`, then `browser_network_request` for bodies. Or a HAR export / mitmproxy for native clients the user owns.
2. For each endpoint record: method, path, auth mechanism (cookie/bearer/signature), required headers, request schema, response schema, pagination, error shapes, rate-limit headers.
3. Look for an official or leaked-by-design spec first: `/openapi.json`, `/swagger`, `/.well-known/`, GraphQL introspection (only if enabled), the site's JS bundles' route tables, public SDKs.
4. Reproduce each call outside the browser (curl/httpie) with the minimal headers — this confirms you actually understand it.
5. **Deliverable**: an OpenAPI 3 spec or typed client (zod/pydantic schemas) + a short README of auth flow and gotchas.

## 4. Product teardown (competitors, public surface only)

Capture: positioning & ICP from homepage/pricing, pricing tiers and packaging, onboarding steps (sign up with the user's own account), activation moment, paywalls, emails received (timing + content), tech stack (Wappalyzer-style signals: headers, script tags, `__NEXT_DATA__`, CDN), SEO footprint (sitemap.xml, top pages), changelog cadence, reviews (G2/Reddit/HN) for pains. Screenshot each step. Deliverable: teardown doc with screenshots, a funnel diagram, "what they do better / where they're weak / what we should steal or avoid." Route deeper GTM conclusions to `eos-gtm:gtm-strategy`.

## 5. Protocols & file formats

Start with `file`, `xxd | head`, `strings -n 8`, entropy (compressed/encrypted?), magic numbers, and length-prefixed structures. Diff two samples that differ in one known field to locate it. Write a parser incrementally (Python `struct` / Kaitai Struct) with a test per discovered field. Deliverable: format spec + parser + sample round-trip test.

## 6. Binaries & apps (authorized/interop/CTF)

Static first: `file`, `otool -L` / `ldd`, `nm`, `strings`, `codesign -dvv` (macOS), class-dump/jadx for ObjC/Android, then Ghidra/radare2/IDA for control flow. Dynamic next in a sandbox/VM: `lldb`/`gdb`, `frida` for hooking, `dtrace`/`strace`, `fs_usage`. Keep a findings log with addresses and hypotheses. Never run unknown binaries on the host outside a sandbox. Deliverable: behavior summary, key functions with addresses, and (for interop) a spec of the interface.

## 7. Design recreation

Recreate *patterns and quality*, not a copy of someone else's brand: measure spacing, type scale, grid, color roles, motion timings (DevTools computed styles), and document them as tokens; then build original UI with those qualities via `eos-frontend:frontend-playbook`. Don't reproduce logos, trademarks, proprietary copy, or assets.

## Working method (all tracks)

- Keep a running `findings.md`: **Observed** (facts with evidence) vs **Inferred** (hypotheses, confidence) vs **Unknown**. Never present an inference as an observation.
- Prefer the cheapest experiment that could falsify the current hypothesis.
- End with the deliverable for the track plus "open questions" — what you couldn't determine and how one would find out.
