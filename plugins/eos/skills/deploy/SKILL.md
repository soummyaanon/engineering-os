---
name: deploy
description: "Engineering OS deployment playbook — ship apps and services to Vercel, AWS, Azure, Cloudflare, Firebase, Netlify, Railway or containers: choosing a platform, environment variables and secrets, CI/CD with GitHub Actions, infrastructure as code (CDK, Bicep, Terraform), database migrations during deploys, custom domains, preview environments, rollbacks, and post-deploy verification. Use whenever the user wants to deploy, host, ship, go live, set up CI/CD, move to AWS or Azure, fix a failing deploy, or asks where to host something, even if they never say 'deploy'."
---

# /eos:deploy — ship it safely

Deploys fail in predictable ways: a missing env var, a migration that ran in the wrong order, no way back when it breaks. This playbook makes every deploy boring: chosen deliberately, checked before, verified after, and reversible.

Deploys and infra changes are outward-facing. The bash guard asks before `--prod`, `terraform apply`, `kubectl apply` and friends, and you should confirm the target with the user before the first production deploy of a project.

## 1. Pick the platform (only if it isn't already decided)

Check first: `vercel.json`, `.vercel/`, `wrangler.toml`, `firebase.json`, `netlify.toml`, `railway.json`, `cdk.json`, `azure.yaml`, `*.bicep`, `*.tf`, `Dockerfile`, `.github/workflows/`. If the project already deploys somewhere, stay there unless asked.

| Situation | Default | Skill |
|---|---|---|
| Next.js / React / static frontend, fast previews | **Vercel** | `deploy-to-vercel`; `vercel-optimize` for cost/perf; `vercel-cli-with-tokens` for CI |
| Edge APIs, global low latency, cheap | **Cloudflare Workers** | `workers-best-practices` |
| Full control, enterprise, existing AWS account | **AWS** | `aws-cdk` (infrastructure as code), `aws-deployment` (CodePipeline/CodeBuild CI/CD); `aws-serverless`, `aws-containers`, `aws-iam`, `aws-amplify` on demand; `architect-for-startups` for a first design |
| Microsoft shop, Entra ID, existing Azure subscription | **Azure** | `azure-prepare` → `azure-validate` → `azure-deploy` (Azure Developer CLI / azd workflow); `python-appservice-deploy` for code-only Python deploys; `azure-diagnostics` when it breaks |
| Simple container or long-running service, minimal ops | **Railway** / Render / Fly | `use-railway` |
| Firebase / mobile backend | **Firebase** | `firebase-hosting-basics` |
| Static site with forms/functions | **Netlify** | `netlify-deploy` |
| Multi-cloud or existing Terraform | **Terraform** | `terraform-style-guide` |

On-demand skills come with `eos enable deploy`. Building the image itself: `multi-stage-dockerfile`.

## 2. Pre-deploy checklist

- [ ] **Build passes locally** with production settings (`NODE_ENV=production`, `next build`, etc.).
- [ ] **Env vars**: every variable the app reads exists in the target environment (diff `.env.example` against the platform's settings). Secrets live in the platform's secret store, never in the repo or the workflow file.
- [ ] **Database migrations**: backwards-compatible with the code currently running (expand → deploy → contract). Decide whether they run before the deploy (release step) or after; never in two places.
- [ ] **Health check** endpoint exists and is wired to the platform.
- [ ] **Rollback path** known: previous deployment promote (Vercel), previous task definition / CDK stack version (AWS), deployment slot swap (Azure), `wrangler rollback` (Cloudflare).
- [ ] **Preview first**: deploy to a preview/staging environment and smoke-test it before production.
- [ ] **Domains and TLS**: DNS records and certificates planned; expect propagation time.
- [ ] **Cost**: rough monthly estimate for anything that scales with traffic (AWS/Azure especially).

## 3. CI/CD

Use GitHub Actions unless the project has another CI (`github-actions-templates`). Minimum pipeline: install → lint/typecheck → test → build → deploy preview on PRs → deploy production on `main` with a manual approval for the first few releases. Use OIDC federation (AWS/Azure) or scoped tokens, never long-lived admin keys. Pin action versions.

## 4. Deploy

Run the platform's CLI or pipeline. Watch the logs while it rolls out rather than walking away.

## 5. Verify (required before saying "deployed")

1. Open the live URL and exercise the main path once (use `agent-browser` or the `playwright` plugin for a screenshot).
2. Hit the health endpoint and one real API route.
3. Check logs and error tracking for new errors in the first few minutes.
4. Confirm the version/commit that's live matches what you meant to ship.
5. Report: URL, commit, what was verified, and the rollback command.

If something is broken, roll back first, then debug (`superpowers:systematic-debugging`, `azure-diagnostics`, AWS logs).
