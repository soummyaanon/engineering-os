# Changelog

Update any time with `eos update` (or re-run the install command). Claude Code tells you when a new version is out.

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
