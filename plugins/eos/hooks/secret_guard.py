#!/usr/bin/env python3
"""PreToolUse(Write|Edit|MultiEdit) guard: stop real secrets from being written into source files.

Writes into .env* files are allowed (that is where secrets belong) but writes of secrets
anywhere else trigger an "ask". Placeholders like sk-xxx / YOUR_KEY are ignored.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import project_config, pretool_decision, read_input  # noqa: E402

PATTERNS = [
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----", "a private key"),
    (r"\bAKIA[0-9A-Z]{16}\b", "an AWS access key id"),
    (r"\bsk-ant-[A-Za-z0-9_\-]{30,}", "an Anthropic API key"),
    (r"\bsk-(proj-)?[A-Za-z0-9_\-]{32,}", "an OpenAI-style API key"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "a GitHub token"),
    (r"\bxox[baprs]-[A-Za-z0-9\-]{10,}", "a Slack token"),
    (r"\b(sk|rk)_live_[A-Za-z0-9]{20,}", "a Stripe live key"),
    (r"\bAIza[0-9A-Za-z_\-]{35}\b", "a Google API key"),
    (r"\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}", "a JWT"),
    (r"(postgres|postgresql|mysql|mongodb(\+srv)?)://[^:\s/]+:[^@\s]{6,}@", "a database URL with a password"),
]
PLACEHOLDER = re.compile(r"(x{6,}|your[_-]?(api[_-]?)?key|example|placeholder|dummy|<[^>]+>|\.\.\.)", re.I)


def main():
    data = read_input()
    if project_config(data.get("cwd")).get("secret_guard") == "off":
        sys.exit(0)
    ti = data.get("tool_input") or {}
    path = ti.get("file_path", "")
    base = os.path.basename(path)
    if base.startswith(".env") or base.endswith((".pem", ".key")) and "example" not in base:
        sys.exit(0)
    chunks = [ti.get("content", ""), ti.get("new_string", "")]
    for e in ti.get("edits", []) or []:
        chunks.append(e.get("new_string", ""))
    text = "\n".join(c for c in chunks if c)
    for pat, what in PATTERNS:
        for m in re.finditer(pat, text):
            if PLACEHOLDER.search(m.group(0)):
                continue
            pretool_decision(
                "ask",
                f"Engineering OS secret guard: this writes what looks like {what} into {base or 'a file'}. "
                "Secrets belong in .env (gitignored) or a secret manager, read via env vars.",
            )
    sys.exit(0)


if __name__ == "__main__":
    main()
