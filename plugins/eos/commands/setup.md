---
description: One-time Engineering OS setup for marketplace installs — installs the curated community skills and the global working rules
allowed-tools: Bash
---

Run this one-time setup for Engineering OS (it was installed from the plugin marketplace, so the curated community skills and global rules aren't on this machine yet).

1. Locate the marketplace copy: `EOS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/engineering-os"` and confirm `$EOS/bin/eos` exists. If not, tell the user to run `claude plugin marketplace add soummyaanon/engineering-os && claude plugin install eos@engineering-os` first.
2. Check prerequisites: `node`/`npx` and `python3` must be on PATH. If missing, explain how to install them and stop.
3. Tell the user what will happen: about 70 vetted community skills get installed into `~/.claude/skills` via `npx skills`, and `~/.claude/CLAUDE.md` gets one import line for the Engineering OS working rules (existing content is kept). Then run:
   `python3 "$EOS/bin/eos" install --no-link $ARGUMENTS`
   (`--all` also installs optional skills.)
4. Summarize the result in a few lines and tell the user to start a new Claude Code session to load everything.
