# Engineering OS

A global harness for Claude Code: curated skills, safety hooks, and domain playbooks that load in **every project** on this machine — frontend, backend, AI, reverse engineering, research, and GTM — and grow by dropping in new skills.

## What's inside

```
engineering-os/
├── CLAUDE.md                     # global working rules (imported by ~/.claude/CLAUDE.md)
├── registry/community.json       # curated community skills by domain (core + optional tiers)
├── bin/eos                       # manager CLI
├── templates/skill/SKILL.md      # template for new skills
├── .claude-plugin/marketplace.json
└── plugins/
    ├── eos-core/                 # hooks + skill map + harness-extension workflow + /commands
    ├── eos-frontend/             # frontend-playbook
    ├── eos-backend/              # backend-playbook
    ├── eos-ai/                   # ai-engineering, llm-evals
    ├── eos-reverse-engineering/  # reverse-engineering
    ├── eos-gtm/                  # gtm-strategy
    └── eos-research/             # research + researcher agent
```

**Hooks (eos-core)**

| Hook | What it does | Opt-out |
|---|---|---|
| SessionStart briefing | Detects the stack (Next.js, FastAPI, Prisma, Anthropic SDK…) and tells Claude which playbooks apply | — |
| Bash guard | **Denies** catastrophic commands (`rm -rf ~`, disk wipes); **asks** before force-push, push to main, `reset --hard`, destructive SQL, `curl \| sh`, `sudo`, publish, prod deploys. Routine `rm -rf node_modules` passes. | `EOS_GUARD=off` or `{"guard":"off"}` |
| Secret guard | Asks before writing real-looking API keys/private keys/DB passwords into source files (`.env` is allowed) | `{"secret_guard":"off"}` |
| Autoformat | Formats edited files with the project's own Prettier/Biome/Ruff/gofmt/rustfmt | **opt-in**: `{"autoformat":true}` |
| Notification | macOS notification when Claude needs you | `EOS_NOTIFY=off` |

Per-project switches go in `<project>/.claude/eos.json`.

## Install (this machine or a new one)

```bash
git clone https://github.com/soummyaanon/engineering-os ~/engineering-os
~/engineering-os/bin/eos install          # links plugins + rules, installs core community skills
ln -sf ~/engineering-os/bin/eos ~/.local/bin/eos
```

Then start a new Claude Code session. `eos install --all` also installs optional skills; `eos enable gtm` turns on one domain's optional tier.

Plugins are **symlinked** into `~/.claude/skills/` (they load as `eos-*@skills-dir`), so edits in this repo are live in the next session — no reinstall.

## Grow it

```bash
eos add owner/repo@skill --domain frontend   # adopt a community skill (recorded in the registry, audited)
eos new-skill backend stripe-webhooks        # write your own skill inside a domain
eos new-domain mobile -d "iOS/Android apps"  # a whole new domain plugin
eos validate                                 # check everything
eos status | eos audit | eos doctor
```

Or just ask Claude: *"add a skill for X"* / `/eos-core:add-skill X` — it uses `find-skills` + vetting, or `skill-creator` to write and eval a new one.

## Share it

**Option A — plugin marketplace** (requires Node.js + Python 3):

```bash
claude plugin marketplace add soummyaanon/engineering-os
for p in core frontend backend ai reverse-engineering gtm research; do claude plugin install eos-$p@engineering-os; done
```

Start Claude Code and run **`/eos-core:setup`** once — it installs the curated community skills and the global rules (the session briefing reminds you until it's done). Update later with `claude plugin marketplace update engineering-os`.

**Option B — clone** (best if you'll customize it): `git clone` + `bin/eos install`, as in *Install* above. Edits are live.

Don't use both on one machine — the plugins would load twice.

## Vetting bar for community skills

Official vendor or well-known author · ≥1K installs (prefer ≥10K) · not redundant with what's installed · SKILL.md read once for off-task/unsafe instructions · `eos audit` clean. Quality over quantity: every skill description costs context and competes for Claude's attention.
