---
name: gtm-strategy
description: Engineering OS go-to-market playbook — ICP and positioning, messaging, pricing and packaging, launch plans, channel strategy, landing page and funnel design, demos, sales motion (PLG vs sales-led), metrics, and growth experiments for software/AI products. Use whenever the user is preparing a launch or demo, writing a landing page or pitch, deciding pricing, choosing channels, asking "how do I get users/customers", building marketing for a product they built, or doing anything GTM/marketing/sales-related — and route to the specialist marketing skills for execution.
---

# Go-To-Market Playbook

GTM fails when it starts from tactics ("let's do TikTok") instead of a sharp answer to: **who exactly is this for, what painful problem does it solve for them, and why is it better than what they do today?** Nail that, and every page, email, and demo writes itself.

## 1. Foundation (do once, revisit quarterly) — produce `gtm/positioning.md`

1. **ICP** — the narrowest segment that has the pain most acutely and can pay: role, company type/size, trigger event ("just raised Series A", "hiring first SDR"), where they hang out. Name 3 real example accounts/people.
2. **Problem & current alternative** — what they do today (incl. spreadsheets, interns, doing nothing) and what it costs them (time, money, risk).
3. **Positioning** (April Dunford): competitive alternatives → unique capabilities → value those enable → who cares most → market category.
4. **Messaging hierarchy** — one-line value prop (outcome, not feature), 3 pillars each with proof (metric, demo, logo, quote), objection handling.
5. **Proof inventory** — what evidence exists today; what's missing.

Use `customer-research` to ground ICP and language in real customer words, `competitor-profiling` / `eos-reverse-engineering:reverse-engineering` §4 for alternatives, `product-marketing` and `marketing-psychology` for messaging.

## 2. Pricing & packaging

Value metric first (what scales with value they get: seats, usage, outcomes), then tiers (good/better/best with a clear upgrade trigger), then numbers anchored to the current alternative's cost. AI products: watch gross margin per unit of usage — model cost can eat a flat price. Use `pricing` for the detailed method.

## 3. Motion & channels

- **PLG** (self-serve, low ACV, fast time-to-value) vs **sales-led** (high ACV, multi-stakeholder) vs hybrid. Decide by ACV and time-to-value, not preference.
- Pick **1–2 channels** where the ICP already is and you have an unfair advantage; ignore the rest until those work. Typical: founder-led outbound (`cold-email`), content/SEO (`content-strategy`, `seo-audit`, `ai-seo`), communities, partnerships, launches (`launch`).
- Every channel gets a hypothesis, a weekly metric, and a kill date.

## 4. Assets

| Asset | Skill |
|---|---|
| Landing page copy | `copywriting`, then `copy-editing` |
| Landing page conversion review | `cro` |
| Landing page build | `eos-frontend:frontend-playbook` (keep existing visuals if told to) |
| Launch plan (Product Hunt, HN, X, email) | `launch` |
| Outbound sequences | `cold-email` |
| Funnel/event tracking | `analytics` |
| Full marketing plan | `marketing-plan` |
| Decks / one-pagers | `anthropic-skills:pptx`, `anthropic-skills:docx`, Artifact slides |

## 5. Demo playbook (for a live product demo)

- Open with the customer's pain in their words (30s), then the "aha" moment within 2 minutes. No login screens, no settings pages.
- One golden path, rehearsed, with **seeded realistic data** and a reset script. Have a recorded backup video.
- Show the before/after metric. End with a single clear ask (pilot, next meeting, sign-up).
- Pre-flight: fresh browser profile, notifications off, zoom 125%, stable network, all accounts logged in, error states not reachable from the golden path.

## 6. Metrics

Define the funnel with one number per stage: visit → signup → activation (the specific action that predicts retention) → retained (week 4) → paid → expansion. North-star = the activation/usage metric that tracks delivered value. Track CAC payback and retention cohorts before scaling spend.

## 7. Output format

For strategy requests produce a concise doc: **Positioning · ICP · Messaging · Pricing · Motion & channels (with metrics and kill criteria) · 30/60/90-day plan · Risks & assumptions to test**. Mark every assumption that isn't backed by data, and propose the cheapest test for it.
