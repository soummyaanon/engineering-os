---
name: frontend-playbook
description: Engineering OS frontend playbook — how to build, change, and verify web UI (React, Next.js, Vue, Svelte, Astro, Tailwind, landing pages, dashboards, design systems, animations). Use whenever the task touches components, pages, styling, layout, client state, forms, accessibility, Core Web Vitals, or "make it look better", even if the user never says "frontend". Routes to the right specialist design/perf skills and defines the verification bar (run it, look at it, screenshot it) before calling UI work done.
---

# Frontend Playbook

Frontend work fails in two ways: it doesn't work (state bugs, hydration errors, broken layout at some width) or it works but looks generic. This playbook covers both. The verification loop at the bottom is the non-negotiable part — UI that wasn't looked at isn't done.

## 1. Orient before touching anything

- Read `package.json`, the router layout (`app/` vs `pages/` vs `src/routes`), the styling system (Tailwind config, CSS modules, tokens file), and one or two existing components that resemble what you're building. **Match existing patterns** — a new component that ignores the house style is a regression even if it's prettier.
- Find the design tokens (colors, spacing, radii, type scale). Never hardcode a hex or px value that a token already covers.
- If the project has a design system / component library (shadcn/ui, Radix, MUI, internal), compose from it rather than rebuilding primitives.
- If the user said to keep existing visuals, keep them. Add; don't replace.

## 2. Pick the specialist skill

| Situation | Skill |
|---|---|
| New UI with no strong existing style; "make it distinctive / premium" | `frontend-design:frontend-design`, then `ui-ux-pro-max` for palette/type/layout systems |
| React/Next.js performance, data fetching, bundle size, re-renders | `vercel-react-best-practices` |
| Next.js App Router structure, server/client components, caching | `nextjs-app-router-patterns` |
| Review UI against web interface guidelines / accessibility | `web-design-guidelines`, then `audit` |
| Polishing an existing screen | `critique` → then the matching fix: `polish`, `typeset`, `arrange`, `colorize`, `clarify`, `quieter`/`bolder`, `delight`, `animate`, `adapt` (responsive), `harden` (edge cases/errors), `normalize` (consistency), `optimize` (perf), `distill` (simplify) |
| Isometric/technical explainer illustration | `anatomy` |
| Charts, dashboards, KPI tiles | `dataviz` |
| Auth screens / flows | `better-auth-best-practices` (+ eos-backend:backend-playbook for the server side) |
| Shopify themes | `liquid-skills:shopify-liquid-themes` |
| SEO for marketing pages | `seo-audit`, `ai-seo` |

Load only what the task needs. One or two skills, read fully, beats skimming six.

## 3. Build rules

**Components** — Small, single-purpose, typed props (no `any`). Co-locate component, styles, and test. Lift state only as far as it needs to go. Derive, don't sync: if a value can be computed from props/state, compute it; `useEffect` that sets state from other state is almost always a bug.

**Next.js / React Server Components** — Default to server components; add `"use client"` only at the leaves that need interactivity. Fetch on the server, pass plain data down. Never import server-only modules (db, secrets) into client components. Use `next/image` and `next/font`. Mark dynamic vs static rendering deliberately.

**State & data** — Server state goes in the framework's data layer or TanStack Query, not in global stores. URL is state: filters, tabs, pagination belong in search params so they survive reloads and are shareable. Forms: controlled by a form lib (react-hook-form/conform) + schema validation (zod) shared with the backend.

**Every async UI has four states**: loading (skeleton matching final layout, no spinner-jank), empty (with a next action), error (human message + retry), success. Missing any one is a bug.

**Styling** — Mobile-first. Test 360px, 768px, 1280px, 1920px. No horizontal scroll at 360px. Use `clamp()` for fluid type. Respect `prefers-reduced-motion` and `prefers-color-scheme`. Animations: transform/opacity only, 150–300ms, ease-out for enter.

**Accessibility (minimum bar, not optional)** — Semantic elements first (`button`, `a`, `nav`, `main`, `label`). Every interactive element reachable and operable by keyboard with a visible focus ring. Images have meaningful `alt` (or `alt=""` if decorative). Color contrast ≥ 4.5:1 for body text. Form inputs have associated labels and error messages linked via `aria-describedby`. Dialogs trap focus and restore it.

**Performance budget** — LCP < 2.5s, INP < 200ms, CLS < 0.1. Reserve space for images/embeds (width/height or aspect-ratio). Lazy-load below-the-fold media. Code-split heavy client-only libs with dynamic import. Don't ship a 300KB library for one function.

**Security** — Never `dangerouslySetInnerHTML` with unsanitized input. No secrets in client bundles (`NEXT_PUBLIC_*` is public). Validate on the server even if the client validates.

## 4. Verify (required before saying "done")

1. **Typecheck + lint + tests**: run the project's own scripts (`npm run typecheck`, `lint`, `test`). Fix what you broke.
2. **Run it**: start the dev server (or use the `run` skill) and load the actual page.
3. **Look at it**: use Playwright (`playwright` plugin tools) to screenshot at mobile (390×844) and desktop (1440×900). Actually view the screenshots. Check: layout, overflow, contrast, empty/error states, dark mode if supported.
4. **Console**: zero new errors or hydration warnings.
5. **Interact**: click the primary path once — submit the form, open the modal, navigate.

Report what you verified and how. If you couldn't run it (no dev server, missing env), say so plainly instead of implying it works.

## 5. Common traps

- Hydration mismatch from `Date.now()`, `Math.random()`, `window` access during render → move to effect or server.
- Layout shift from fonts → `next/font` or `font-display: optional` + size-adjust.
- Stale closures in effects/handlers → correct dependency arrays; prefer event handlers over effects.
- Z-index wars → define a small z-index scale in tokens.
- "Works on my screen" → you only checked 1440px. Check 360px.
