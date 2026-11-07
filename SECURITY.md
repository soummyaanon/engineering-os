# Security policy

Engineering OS runs inside your coding agent: it installs skills, runs hooks on every tool call, and is often installed with `curl | bash`. Security reports are taken seriously and handled first.

## Reporting a vulnerability

**Please don't open a public issue.** Report privately through GitHub: **[Report a vulnerability](https://github.com/soummyaanon/engineering-os/security/advisories/new)** (Security tab → Advisories).

Include what you found, how to reproduce it, and what an attacker could do with it. You'll get an acknowledgement within 3 days and a fix or a plan within 14. Reporters are credited in the advisory and the changelog unless they ask not to be.

## What counts

Report privately:
- `install.sh`, `eos install` / `update`, or `curl …/score | python3 -` running code or writing files they shouldn't.
- A hook that can be made to run attacker-controlled input as code. For example, a crafted file path, command or tool result that a hook executes.
- Secrets reaching anything outside your machine, or reaching the local receipts log (`~/.claude/eos-receipts.jsonl`) without redaction.
- A registry skill that is malicious or has been taken over upstream (supply chain).
- A way to turn off the guards from inside a session without the user knowing.

A normal issue is fine (use the **Guard miss / false alarm** template) for:
- A destructive command or a secret the guards don't catch. The guards are a seatbelt, not a sandbox: they're pattern-based and can't stop deliberate obfuscation. Gaps in common commands are bugs we want public so they get fixed and tested, and `eos redteam` tracks them.

## Supported versions

Only the latest release gets fixes. `eos update` (or `claude plugin update eos@engineering-os`) moves you to it.
