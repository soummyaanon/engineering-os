#!/usr/bin/env python3
"""eos score — grade a coding-agent setup (Claude Code) like Lighthouse grades a web page.

Read-only and local: it reads ~/.claude and the current project, prints a report, and sends nothing anywhere.
Works without Engineering OS installed:

    curl -fsSL https://engineering-os-hazel.vercel.app/score | python3 -

Options: --json · --card [PATH] (shareable SVG/PNG) · --badge (README badge markdown) · --project DIR
Stdlib only, Python 3.8+.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse

SITE = "https://engineering-os-hazel.vercel.app"
REPO = "https://github.com/soummyaanon/engineering-os"
INSTALL = f"curl -fsSL {SITE.replace('https://', '')}/install | bash"
SCORE_CMD = f"curl -fsSL {SITE.replace('https://', '')}/score | python3 -"

CLAUDE_HOME = os.environ.get("CLAUDE_CONFIG_DIR") or os.environ.get("CLAUDE_HOME") or os.path.expanduser("~/.claude")
RECEIPTS = os.path.join(CLAUDE_HOME, "eos-receipts.jsonl")

TTY = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
def c(code, s): return f"\033[{code}m{s}\033[0m" if TTY else s


# ---------- reading the setup ----------
def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def read_text(path, limit=400_000):
    try:
        with open(path, errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""

def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---", read_text(path, 20_000), re.S)
    if not m:
        return {}
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, _, v = line.partition(":")
            key, v = k.strip(), v.strip()
            fm[key] = "" if v in (">", "|", ">-", "|-") else v
        elif key and line.strip() and line.startswith((" ", "\t")):  # YAML continuation / block scalar
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm

def with_imports(path, depth=0):
    """CLAUDE.md text with its @path imports inlined (two levels, like Claude Code)."""
    txt = read_text(path)
    if depth >= 2:
        return txt
    out = [txt]
    for m in re.finditer(r"^@(\S+)\s*$", txt, re.M):
        p = os.path.expanduser(m.group(1))
        if not os.path.isabs(p):
            p = os.path.join(os.path.dirname(path), p)
        if os.path.isfile(p):
            out.append(with_imports(p, depth + 1))
    return "\n".join(out)


class Setup:
    """Everything the checks need, gathered once."""

    def __init__(self, project):
        self.project = project
        self.settings = [read_json(os.path.join(CLAUDE_HOME, n)) for n in ("settings.json", "settings.local.json")] + \
                        [read_json(os.path.join(project, ".claude", n)) for n in ("settings.json", "settings.local.json")]
        self.plugin_roots = self._plugin_roots()
        self.hooks = self._hooks()
        self.skills = self._skills()

    def setting(self, *keys):
        """Last non-empty value wins (project overrides user)."""
        val = None
        for s in self.settings:
            cur = s
            for k in keys:
                cur = cur.get(k) if isinstance(cur, dict) else None
            if cur not in (None, "", [], {}):
                val = cur
        return val

    def _plugin_roots(self):
        """(name, root) for every enabled marketplace plugin and every plugin linked into ~/.claude/skills."""
        enabled = {}
        for s in self.settings:
            for k, v in (s.get("enabledPlugins") or {}).items():
                enabled[k] = v
        installed = read_json(os.path.join(CLAUDE_HOME, "plugins", "installed_plugins.json"))
        installed = installed.get("plugins", installed) if isinstance(installed, dict) else {}
        roots = []
        for key, on in enabled.items():
            if not on:
                continue
            recs = installed.get(key) or []
            recs = recs if isinstance(recs, list) else [recs]
            for r in recs:
                p = isinstance(r, dict) and r.get("installPath")
                if p and os.path.isdir(p):
                    roots.append((key, p))
                    break
        sdir = os.path.join(CLAUDE_HOME, "skills")
        for d in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
            p = os.path.join(sdir, d)
            if os.path.isfile(os.path.join(p, ".claude-plugin", "plugin.json")):
                roots.append((d, os.path.realpath(p)))
        return roots

    def _hooks(self):
        """List of (event, matcher, command, source)."""
        out = []

        def collect(spec, source):
            for event, groups in ((spec or {}).get("hooks") or {}).items():
                for g in groups if isinstance(groups, list) else []:
                    for h in g.get("hooks") or []:
                        out.append((event, str(g.get("matcher", "") or ""), str(h.get("command", "") or h.get("prompt", "")), source))

        for i, s in enumerate(self.settings):
            collect(s, "user settings" if i < 2 else "project settings")
        for name, root in self.plugin_roots:
            collect(read_json(os.path.join(root, "hooks", "hooks.json")), name)
            manifest = read_json(os.path.join(root, ".claude-plugin", "plugin.json"))
            h = manifest.get("hooks")
            if isinstance(h, dict):
                collect({"hooks": h} if "hooks" not in h else h, name)
            elif isinstance(h, str):
                collect(read_json(os.path.join(root, h)), name)
        return out

    def _skills(self):
        """name -> SKILL.md path for every skill Claude Code would list."""
        found = {}

        def scan(d):
            for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                p = os.path.join(d, n, "SKILL.md")
                if not n.startswith(".") and os.path.isfile(p):
                    found.setdefault(n, p)

        scan(os.path.join(CLAUDE_HOME, "skills"))
        scan(os.path.join(self.project, ".claude", "skills"))
        for _, root in self.plugin_roots:
            scan(os.path.join(root, "skills"))
        return found

    def hook_for(self, event, tool):
        for ev, matcher, cmd, src in self.hooks:
            if ev != event:
                continue
            if matcher in ("", "*"):
                return src
            try:
                if re.fullmatch(matcher, tool) or re.search(rf"(^|\|){re.escape(tool)}($|\|)", matcher):
                    return src
            except re.error:
                if tool in matcher:
                    return src
        return None

    def has_skill(self, *needles):
        return [n for n in self.skills if any(x in n.lower() for x in needles)]


# ---------- stack detection (compact; mirrors the session briefing) ----------
STACK = {  # label: (package.json deps, python deps, files, skill-name needles that cover it)
    "Next.js": (["next"], [], [], ["next", "react"]),
    "React": (["react"], [], [], ["react"]),
    "Vue": (["vue"], [], [], ["vue"]),
    "Svelte": (["svelte"], [], [], ["svelte"]),
    "Tailwind": (["tailwindcss"], [], [], ["tailwind"]),
    "Expo / React Native": (["expo", "react-native"], [], [], ["expo", "react-native"]),
    "Prisma": (["prisma", "@prisma/client"], [], [], ["prisma"]),
    "Supabase": (["@supabase/supabase-js"], ["supabase"], ["supabase"], ["supabase"]),
    "Stripe": (["stripe"], ["stripe"], [], ["stripe"]),
    "Better Auth": (["better-auth"], [], [], ["better-auth", "auth"]),
    "Anthropic SDK": (["@anthropic-ai/sdk"], ["anthropic"], [], ["claude-api", "anthropic"]),
    "Vercel AI SDK": (["ai"], [], [], ["ai-sdk"]),
    "MCP": (["@modelcontextprotocol/sdk"], ["mcp"], [], ["mcp"]),
    "FastAPI": ([], ["fastapi"], [], ["fastapi"]),
    "Django": ([], ["django"], [], ["django"]),
    "Playwright": (["@playwright/test", "playwright"], ["playwright"], [], ["playwright", "e2e", "webapp-testing"]),
    "Docker": ([], [], ["Dockerfile"], ["docker"]),
    "GitHub Actions": ([], [], [".github/workflows"], ["github-actions"]),
    "Vercel": ([], [], ["vercel.json"], ["vercel"]),
    "Terraform": ([], [], ["main.tf"], ["terraform"]),
}

def detect_stack(root):
    pkg = read_json(os.path.join(root, "package.json"))
    deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})} if isinstance(pkg, dict) else {}
    py = (read_text(os.path.join(root, "pyproject.toml")) + read_text(os.path.join(root, "requirements.txt"))).lower()
    out = []
    for label, (js, pyd, files, _) in STACK.items():
        if any(d in deps for d in js) or any(re.search(rf"(^|[\s\"'=<>~]){re.escape(d)}\b", py, re.M) for d in pyd) \
                or any(os.path.exists(os.path.join(root, f)) for f in files):
            out.append(label)
    return out


# ---------- checks ----------
INJECTION = [
    (r"ignore (all )?(previous|prior) instructions", "prompt-injection phrasing"),
    (r"(nc|ncat)\s+-e\s|/dev/tcp/\d", "reverse-shell pattern"),
    (r"eval\s*\(\s*(atob|Buffer\.from)", "obfuscated eval"),
]

def check(cat, cid, title, pts, earned, detail, fix="", eos_fixes=False):
    return {"category": cat, "id": cid, "title": title, "max": pts, "earned": round(max(0, min(pts, earned)), 1),
            "detail": detail, "fix": fix, "eos_fixes": eos_fixes}

def run_checks(s):
    out = []
    G, R, K, L = "Guardrails", "Working rules", "Skills", "Feedback loops"

    # --- Guardrails (35)
    src = s.hook_for("PreToolUse", "Bash")
    deny = [r for r in (s.setting("permissions", "deny") or []) if str(r).startswith("Bash")]
    if src:
        out.append(check(G, "bash-guard", "Destructive commands are guarded", 15, 15, f"PreToolUse(Bash) hook from {src}"))
    else:
        out.append(check(G, "bash-guard", "Destructive commands are guarded", 15, 7 if deny else 0,
                         f"{len(deny)} Bash deny rule(s), no guard hook" if deny else
                         "nothing stops the agent running rm -rf ~, git push --force, DROP TABLE…",
                         "add a PreToolUse(Bash) guard hook", True))
    src = s.hook_for("PreToolUse", "Write") or s.hook_for("PreToolUse", "Edit")
    out.append(check(G, "secret-guard", "Secrets can't be written into source", 10, 10 if src else 0,
                     f"PreToolUse(Write/Edit) hook from {src}" if src else "API keys can land in committed files unnoticed",
                     "add a PreToolUse(Write|Edit) secret guard", True))
    mode = s.setting("permissions", "defaultMode") or "default"
    skip = bool(s.setting("skipDangerousModePermissionPrompt"))
    risky = mode == "bypassPermissions" or skip
    out.append(check(G, "permission-mode", "Permissions aren't bypassed by default", 10, 0 if risky else 10,
                     f"defaultMode: {mode}" + (" + dangerous-mode prompt skipped" if skip else ""),
                     "don't default to bypassPermissions; use auto mode with guards instead"))

    # --- Working rules (20)
    gpath = os.path.join(CLAUDE_HOME, "CLAUDE.md")
    rules = with_imports(gpath) if os.path.isfile(gpath) else ""
    words = len(re.findall(r"\w+", rules))
    out.append(check(R, "global-rules", "Global working rules exist", 8, 8 if words >= 150 else 4 if words >= 30 else 0,
                     f"~/.claude/CLAUDE.md: {words} words (imports included)" if rules else "no ~/.claude/CLAUDE.md",
                     "write global rules: how to verify, git safety, code quality", True))
    low = rules.lower()
    verify = bool(re.search(r"\b(verif|evidence|run (the )?tests|tests? pass)", low))
    git = bool(re.search(r"force[- ]push|--no-verify|commit only|never push|don't push", low))
    out.append(check(R, "rule-coverage", "Rules require verification and git safety", 6, 3 * verify + 3 * git,
                     ", ".join(x for x in ["verification rule" if verify else "no verification rule",
                                           "git-safety rule" if git else "no git-safety rule"]),
                     "add rules: evidence before 'done'; never force-push or skip hooks unasked", True))
    is_repo = os.path.isdir(os.path.join(s.project, ".git"))
    if is_repo:
        has = [f for f in ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md") if os.path.isfile(os.path.join(s.project, f))]
        out.append(check(R, "project-rules", "This repo has project instructions", 6, 6 if has else 0,
                         ", ".join(has) if has else f"no CLAUDE.md in {os.path.basename(s.project)}",
                         "run /init in Claude Code to create one"))

    # --- Skills (30)
    n = len(s.skills)
    process = {"debugging": s.has_skill("debug"), "verification / TDD": s.has_skill("verif", "test-driven", "tdd"),
               "code review": s.has_skill("review")}
    got = [k for k, v in process.items() if v]
    out.append(check(K, "process-skills", "Process skills: debugging, verification, review", 8, 8 * len(got) / 3,
                     ("has " + ", ".join(got)) if got else "none of debugging / verification / review",
                     "install process skills (systematic debugging, verification, code review)", True))
    stack = detect_stack(s.project)
    if stack:
        covered = [x for x in stack if s.has_skill(*STACK[x][3])]
        missing = [x for x in stack if x not in covered]
        out.append(check(K, "stack-coverage", "Skills cover this project's stack", 10, 10 * len(covered) / len(stack),
                         f"{len(covered)}/{len(stack)} covered" + (f"; missing: {', '.join(missing)}" if missing else ""),
                         "add skills from the vendors behind your stack (" + ", ".join(missing[:4]) + ")", True))
    pts = 6 if 5 <= n <= 120 else 3 if n <= 200 and n > 0 else 0
    out.append(check(K, "skill-load", "Skill count is useful, not overwhelming", 6, pts,
                     f"{n} skills visible to the agent" + (" (too many: it picks worse)" if n > 120 else " (too few)" if n < 5 else ""),
                     "route through playbooks and keep rarely-used skills off" if n > 120 else "install a curated core set",
                     n < 5))
    broken, flagged = [], []
    for name, path in s.skills.items():
        fm = frontmatter(path)
        if not fm.get("description"):
            broken.append(name)
        txt = read_text(path, 200_000).lower()
        for pat, why in INJECTION:
            if re.search(pat, txt):
                flagged.append(f"{name} ({why})")
    if n:
        out.append(check(K, "skill-hygiene", "Skills are well-formed and clean", 6, 6 - 2 * len(broken) - 3 * len(flagged),
                         "; ".join(filter(None, [f"no description: {', '.join(broken[:4])}" if broken else "",
                                                 f"suspicious: {', '.join(flagged[:3])}" if flagged else ""])) or f"{n} skills checked",
                         "fix or remove the skills listed"))

    # --- Feedback loops (15)
    src = s.hook_for("PostToolUse", "Edit") or s.hook_for("PostToolUse", "Write")
    out.append(check(L, "format-hook", "Edits are auto-formatted or linted", 5, 5 if src else 0,
                     f"PostToolUse(Edit) hook from {src}" if src else "no format/lint hook after edits",
                     "add a PostToolUse(Edit|Write) formatter hook", True))
    src = s.hook_for("SessionStart", "startup")
    out.append(check(L, "session-context", "Sessions start with project context", 5, 5 if src else 0,
                     f"SessionStart hook from {src}" if src else "the agent starts every session cold",
                     "add a SessionStart hook that briefs the agent on the stack", True))
    user_cfg = os.path.join(os.environ["CLAUDE_CONFIG_DIR"], ".claude.json") if os.environ.get("CLAUDE_CONFIG_DIR") \
        else os.path.expanduser("~/.claude.json")
    mcp = set((read_json(user_cfg).get("mcpServers") or {}).keys()) | \
          set((read_json(os.path.join(s.project, ".mcp.json")).get("mcpServers") or {}).keys())
    out.append(check(L, "mcp-load", "MCP servers are kept lean", 5, 5 if len(mcp) <= 8 else 2 if len(mcp) <= 15 else 0,
                     f"{len(mcp)} MCP server(s) configured", "disable MCP servers you don't use every week"))
    return out


# ---------- scoring ----------
GRADES = [(95, "A+"), (90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")]
COLORS = {"A": "#5bb974", "B": "#a88bfa", "C": "#e0a53b", "D": "#e5484d", "F": "#e5484d"}
TERM = {"A": "32", "B": "35", "C": "33", "D": "31", "F": "31"}

def summarize(checks):
    cats = {}
    for ch in checks:
        e, m = cats.get(ch["category"], (0, 0))
        cats[ch["category"]] = (e + ch["earned"], m + ch["max"])
    earned = sum(e for e, _ in cats.values())
    total = sum(m for _, m in cats.values())
    score = round(100 * earned / total) if total else 0
    grade = next(g for t, g in GRADES if score >= t)
    return {"score": score, "grade": grade,
            "categories": {k: round(100 * e / m) for k, (e, m) in cats.items()}}

def receipts_count(days=30):
    since, n = time.time() - days * 86400, 0
    for line in read_text(RECEIPTS, 2_000_000).splitlines():
        try:
            n += json.loads(line).get("ts", 0) >= since
        except Exception:
            pass
    return n

def eos_installed():
    return os.path.isfile(os.path.join(CLAUDE_HOME, "skills", "eos", ".claude-plugin", "plugin.json")) or \
        "eos@engineering-os" in json.dumps(read_json(os.path.join(CLAUDE_HOME, "settings.json")).get("enabledPlugins") or {})


# ---------- output ----------
def bar(pct, width=20):
    full = round(pct / 100 * width)
    return "█" * full + c("2", "░" * (width - full))

def badge_url(summary):
    g = summary["grade"]
    label = urllib.parse.quote(f"{g} · {summary['score']}")
    return f"https://img.shields.io/badge/agent%20setup-{label}-{COLORS[g[0]].lstrip('#')}?style=flat-square&labelColor=161618"

def badge_md(summary):
    return f"[![agent setup: {summary['grade']}]({badge_url(summary)})]({SITE}/#score)"

def share_text(summary):
    return (f"My coding agent setup scored {summary['grade']} ({summary['score']}/100) on eos score.\n\n"
            f"Score yours in 5 seconds, nothing leaves your machine:\n{SCORE_CMD}")

def print_report(checks, summary):
    g = summary["grade"]
    col = TERM[g[0]]
    print()
    print(c("1", "  eos score") + c("2", "  ·  your coding agent setup, graded"))
    print()
    print("  " + c("1;" + col, f"{g:<3}") + "  " + c("1", f"{summary['score']}/100"))
    print()
    for cat, pct in summary["categories"].items():
        print(f"  {cat:<15} {bar(pct)} {pct:>3}%")
    current = None
    for ch in checks:
        if ch["category"] != current:
            current = ch["category"]
            print("\n  " + c("1", current))
        full = ch["earned"] >= ch["max"]
        mark = c("32", "✓") if full else c("33", "◐") if ch["earned"] > 0 else c("31", "✗")
        print(f"  {mark} {ch['title']}  " + c("2", f"{ch['earned']:g}/{ch['max']}  {ch['detail']}"))
    gaps = sorted([ch for ch in checks if ch["earned"] < ch["max"]], key=lambda x: x["earned"] - x["max"])
    if gaps:
        print("\n  " + c("1", "Biggest wins"))
        for ch in gaps[:5]:
            print(f"  +{ch['max'] - ch['earned']:<4g} {ch['fix']}")
        if any(ch["eos_fixes"] for ch in gaps) and not eos_installed():
            print("\n  " + c("1", "Most of these in one command:") + f"  {INSTALL}")
    n = receipts_count()
    if n:
        print("\n  " + c("1", f"Guards stopped {n} risky action{'s' * (n != 1)} in the last 30 days") + c("2", "  →  eos receipts"))
    print("\n  " + c("2", "Share it:") + "  eos score --card   " + c("2", "README badge:") + "  eos score --badge")
    print("  " + c("2", "Read-only and local. Nothing was sent anywhere."))
    print()


# ---------- shareable card ----------
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_frame(body, footer):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#161618"/>
<rect x="24" y="24" width="1152" height="582" rx="14" fill="#1c1c1f" stroke="#2e2e33" stroke-width="2"/>
<g font-family="JetBrains Mono, SF Mono, Menlo, monospace">{body}
<text x="72" y="566" font-size="22" fill="#6f6f78">{esc(footer)}</text>
<text x="1128" y="104" font-size="24" fill="#a88bfa" text-anchor="end">engineering os</text>
</g></svg>"""

