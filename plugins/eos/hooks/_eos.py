"""Shared helpers for Engineering OS hooks. Stdlib only, Python 3.8+."""
import json
import os
import sys


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_config(cwd):
    """Per-project switches live in <project>/.claude/eos.json, e.g. {"autoformat": true, "guard": "strict"}."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd()
    path = os.path.join(root, ".claude", "eos.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def eos_home():
    """Locate the engineering-os repo (for registry etc). Works when the plugin is symlinked from the repo."""
    env = os.environ.get("EOS_HOME")
    if env and os.path.isdir(env):
        return env
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if root:
        real = os.path.realpath(root)
        cand = os.path.dirname(os.path.dirname(real))
        if os.path.isfile(os.path.join(cand, "registry", "community.json")):
            return cand
    default = os.path.expanduser("~/engineering-os")
    return default if os.path.isdir(default) else None


def pretool_decision(decision, reason):
    """decision: allow | deny | ask"""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


# ---------- update check ----------
LATEST_URL = "https://raw.githubusercontent.com/soummyaanon/engineering-os/main/plugins/eos/.claude-plugin/plugin.json"
CHECK_EVERY = 12 * 3600


def _claude_home():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def update_cache_path():
    return os.path.join(_claude_home(), "eos-update.json")


def local_version():
    root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json")) as f:
            return json.load(f).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


def vtuple(v):
    out = []
    for part in str(v).split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits or 0))
    return tuple(out + [0] * (3 - len(out)))


def refresh_latest():
    """Fetch the latest published version and cache it. Run in the background only."""
    import time
    import urllib.request
    try:
        with urllib.request.urlopen(LATEST_URL, timeout=5) as r:
            latest = json.loads(r.read().decode()).get("version")
        if latest:
            with open(update_cache_path(), "w") as f:
                json.dump({"latest": latest, "checked_at": time.time()}, f)
    except Exception:
        pass


def update_notice():
    """Return (user_message, claude_context) if a newer version is cached; kick off a background refresh when stale."""
    import subprocess
    import time
    if os.environ.get("EOS_UPDATE_CHECK") == "off":
        return None
    cache = {}
    try:
        with open(update_cache_path()) as f:
            cache = json.load(f)
    except Exception:
        pass
    if time.time() - cache.get("checked_at", 0) > CHECK_EVERY:
        try:
            subprocess.Popen([sys.executable, os.path.abspath(__file__), "--refresh"],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except Exception:
            pass
    latest, current = cache.get("latest"), local_version()
    if not latest or vtuple(latest) <= vtuple(current):
        return None
    root = os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    how = ("claude plugin marketplace update engineering-os && claude plugin update eos@engineering-os"
           if os.sep + "plugins" + os.sep + "cache" + os.sep in root else "eos update")
    msg = f"Engineering OS {latest} is available (you have {current}). Update: {how}"
    ctx = (f"An Engineering OS update is available ({current} → {latest}). Tell the user once, briefly, at a natural point: "
           f"run `{how}` in a terminal, then start a new session. Changes: https://github.com/soummyaanon/engineering-os/blob/main/CHANGELOG.md")
    return msg, ctx


if __name__ == "__main__" and "--refresh" in sys.argv:
    refresh_latest()
