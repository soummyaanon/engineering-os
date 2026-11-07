# Contributing to Engineering OS

Thanks for helping. Engineering OS is small on purpose: Python stdlib only, no build step, no runtime dependencies. Contributions that keep it that way are the easiest to merge.

## Ways to help

| You want to… | Do this |
|---|---|
| Suggest a skill | Open a **Skill suggestion** issue, or a PR that runs `eos add owner/repo@skill --domain <d>` |
| Report a guard that missed something, or nagged about something harmless | Open a **Guard miss / false alarm** issue with the exact command |
| Fix a bug | Open a **Bug report** first if it's not obvious, then a PR |
| Improve a playbook (`/eos:frontend`, `/eos:backend`, …) | Edit `plugins/eos/skills/<name>/SKILL.md` and open a PR |
| Report a security problem | **Don't open an issue.** See [SECURITY.md](SECURITY.md) |

## Setup

```bash
git clone https://github.com/soummyaanon/engineering-os && cd engineering-os
python3 bin/eos doctor        # checks prerequisites; needs Python 3.8+, git, node (for `npx skills`)
```

To try your checkout as your live setup, point the plugin link at it: `ln -sfn "$PWD/plugins/eos" ~/.claude/skills/eos`, then start a new Claude Code session.

## Layout

```
bin/eos              the manager CLI (install, add, validate, verify, …)
bin/eos_score.py     eos score / receipts / redteam, a standalone file so `curl … | python3 -` works
plugins/eos/hooks/   the guards and other hooks (bash_guard.py, secret_guard.py, session_brief.py, …)
plugins/eos/skills/  the playbooks and the skill map
registry/            community.json: every third-party skill and plugin, with domain and core/optional
tests/               stdlib test scripts, run by CI
site/                the static landing page (deployed with the Vercel CLI from site/)
```

## Before you open a PR

Run what CI runs:

```bash
python3 -m py_compile plugins/eos/hooks/*.py bin/eos bin/eos_score.py tests/*.py
python3 tests/test_bash_guard.py      # guard decision table
python3 bin/eos_score.py redteam      # every attack stopped, no false alarms, against your installed guards
python3 bin/eos validate              # plugin, marketplace and skill frontmatter
python3 bin/eos verify                # every registry skill still exists upstream (needs network)
```

## Rules for specific areas

**Registry skills** must meet the vetting bar: an official vendor or a well-known author, at least 1K installs, and no install-time scripts. In the PR, say what the skill beats in the current set and why. Rarely used skills go in `optional`, not `core`; every core skill costs context in every session.

**Guards** (`bash_guard.py`, `secret_guard.py`):
- Every change adds a case to `tests/test_bash_guard.py`, and to the redteam corpus in `bin/eos_score.py` (`redteam_corpus`) if it's a new kind of attack or a new look-alike.
- `eos redteam` must stay at every attack stopped with zero false alarms.
- A false alarm is a bug too. Guards that nag get turned off, and then they stop nothing.

**Never commit a key-shaped string**, even a fake one. GitHub push protection blocks it, and scanners copy it. Build test keys at runtime, for example `"sk" + "_live_" + "…"`; see `.github/workflows/verify.yml`.

**Python** stays stdlib-only and 3.8-compatible. Hooks must never crash Claude Code: catch broad exceptions at the edges and exit 0 when unsure.

## Commits and PRs

- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Keep PRs small and focused. Add a line to `CHANGELOG.md` under the next version for anything user-visible.
- Fill in the PR template. "How I verified it" is the part reviewers read first.

By contributing you agree your work is released under the [MIT License](LICENSE) and that you'll follow the [Code of Conduct](CODE_OF_CONDUCT.md).
