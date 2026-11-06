#!/usr/bin/env python3
"""Notification hook: macOS desktop notification when Claude needs you. Disable with EOS_NOTIFY=off."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import read_input  # noqa: E402


def main():
    if os.environ.get("EOS_NOTIFY") == "off" or sys.platform != "darwin":
        sys.exit(0)
    data = read_input()
    msg = (data.get("message") or "Claude needs your attention").replace('"', "'")[:180]
    proj = os.path.basename(data.get("cwd") or os.getcwd()).replace('"', "'")
    try:
        subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "Claude · {proj}"'],
                       timeout=4, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
