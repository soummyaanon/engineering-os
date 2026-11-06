# Engineering OS

A global harness for Claude Code: curated skills, safety hooks, and playbooks that load in **every project** — frontend, backend, AI, reverse engineering, research, and GTM — and grow by dropping in new skills.

## Install — one command

```bash
curl -fsSL https://raw.githubusercontent.com/soummyaanon/engineering-os/main/install.sh | bash
```

Installs everything: the `eos` plugin (playbooks + hooks), global working rules, ~70 vetted community skills, and the `eos` CLI. Needs `git`, `node`, `python3`. Re-run any time to update. Add `-s -- --all` after `bash` to include optional skills.

Then open a **new** Claude Code session and try `/eos:map <task>`.

## Commands

| Command | Does |
|---|---|
| `/eos:map <task>` | which skill/agent to use for this task |
| `/eos:add <need>` | find the best skill for a need (or write one) and add it |
| `/eos:status` | what's installed / missing |
| `/eos:frontend` `/eos:backend` `/eos:ai` `/eos:evals` | engineering playbooks |
| `/eos:reverse` `/eos:research` `/eos:gtm` | reverse engineering, research, go-to-market |

Claude also loads these on its own when a task matches — you rarely need to type them.

## Hooks (always on)

| Hook | What it does | Opt-out |
|---|---|---|
| Session briefing | Detects the stack (Next.js, FastAPI, Prisma, Anthropic SDK…) and points Claude at the right playbooks | — |
| Bash guard | **Blocks** catastrophic commands (`rm -rf ~`, disk wipes); **asks** before force-push, push to main, `reset --hard`, destructive SQL, `curl \| sh`, `sudo`, publish, prod deploys. `rm -rf node_modules` passes. | `EOS_GUARD=off` or `{"guard":"off"}` |
| Secret guard | Asks before writing real-looking keys / private keys / DB passwords into source (`.env` allowed) | `{"secret_guard":"off"}` |
| Autoformat | Formats edits with the project's own Prettier/Biome/Ruff/gofmt/rustfmt | **opt-in** `{"autoformat":true}` |
| Notification | macOS notification when Claude needs you | `EOS_NOTIFY=off` |

Per-project switches live in `<project>/.claude/eos.json`.

## Grow it

```bash
eos add owner/repo@skill --domain frontend   # adopt a community skill (registry + install + audit)
eos new-skill stripe-webhooks                # your own skill → /eos:stripe-webhooks
eos new-domain mobile -d "iOS/Android"       # new domain + playbook → /eos:mobile
eos status · eos validate · eos audit · eos doctor
```

Or just ask Claude: `/eos:add <need>`. New skills under `plugins/eos/skills/` are live next session — no reinstall.

## Layout

```
engineering-os/
├── install.sh                 # one-command installer
├── CLAUDE.md                  # global working rules (imported by ~/.claude/CLAUDE.md)
├── registry/community.json    # curated community skills by domain (core + optional)
├── bin/eos                    # CLI
└── plugins/eos/               # the plugin → /eos:*
    ├── skills/                # map, add, frontend, backend, ai, evals, reverse, gtm, research
    ├── agents/researcher.md
    ├── commands/              # status, setup
    └── hooks/                 # briefing, guards, autoformat, notify
```

## Alternative: plugin marketplace

```bash
claude plugin marketplace add soummyaanon/engineering-os && claude plugin install eos@engineering-os
```

Then run `/eos:setup` once inside Claude Code for the community skills and rules. Use either this or `install.sh`, not both.

## Vetting bar for community skills

Official vendor or well-known author · ≥1K installs (prefer ≥10K) · not redundant · SKILL.md read for off-task/unsafe instructions · `eos audit` clean. Quality over quantity: every skill description costs context and competes for Claude's attention.

MIT licensed.