def score_svg(summary):
    g = summary["grade"]
    col = COLORS[g[0]]
    body = [f'<text x="72" y="104" font-size="26" fill="#6f6f78">my coding agent setup</text>',
            f'<text x="60" y="350" font-size="240" font-weight="700" fill="{col}">{esc(g)}</text>',
            f'<text x="80" y="430" font-size="44" font-weight="700" fill="#dcdcdf">{summary["score"]}/100</text>']
    y = 190
    for cat, pct in summary["categories"].items():
        body += [f'<text x="600" y="{y}" font-size="26" fill="#dcdcdf">{esc(cat)}</text>',
                 f'<text x="1128" y="{y}" font-size="26" fill="#6f6f78" text-anchor="end">{pct}%</text>',
                 f'<rect x="600" y="{y + 16}" width="528" height="12" rx="6" fill="#26262a"/>',
                 f'<rect x="600" y="{y + 16}" width="{round(528 * pct / 100)}" height="12" rx="6" fill="{col}"/>']
        y += 84
    return svg_frame("\n".join(body), f"score yours: {SCORE_CMD}")

BROWSERS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]

def write_card(svg, path):
    """Write the SVG, and a PNG next to it when the machine can render one (X and LinkedIn don't take SVG)."""
    path = os.path.abspath(path)
    with open(path, "w") as f:
        f.write(svg)
    png = os.path.splitext(path)[0] + ".png"
    if os.path.exists(png):
        os.remove(png)
    try:
        if shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630", "-o", png, path], capture_output=True, timeout=30)
        else:
            exe = next((b for b in BROWSERS if shutil.which(b) or os.path.isfile(b)), None)
            if exe:
                subprocess.run([shutil.which(exe) or exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                "--window-size=1200,630", f"--screenshot={png}", "file://" + path],
                               capture_output=True, timeout=60)
    except Exception:
        pass
    return path, (png if os.path.isfile(png) else None)


