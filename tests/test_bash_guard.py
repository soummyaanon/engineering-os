#!/usr/bin/env python3
"""Decision table for the bash guard. Run: python3 tests/test_bash_guard.py (stdlib only)."""
import json
import os
import subprocess
import sys

GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "eos", "hooks", "bash_guard.py")
NL = "\n"

CASES = [
    # catastrophic: always denied, even inside quotes or script bodies
    ("rm -rf ~", "deny"),
    ("rm -rf /", "deny"),
    ('bash -c "rm -rf ~"', "deny"),
    ("python3 - <<'EOF'" + NL + "import os; os.system('rm -rf ~')" + NL + "EOF", "deny"),
    # risky: held for approval
    ("git push --force origin main", "ask"),
    ("git reset --hard HEAD~1", "ask"),
    ("rm -rf ~/projects/old-app", "ask"),
    ("bash <<'EOF'" + NL + "git reset --hard" + NL + "EOF", "ask"),
    ("cat <<'EOF' | sh" + NL + "git push --force origin main" + NL + "EOF", "ask"),
    ("psql $DB <<'EOF'" + NL + "DROP TABLE users;" + NL + "EOF", "ask"),
    ("ssh prod <<'EOF'" + NL + "git reset --hard" + NL + "EOF", "ask"),
    ("python3 - <<'EOF'" + NL + "x = 1" + NL + "EOF" + NL + "git push --force", "ask"),
    # routine, or risky words that are only text (scripts, commit messages, notes)
    ("npm test", "pass"),
    ("rm -rf node_modules", "pass"),
    ("rm -rf /tmp/x", "pass"),
    ("python3 - <<'EOF'" + NL + "s = 'git reset --hard and rm -rf build'" + NL + "EOF", "pass"),
    ("git commit -F - <<'EOF'" + NL + "fix: guard no longer flags force-push text" + NL + "EOF", "pass"),
    ('git commit -m "$(cat <<\'EOF\'' + NL + "docs: mention DROP TABLE and git reset --hard" + NL + "EOF" + NL + ')"', "pass"),
    ("cat > notes.md <<EOF" + NL + "never run git push --force" + NL + "EOF", "pass"),
    ("git commit -F - <<'EOF'" + NL + 'fix: now catches `rm -rf ~` inside quotes (bash -c "rm -rf ~")' + NL + "EOF", "pass"),
    ("cat <<'EOF' | bash" + NL + "rm -rf ~" + NL + "EOF", "deny"),
]


def decide(cmd):
    env = {**os.environ, "EOS_RECEIPTS": "off"}
    out = subprocess.run([sys.executable, GUARD], input=json.dumps({"cwd": "/tmp", "tool_input": {"command": cmd}}),
                         capture_output=True, text=True, env=env).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "pass"


def main():
    failed = 0
    for cmd, want in CASES:
        got = decide(cmd)
        failed += got != want
        print(("ok   " if got == want else "FAIL ") + f"{want:5} got {got:5} | " + cmd.replace(NL, " ⏎ ")[:90])
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
