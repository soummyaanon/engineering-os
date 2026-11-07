## What and why

<!-- One or two sentences. Link the issue if there is one: Fixes #123 -->

## How I verified it

<!-- Commands you ran and what they printed. "Tests pass" without output is not verification. -->

- [ ] `python3 tests/test_bash_guard.py`
- [ ] `python3 bin/eos_score.py redteam` (if guards or the corpus changed: every attack stopped, 0 false alarms)
- [ ] `python3 bin/eos validate`
- [ ] Tried it in a real Claude Code session (say what you did)

## Checklist

- [ ] Small and focused; no unrelated changes
- [ ] Stdlib-only Python, 3.8-compatible
- [ ] No key-shaped strings committed, even fake ones (build them at runtime)
- [ ] Registry additions meet the vetting bar (official or well-known author, 1K+ installs, no install scripts)
- [ ] `CHANGELOG.md` updated if users will notice