# ---------- receipts: what the guards stopped ----------
SHORT = {
    "recursive delete of / or your home directory": "rm -rf on home or /",
    "force-push rewrites remote history": "force-push",
    "pushing directly to a protected branch": "push straight to main",
    "git reset --hard discards uncommitted work": "git reset --hard",
    "git clean -f deletes untracked files": "git clean -f",
    "discards all local changes": "discard all local changes",
    "recursive force delete": "rm -rf",
    "destructive SQL": "DROP / TRUNCATE",
    "drops/resets a database": "database reset",
    "piping a remote script straight into a shell": "curl | sh",
    "publishing a package publicly": "public package publish",
    "deploying / changing live infrastructure": "prod deploy / infra change",
}

def label(r):
    why = r.get("why", "?")
    if r.get("guard") == "secret":
        return re.sub(r"^(a|an) ", "", why) + " in code"
    return SHORT.get(why, why)

def load_receipts(days):
    since, out = time.time() - days * 86400, []
    for line in read_text(RECEIPTS, 2_000_000).splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("ts", 0) >= since:
            out.append(r)
    return out

def tally(rs):
    counts = {}
    for r in rs:
        counts[label(r)] = counts.get(label(r), 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])

def period(days):
    return "this week" if days == 7 else "today" if days == 1 else f"in the last {days} days"

