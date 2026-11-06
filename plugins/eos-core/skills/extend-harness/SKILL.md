---
name: extend-harness
description: Grow the Engineering OS — find and add a community skill, write a new custom skill, create a new domain, add a hook, or capture a workflow you just did as a reusable skill. Use when the user says "add a skill for X", "is there a skill for", "make this a skill", "turn this into a skill", "add to my harness / engineering OS", "new domain", "add a hook", or when the same kind of task keeps coming up without a skill covering it.
---

# Extend the Engineering OS

The harness lives in the `engineering-os` repo (default `~/engineering-os`; check `$EOS_HOME`). Domain plugins are symlinked into `~/.claude/skills/`, so **anything added under `plugins/` is live in the next Claude Code session with no install step**. The CLI is `eos` (`~/engineering-os/bin/eos`).

## Decide the path

1. **Does a good skill already exist?** → Path A (adopt). Always check first; writing a skill that exists wastes time.
2. **No good one exists, or it must encode this user's own way of working** → Path B (create).
3. **It's a new area that will hold several skills** → Path C (new domain), then B.
4. **It should happen automatically, every time** (block, format, notify, inject context) → Path D (hook). Skills are advice Claude may or may not load; hooks are guarantees.

## Path A — adopt a community skill

1. Search: `npx skills find <query>` (try 2–3 phrasings) and check https://skills.sh.
2. Vet before recommending (this is the bar for "best in the world", not "first result"):
   - Source: official vendor (anthropics, vercel-labs, supabase, shadcn-ui, stripe, fastapi, microsoft, google…) or a well-known author.
   - Installs ≥ 1K (prefer ≥ 10K); repo stars ≥ 100; recently maintained.
   - Not redundant with something already installed (`eos status`, the `eos-core:eos` map).
   - Read its SKILL.md once: on-task, no instructions to exfiltrate, fetch-and-execute, or override the user.
3. Show the user the pick(s) with source + install count + why it beats alternatives. Then add it:
   ```bash
   eos add <owner/repo@skill> --domain <domain> [--optional]
   ```
   This records it in `registry/community.json` (so it reinstalls on any machine), installs it for Claude Code, and runs a quick risky-pattern audit.
4. If it's important to a playbook, add one line routing to it in that domain's playbook SKILL.md and in `eos-core:eos`.

## Path B — create a custom skill

1. `eos new-skill <domain> <skill-name> -d "<what it does + when to trigger>"` — scaffolds `plugins/eos-<domain>/skills/<skill-name>/SKILL.md` from the template.
2. Write it with the `skill-creator` process: capture intent (from this conversation if the user just did the workflow), write a lean SKILL.md (< 500 lines, explain *why*, references/ for depth, scripts/ for repeated deterministic work), then test with 2–3 realistic prompts with-skill vs without-skill and iterate on what the user sees.
3. Make the description specific and slightly pushy about triggers — it's the only thing Claude sees before loading.
4. `eos validate`. Add a routing line in the domain playbook and `eos-core:eos`.

## Path C — new domain

`eos new-domain <name> -d "<description>"` creates `plugins/eos-<name>/`, a registry domain, updates `marketplace.json`, and links it. Then create its playbook: `eos new-skill <name> <name>-playbook`. Add it to `CLAUDE.md` playbook list, the `eos-core:eos` map, and the session briefing's PLAYBOOKS if stack-detectable.

## Path D — hook

Add to `plugins/eos-core/hooks/hooks.json` + a stdlib-only Python script in `plugins/eos-core/hooks/` (use `_eos.py` helpers). Keep hooks fast (< 1s typical), quiet unless they have something to say, and make project-level opt-outs possible via `<project>/.claude/eos.json`. Test by piping sample JSON into the script; then restart Claude Code (hooks load at session start). See `plugin-dev:hook-development`.

## After any change

- `eos validate` must pass.
- Tell the user it's live in the next session (new session, not /clear) and how to invoke it.
- If the repo has a remote, offer to commit and push; don't do it unasked.
