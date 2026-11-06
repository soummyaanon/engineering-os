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