def receipts_share(rs, days):
    lines = "\n".join(f"• {n}× {k}" for k, n in tally(rs)[:4])
    return (f"{period(days).capitalize()} my coding agent tried {len(rs)} risky thing{'s' * (len(rs) != 1)}. "
            f"Engineering OS caught every one before it ran:\n{lines}\n\n"
            f"Guardrails for Claude Code, one command: {SITE}")

def receipts_svg(rs, days):
    body = [f'<text x="72" y="104" font-size="26" fill="#6f6f78">{esc(period(days))}, my coding agent tried</text>',
            f'<text x="64" y="300" font-size="200" font-weight="700" fill="#e0a53b">{len(rs)}</text>',
            f'<text x="72" y="370" font-size="34" font-weight="700" fill="#dcdcdf">risky thing{"s" * (len(rs) != 1)}.</text>',
            '<text x="72" y="420" font-size="34" font-weight="700" fill="#5bb974">all caught before they ran.</text>']
    y = 190
    for k, n in tally(rs)[:5]:
        k = k if len(k) <= 24 else k[:23] + "…"
        body += [f'<text x="1128" y="{y}" font-size="28" fill="#e0a53b" font-weight="700" text-anchor="end">{n}×</text>',
                 f'<text x="700" y="{y}" font-size="26" fill="#dcdcdf">{esc(k)}</text>']
        y += 62
    return svg_frame("\n".join(body), f"guardrails for your coding agent: {SITE.replace('https://', '')}")

