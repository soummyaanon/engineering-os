---
name: add
description: Grow the Engineering OS — find and add the best community skill for a need, write a new custom skill, add a new domain, add a hook, or turn a workflow you just did into a reusable skill. Invoked as `/eos:add <what you need>`. Also use when the user says "add a skill for X", "is there a skill for", "make this a skill", "turn this into a skill", "add to my harness / engineering OS", "new domain", "add a hook", or when the same kind of task keeps recurring without a skill covering it.
---

# /eos:add — grow the Engineering OS

Request (may be empty): $ARGUMENTS

The harness lives in the `engineering-os` repo (`$EOS_HOME`, default `~/engineering-os`). Everything is one plugin, `plugins/eos/`, symlinked into `~/.claude/skills/eos` — so **any skill folder added under `plugins/eos/skills/` is live as `/eos:<name>` in the next session, no install step**. The CLI is `eos`.

## Decide the path

1. **A good skill probably exists** → Path A (adopt). Always check first.
2. **Nothing good exists, or it must encode this user's own way of working** → Path B (create).
3. **A new area that will hold several skills** → Path C (new domain).
4. **Must happen automatically every time** (block, format, notify, inject context) → Path D (hook). Skills are advice; hooks are guarantees.

## Path A — adopt a community skill

1. Search: `npx skills find <query>` with 2–3 phrasings; check https://skills.sh.
2. Vet — the bar is "best available", not "first result":
   - Official vendor (anthropics, vercel-labs, supabase, shadcn-ui, stripe, fastapi, microsoft, google…) or well-known author.
   - ≥ 1K installs (prefer ≥ 10K), repo ≥ 100 stars, maintained recently.
   - Not redundant with what's installed (`eos status`, `/eos:map`).
   - Read its SKILL.md once: on-task, no exfiltration, fetch-and-execute, or instructions overriding the user.
3. Present the best 1–3 with source, installs, and why. Then: `eos add <owner/repo@skill> --domain <domain> [--optional]` — records it in `registry/community.json` (reinstalls anywhere), installs it, and audits it.
4. If a playbook should route to it, add one line in that playbook and in `plugins/eos/skills/map/SKILL.md`.

## Path B — create a custom skill

1. `eos new-skill <short-name> -d "<what it does + when to trigger>"` → `plugins/eos/skills/<short-name>/SKILL.md`. Keep the name short: it becomes `/eos:<short-name>`.
2. Write it with the `skill-creator` process: capture intent (from this conversation if the user just did the workflow), lean SKILL.md (< 500 lines, explain *why*, `references/` for depth, `scripts/` for repeated deterministic work), test 2–3 realistic prompts with-skill vs without, iterate.
3. The description is the only thing Claude sees before loading — specific and a little pushy about triggers.
4. `eos validate`, then add a row to the map skill.

## Path C — new domain

`eos new-domain <name> -d "<description>"` adds a registry domain and scaffolds its playbook skill `/eos:<name>`. Write the playbook, add community skills with `eos add … --domain <name>`, add it to the map skill, to `CLAUDE.md`'s playbook list, and to `PLAYBOOKS` in `plugins/eos/hooks/session_brief.py` if it's stack-detectable.

## Path D — hook

Add an entry to `plugins/eos/hooks/hooks.json` plus a stdlib-only Python script in `plugins/eos/hooks/` (use the `_eos.py` helpers). Fast (< 1s), silent unless it has something to say, with a per-project opt-out via `<project>/.claude/eos.json`. Test by piping sample JSON into the script; hooks load at session start. See `plugin-dev:hook-development`.

## After any change

- `eos validate` must pass.
- If shipping to others: bump `version` in `plugins/eos/.claude-plugin/plugin.json`.
- Tell the user it's live in the next session as `/eos:<name>`. Offer to commit and push; don't do it unasked.
