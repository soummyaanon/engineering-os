---
name: backend-playbook
description: Engineering OS backend playbook — designing and changing APIs, services, databases, auth, background jobs, payments, and infrastructure (Node/TypeScript, Python/FastAPI/Django, Go, Postgres, Prisma/Drizzle, Supabase, Redis, queues, Docker, serverless). Use for any server-side task, schema change, migration, endpoint, webhook, auth/permissions work, performance problem, or deploy — even when the user only says "add a feature" and the feature needs a server. Defines the correctness, security, and verification bar.
---

# Backend Playbook

Backend bugs are expensive because they corrupt data, leak data, or fail silently at 3am. This playbook optimizes for: correct data, least privilege, observable failures, reversible changes.

## 1. Orient

- Find the entrypoint, routing layer, data layer (ORM/schema files), config/env loading, and how tests run. Read one existing endpoint end-to-end (route → validation → service → db → response) and **follow the same layering**.
- Check `.env.example` / config schema for what's required. Never print or commit secrets; read them via env.
- Identify the migration tool and whether migrations are applied automatically on deploy.

## 2. Specialist skills

| Situation | Skill |
|---|---|
| Postgres schema, indexes, queries, RLS | `postgres-best-practices` |
| Auth (sessions, OAuth, 2FA, orgs/teams, email+password) | `better-auth-best-practices`, `better-auth-security-best-practices`, `two-factor-authentication-best-practices`, `organization-best-practices`, `email-and-password-best-practices` |
| Payments, subscriptions, webhooks | `stripe:stripe-best-practices` |
| Building an MCP server | `mcp-builder` |
| System/architecture decisions, ADRs | `engineering:system-design`, `engineering:architecture` |
| Production incident | `engineering:incident-response`, then `superpowers:systematic-debugging` |
| Deploy readiness | `engineering:deploy-checklist` |
| Security review of a diff | `security-review` |

## 3. API design

- **Validate at the boundary** with a schema (zod / pydantic / valibot). Reject unknown fields on writes. Parse, don't trust: types from the request are `unknown` until validated.
- Resource-oriented REST (or tRPC/GraphQL if the project uses it — match it). Plural nouns, correct verbs, correct status codes: 400 validation, 401 unauthenticated, 403 unauthorized, 404, 409 conflict, 422 semantic, 429 rate-limited. Never 200 with `{error}`.
- One consistent error shape: `{ error: { code, message, details? } }`. Messages safe for end users; internals go to logs.
- Pagination on every list endpoint (cursor-based for large/real-time sets). Cap page size.
- **Idempotency** for anything that charges money, sends messages, or creates external side effects: idempotency key or natural unique constraint. Webhooks are delivered at-least-once — dedupe by event id.
- Version breaking changes; additive changes don't need a version.

## 4. Data

- Schema changes go through migrations, never manual edits. Migrations must be **backwards-compatible with the currently-deployed code**: expand → deploy → backfill → contract. Adding a NOT NULL column = add nullable, backfill, then constrain.
- Index what you filter/join/sort on; check with `EXPLAIN ANALYZE` for anything on a hot path. Watch for N+1 (ORM loops) — use joins/`include`/dataloaders.
- Transactions for multi-row invariants. Keep them short; never call external APIs inside a transaction.
- Use the DB for integrity: foreign keys, unique constraints, check constraints. App-level checks race.
- Money as integer minor units (cents) or decimal — never float. Timestamps in UTC (`timestamptz`).
- Soft-delete only if there's a product reason; otherwise delete and rely on backups/audit log.

## 5. Security (OWASP minimum bar)

- AuthN on every non-public route; **AuthZ on every resource access** — check the caller owns/can access *this* object id (IDOR is the #1 real-world API bug).
- Parameterized queries only. No string-built SQL, shell commands, or file paths from user input.
- Rate-limit auth, signup, password reset, and expensive endpoints.
- Secrets from env/secret manager; rotateable; never logged. Hash passwords with argon2id/bcrypt (or use the auth library).
- CORS: explicit origins, not `*` with credentials. Cookies: `HttpOnly; Secure; SameSite=Lax` or stricter.
- Verify webhook signatures. Validate redirect URLs against an allowlist. Limit upload size and type.
- Least-privilege DB roles and API keys.

## 6. Reliability & observability

- Structured logs (JSON) with request id, user id (not PII), and duration. Log at boundaries, not in loops.
- Timeouts on every outbound call; retries with exponential backoff + jitter **only** for idempotent operations.
- Slow work (emails, AI calls > a few seconds, exports) goes to a queue/background job, not the request path.
- Health check endpoint. Graceful shutdown (drain in-flight requests).
- Errors reported to the project's error tracker with context.

## 7. Verify (required before "done")

1. Typecheck, lint, unit tests — the project's own commands.
2. Add or update tests at the right level: unit for logic, integration for route → db (use a real test DB or testcontainers when the project supports it; don't mock the ORM into meaninglessness).
3. Run the migration up **and** down (or forward-fix plan) against a local DB.
4. Hit the endpoint for real (curl/httpie) with: happy path, invalid input, unauthenticated, wrong-user (authz), and duplicate request (idempotency).
5. State exactly what was verified. If something couldn't be run locally, say so.