def receipts_main(argv=None):
    ap = argparse.ArgumentParser(prog="eos receipts", description="What the Engineering OS guards stopped (local log).")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--card", nargs="?", const="eos-receipts.svg", metavar="PATH", help="write a shareable card")
    ap.add_argument("--share", action="store_true", help="print a ready-to-post summary")
    a = ap.parse_args(argv)
    rs = load_receipts(a.days)
    if a.json:
        print(json.dumps({"days": a.days, "total": len(rs), "by_kind": dict(tally(rs)), "receipts": rs}, indent=2))
        return
    print()
    print(c("1", "  eos receipts") + c("2", f"  ·  {period(a.days)}"))
    print()
    if not rs:
        print("  Nothing risky caught " + period(a.days) + ". The guards are watching." if os.path.exists(RECEIPTS) else
              "  No receipts yet. They appear when the Engineering OS guards block or pause a risky action.")
        print()
        return
    blocked = sum(r.get("decision") == "deny" for r in rs)
    print("  " + c("1;33", str(len(rs))) + c("1", f" risky action{'s' * (len(rs) != 1)} caught before running") +
          c("2", f"   {blocked} blocked · {len(rs) - blocked} held for your OK"))
    print()
    for k, n in tally(rs):
        print(f"  {n:>3}×  {k}")
    print("\n  " + c("1", "Latest"))
    for r in rs[-8:][::-1]:
        when = time.strftime("%b %d %H:%M", time.localtime(r.get("ts", 0)))
        what = r.get("cmd") or r.get("file") or ""
        tag = c("31", "blocked") if r.get("decision") == "deny" else c("33", "held   ")
        print(f"  {c('2', when)}  {tag}  {label(r)}" + c("2", f"  {what}  {r.get('project', '')}"))
    print("\n  " + c("2", "Share it:") + "  eos receipts --card   " + c("2", "or") + "  eos receipts --share")
    print("  " + c("2", f"Local log: {RECEIPTS} (secrets are never written to it)"))
    print()
    if a.card:
        svg, png = write_card(receipts_svg(rs, a.days), a.card)
        print(f"  card: {png or svg}")
    if a.card or a.share:
        print("  post: https://x.com/intent/post?text=" + urllib.parse.quote(receipts_share(rs, a.days)))
        if a.share:
            print("\n" + receipts_share(rs, a.days))
        print()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="eos score", description="Grade your coding agent setup (read-only, local).")
    ap.add_argument("--project", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), help="project to score (default: cwd)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--card", nargs="?", const="eos-score.svg", metavar="PATH", help="write a shareable card (SVG, plus PNG when possible)")
    ap.add_argument("--badge", action="store_true", help="print README badge markdown")
    a = ap.parse_args(argv)
    checks = run_checks(Setup(os.path.abspath(a.project)))
    summary = summarize(checks)
    if a.json:
        print(json.dumps({**summary, "checks": checks, "receipts_30d": receipts_count()}, indent=2))
        return summary
    if a.badge:
        print(badge_md(summary))
        return summary
    print_report(checks, summary)
    if a.card:
        svg, png = write_card(score_svg(summary), a.card)
        print(f"  card: {png or svg}")
        print("  post: https://x.com/intent/post?text=" + urllib.parse.quote(share_text(summary)))
        print()
    return summary


if __name__ == "__main__":
    if sys.argv[1:2] == ["receipts"]:
        receipts_main(sys.argv[2:])
    else:
        main(sys.argv[2:] if sys.argv[1:2] == ["score"] else None)
