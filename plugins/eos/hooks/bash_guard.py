#!/usr/bin/env python3
"""PreToolUse(Bash) guard.

DENY  = catastrophic and never what you meant (wiping home/root, fork bombs, disk writes).
ASK   = legitimate but destructive or outward-facing; a human should confirm even in auto mode.
Everything else passes silently.

Patterns are matched case-insensitively; `(?-i:...)` marks the few places where case matters (git branch -D).
`eos redteam` fires a corpus of attacks and look-alikes at this file; keep it at 100% / 0 false alarms.

Escape hatch: set "guard": "off" in <project>/.claude/eos.json, or EOS_GUARD=off in the env.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import pretool_decision, project_config, read_input, redact  # noqa: E402

HOME_OR_ROOT = r"[\"']?(/|~|\$home|\$\{home\})/?\*?[\"']?"

DENY = [
    (r"\brm\s+(-[a-z-]+\s+)*(-[a-z]*r[a-z]*|--recursive)\s+(-[a-z-]+\s+)*" + HOME_OR_ROOT + r"(\s|$|;|&|[`)|'\",])",
     "recursive delete of / or your home directory"),
    (r"\bfind\s+" + HOME_OR_ROOT + r"\s.*(-delete\b|-exec\s+rm\b)", "deleting everything under / or your home directory"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bdd\s+.*\bof=/dev/(disk|sd|nvme|rdisk)", "raw write to a disk device"),
    (r"\bmkfs(\.\w+)?\s", "formatting a filesystem"),
    (r"\bdiskutil\s+(erase|zero|reformat)", "erasing a disk"),
    (r">\s*/dev/(disk|sd|nvme|rdisk)", "redirect onto a disk device"),
]

# a network sender and a credential file (or the whole environment) in the same command
EXFIL = (r"(?s)^(?=.*\b(curl|wget|nc|ncat|netcat|socat|scp|rsync|sftp|ftp)\b)"
         r"(?=.*(\.env\b|\bid_(rsa|ed25519|ecdsa|dsa)\b|\.ssh/|\.aws/credentials|\.netrc|\.npmrc|\.pgpass"
         r"|\.docker/config\.json|\.kube/config|\bprintenv\b|\benv\s*\|))")

ASK = [
    (r"\bgit\s+push\b.*(\s-f\b|--force\b|--force-with-lease\b|\s\+\w)", "force-push rewrites remote history"),
    (r"\bgit\s+push\b.*\b(main|master|production|prod|release)\b", "pushing directly to a protected branch"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards uncommitted work"),
    (r"\bgit\s+clean\s+-[a-z]*f", "git clean -f deletes untracked files"),
    (r"\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)", "discards all local changes"),
    (r"\bgit\s+branch\s+(-\w+\s+)*((?-i:-D)|--delete\s+--force|--force\s+--delete)\b", "force-deletes a branch"),
    (r"\bgit\s+filter-(branch|repo)\b", "rewrites repository history"),
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r|\brm\s+-[rf]\s+-[rf]\b", "recursive force delete"),
    (r"\b(drop\s+(table|database|schema)|truncate\s+table)\b", "destructive SQL"),
    (r"\b(prisma\s+migrate\s+reset|rails\s+db:(drop|reset)|dropdb)\b", "drops/resets a database"),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z)?sh\b|\b((ba|z)?sh|source)\s+<\(\s*(curl|wget)\b"
     r"|\beval\s+[\"']?\$\(\s*(curl|wget)\b", "piping a remote script straight into a shell"),
    (EXFIL, "sending secrets or credentials off the machine"),
    (r"\baws\s+s3\s+(rm\b.*--recursive|rb\b)|\bgsutil\s+(-m\s+)?rm\s+-[a-z]*r|\bgcloud\s.*\bdelete\b|\baz\s+\w.*\bdelete\b",
     "deleting cloud resources"),
    (r"\bchmod\s+(-R\s+)?777\b", "world-writable permissions"),
    (r"\bsudo\b", "running with sudo"),
    (r"\b(npm|pnpm|yarn)\s+publish\b|\bcargo\s+publish\b|\btwine\s+upload\b|\bgem\s+push\b", "publishing a package publicly"),
    (r"\b(vercel|netlify)\b.*--prod\b|\bfly\s+deploy\b|\bterraform\s+(apply|destroy)\b|\bkubectl\s+(delete|apply)\b",
     "deploying / changing live infrastructure"),
    (r"\bgh\s+(repo\s+delete|release\s+delete)\b", "deleting a GitHub repo or release"),
    (r"\bkill\s+-9\s+-1\b|\bkillall\b", "killing many processes"),
]


SAFE_RM_TARGETS = {"node_modules", "dist", "build", "out", ".next", ".nuxt", ".turbo", ".cache", ".parcel-cache",
                   "coverage", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "target", ".venv", "venv",
                   ".svelte-kit", ".vercel", ".expo", "storybook-static", ".output"}


def rm_is_routine(cmd):
    """rm -rf on build artifacts / temp dirs is routine; don't nag about it."""
    if ";" in cmd or "&&" in cmd or "||" in cmd or "|" in cmd:
        return False
    args = [a for a in cmd.split()[1:] if not a.startswith("-")]
    if not args:
        return False
    for a in args:
        a = a.rstrip("/")
        if a.startswith(("/tmp/", "/private/tmp/", "/var/folders/")):
            continue
        if os.path.basename(a) in SAFE_RM_TARGETS and "*" not in a and ".." not in a:
            continue
        return False
    return True


HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
# Heredoc consumers whose body isn't a shell command the agent is running.
# TEXT: the body is plain text (files, commit messages) → ignored by every rule.
# CODE: the body is another language's code → ignored by ASK rules, still scanned by DENY rules (os.system(...)).
_TEXT = r"cat|tee|git\s+commit|gh\s+(pr|issue|release)\s+(create|comment|edit)"
TEXT_CONSUMER = re.compile(rf"^({_TEXT})\b")
CODE_CONSUMER = re.compile(rf"^(python[\d.]*|node|deno|bun|ruby|perl|{_TEXT})\b")
PIPED_TO_SHELL = re.compile(r"\|\s*(sudo\s+)?(ba|z|da|k|fi)?sh\b")
# code that can run a shell command; a script without any of these can only *mention* `rm -rf ~`
RUNS_SHELL = re.compile(r"\bos\.(system|popen|exec\w*|spawn\w*)|\bsubprocess\b|\bchild_process\b|\bexecSync\b|\bspawnSync\b"
                        r"|\bDeno\.(run|Command)\b|\bBun\.(spawn|\$)|\bshell\s*=\s*True|\bsystem\s*\(|\bexec\s*\(|%x|`")


def strip_inert_heredocs(cmd, consumers, code_without_shell=False):
    """Drop heredoc bodies fed to `consumers`; keep those fed to a shell, psql, ssh, etc.

    `python3 - <<'EOF' … EOF` whose script merely *mentions* `git reset --hard` shouldn't trigger an ask.
    With code_without_shell, code bodies (python, node, …) that can't run a shell command are dropped too.
    """
    lines, out, i = cmd.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            seg = re.split(r"&&|\|\||[;&|(`]", line[:m.start()])[-1].split()
            seg = [w for w in seg if not re.match(r"^[A-Za-z_]\w*=", w)]
            if seg:
                seg[0] = os.path.basename(seg[0])
            body = []
            while i < len(lines):
                end = lines[i].lstrip("\t") if m.group(1) else lines[i]
                if end.strip() == m.group(3):
                    break
                body.append(lines[i])
                i += 1
            head = " ".join(seg)
            inert = bool(seg) and not PIPED_TO_SHELL.search(line[m.end():]) and (
                bool(consumers.match(head))
                or (code_without_shell and bool(CODE_CONSUMER.match(head)) and not RUNS_SHELL.search("\n".join(body))))
            if not inert:
                out.extend(body)
            if i < len(lines):  # closing delimiter line (may continue the command, e.g. `EOF\n)" && git push`)
                out.append(lines[i])
                i += 1
    return "\n".join(out)


# Commands whose quoted arguments are text, not commands: `git commit -m "fix rm -rf bug"`, `grep -r "DROP TABLE"`.
TEXT_ARGS = re.compile(r"^(echo|printf|grep|egrep|fgrep|rg|ag|ack|git\s+(commit|grep|log|tag|stash))\b")
# single-quoted strings never expand; double-quoted ones only count as text when they hold no $ or backtick
QUOTED = re.compile(r"'[^']*'|\"(?:[^\"\\`$]|\\[^`$])*\"")


def _segments(cmd):
    """(start, end) spans of simple commands: split on unquoted ; & | and newlines."""
    spans, start, quote, i = [], 0, None, 0
    while i < len(cmd):
        ch = cmd[i]
        if ch == "\\" and quote != "'":
            i += 2
            continue
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch in ";&|\n":
            spans.append((start, i))
            start = i + 1
        i += 1
    spans.append((start, len(cmd)))
    return spans


def strip_text_args(cmd):
    """Blank the quoted arguments of text-only commands. Leaves everything alone if the output feeds a shell."""
    if PIPED_TO_SHELL.search(cmd) or re.search(r"\beval\b", cmd):
        return cmd
    out, last = [], 0
    for a, b in _segments(cmd):
        seg = cmd[a:b]
        words = [w for w in seg.split() if not re.match(r"^[A-Za-z_]\w*=", w)]
        if words:
            words[0] = os.path.basename(words[0])
        if words and TEXT_ARGS.match(" ".join(words)):
            seg = QUOTED.sub("''", seg)
        out.append(cmd[last:a] + seg)
        last = b
    # `rsync --exclude .env` names a file in order to leave it behind
    return re.sub(r"--exclude(-from)?(=|\s+)\S+", "", "".join(out) + cmd[last:])


def main():
    data = read_input()
    if os.environ.get("EOS_GUARD") == "off" or project_config(data.get("cwd")).get("guard") == "off":
        sys.exit(0)
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not cmd:
        sys.exit(0)
    receipt = {"guard": "bash", "cmd": redact(cmd), "project": os.path.basename(data.get("cwd") or "")}
    view = strip_text_args(strip_inert_heredocs(cmd, TEXT_CONSUMER, code_without_shell=True))
    for pat, why in DENY:  # catastrophic: check everything but plain text, and script bodies that can run a shell
        if re.search(pat, view, re.I):
            pretool_decision("deny", f"Engineering OS guard blocked this: {why}. If you truly need it, run it yourself.",
                             {**receipt, "why": why})
    view = strip_text_args(strip_inert_heredocs(cmd, CODE_CONSUMER))
    for pat, why in ASK:
        if re.search(pat, view, re.I):
            if why == "recursive force delete" and rm_is_routine(cmd.strip()):
                continue
            pretool_decision("ask", f"Engineering OS guard: {why}. Confirm this is intended.", {**receipt, "why": why})
    sys.exit(0)


if __name__ == "__main__":
    main()
