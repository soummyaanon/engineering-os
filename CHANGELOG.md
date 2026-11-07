# Changelog

Update any time with `eos update` (or re-run the install command). Claude Code tells you when a new version is out.

## 0.6.0 — 2026-11-08

**New: `eos redteam`.** Fires 51 attacks (wiping home, destroying data, rewriting git history, running remote scripts, leaking secrets off the machine, prod changes, keys written into source) and 35 everyday look-alikes at your guards. The calls are fake: your PreToolUse hooks and Bash permission rules judge them, and nothing is executed. Works on any setup, without installing anything: `curl -fsSL https://engineering-os-hazel.vercel.app/score | python3 - redteam`. `--all` lists every case, `--card` makes a shareable image, `--json` for CI.

**`eos score` now tests guards instead of checking that they exist.** Guardrail points are the share of redteam attacks stopped, scaled down by false alarms, since a guard that asks about everything gets clicked through. `--no-redteam` restores the old presence check.

**Guard fixes found by redteam.** The 0.5.0 bash guard stopped 38/51 with 4 false alarms. Now it stops 51/51 with none:
- `rm -rf $HOME`, `rm -rf ~/`, `rm -r -f ~` and `find ~ -delete` are blocked. `$HOME` used to be matched case-sensitively against lowercased text, so it never matched.
- `git branch -D` and `chmod -R 777` now ask. Their uppercase flags could never match before.
- New: sending `.env`, SSH keys, cloud credentials or the whole environment to the network asks first. So do `bash <(curl …)`, `eval "$(curl …)"` and recursive cloud-storage deletes.
- Quoted text in `git commit -m`, `grep`, `echo` and similar no longer triggers prompts, unless it's piped into a shell or contains `$(…)`.

**Community files.** CONTRIBUTING, SECURITY (private vulnerability reporting), Code of Conduct, issue templates (bug, guard miss / false alarm, skill suggestion) and a PR template.

## 0.5.0 — 2026-11-07

**New: `eos score`, Lighthouse for coding agents.** Grades a Claude Code setup out of 100 across guardrails, working rules, skills and feedback loops, then lists the biggest wins. It credits any guard hook, not only Engineering OS's. Read-only and local; runs without installing anything: `curl -fsSL https://engineering-os-hazel.vercel.app/score | python3 -`. `--card` writes a shareable 1200×630 card (PNG when Chrome or rsvg-convert is available), `--badge` prints a README badge, `--json` for scripts.

**New: `eos receipts`.** The bash and secret guards now keep a local log of what they blocked or held for approval. Commands are redacted before they're written, and secret receipts store only the key type and file name. `eos receipts` shows the week; `--card` and `--share` turn it into a post. Turn off with `EOS_RECEIPTS=off`.

CI now checks that receipts never contain secrets and that `eos score` grades an empty setup F and a guarded one with full guard credit.

## 0.4.0 — 2026-11-07

**New: `/eos:deploy`** — picks the platform (or keeps yours), runs a pre-deploy checklist, sets up CI/CD, and verifies after shipping. Official skills for **Vercel** (deploy), **AWS** (deployment, CDK) and **Azure** (prepare, deploy, validate), plus GitHub Actions templates. On demand (`eos enable deploy`): Cloudflare Workers, Firebase Hosting, Netlify, Railway, Terraform, AWS serverless/containers/IAM/Amplify, Azure diagnostics/AKS/App Service, Vercel optimize.

**Product videos** — Remotion's official skills (best practices, create, render) and a script → storyboard → render workflow in `/eos:gtm`. On demand: Remotion captions and remotion-saas (for apps built on Remotion), HeyGen HyperFrames video.

**Frontend** — Anthropic's frontend-design, canvas-design and webapp-testing; Vercel's agent-browser; Emil Kowalski's design-engineering and Apple-design skills. On demand: animation review/improve, prototyping, UI-library picker, theme factory.

**Backend** — Node.js backend patterns, database migrations, Stripe's own best practices. On demand: NestJS, Firebase, microservices, background jobs, API security testing, QStash.

The session briefing now recognises deploy targets (Vercel, AWS CDK, Azure, Terraform, Firebase, Netlify, Railway, Fly, GitHub Actions) and Remotion projects. 162 skills in total: 84 by default, 78 on demand.

## 0.3.0 — 2026-11-07

**Top-tier stack skills**
- Prisma (official: ORM setup, client API, CLI), Supabase (official, full platform), Neon Postgres, Upstash Redis + rate limiting.
- Vercel AI SDK (official), ui-ux-pro-max design-system, GSAP core + ScrollTrigger (official), Emil Kowalski's animation vocabulary, Core Web Vitals, Vitest (Anthony Fu), E2E testing patterns.
- Optional packs, installed on demand with `eos enable <area>`: Convex, MongoDB, Redis, Cloudflare Workers, Hono, Clerk, Sentry, AWS, GitHub Actions, three.js, LangGraph, ElevenLabs, and a new **mobile** area (Expo, React Native).
- The session briefing spots a stack that has an optional pack (Expo, Convex, Hono…) and suggests the one-line `eos enable`.

**Update notifications**
- Claude Code now tells you when a newer Engineering OS is published, with the exact update command. Checked in the background at most every 12 hours; never slows startup. Turn off with `EOS_UPDATE_CHECK=off`.
- New `eos update`: pulls the latest version and re-installs.

**Fixes**
- Backend playbook pointed at a Postgres skill that wasn't installed; it now routes to `supabase-postgres-best-practices`.
- Install page: long commands wrap cleanly.

## 0.2.1 — 2026-11-06

- One plugin, short commands: `/eos:map`, `/eos:add`, `/eos:frontend`, `/eos:backend`, `/eos:ai`, `/eos:evals`, `/eos:reverse`, `/eos:gtm`, `/eos:research`.
- One-command install for Claude Code and 70+ other agents (`--agent codex`, `cursor`, `gemini-cli`, …).
- Install page with Command and Prompt options.
- Fixes: `curl | bash` stopping early, upstream skill renames (impeccable merged, create-auth), strict-YAML skill descriptions.

## 0.1.0 — 2026-11-06

- First release: playbooks, safety hooks (bash guard, secret guard, session briefing, notifications), curated community-skill registry, `eos` CLI.
