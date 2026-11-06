#!/usr/bin/env python3
"""PostToolUse(Write|Edit) autoformat. OPT-IN per project: <project>/.claude/eos.json -> {"autoformat": true}

Only uses formatters the project already has configured, so it never reformats a repo
into a style the team did not choose.
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import project_config, read_input  # noqa: E402

PRETTIER_CFG = (".prettierrc", ".prettierrc.json", ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs",
                ".prettierrc.yaml", ".prettierrc.yml", "prettier.config.js", "prettier.config.mjs", "prettier.config.cjs")
BIOME_CFG = ("biome.json", "biome.jsonc")
JS_EXT = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".css", ".scss", ".md", ".mdx", ".html", ".vue", ".svelte")


def has(root, names):
    return any(os.path.exists(os.path.join(root, n)) for n in names)


def run(cmd, cwd):
    try:
        subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
    except Exception:
        pass


def main():
    data = read_input()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    if not project_config(root).get("autoformat"):
        sys.exit(0)
    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not os.path.isfile(path):
        sys.exit(0)
    local_bin = os.path.join(root, "node_modules", ".bin")
    if path.endswith(JS_EXT):
        if has(root, BIOME_CFG) and os.path.exists(os.path.join(local_bin, "biome")):
            run([os.path.join(local_bin, "biome"), "format", "--write", path], root)
        elif has(root, PRETTIER_CFG) and os.path.exists(os.path.join(local_bin, "prettier")):
            run([os.path.join(local_bin, "prettier"), "--write", path], root)
    elif path.endswith(".py") and shutil.which("ruff") and has(root, ("ruff.toml", ".ruff.toml", "pyproject.toml")):
        run(["ruff", "format", path], root)
    elif path.endswith(".go") and shutil.which("gofmt"):
        run(["gofmt", "-w", path], root)
    elif path.endswith(".rs") and shutil.which("rustfmt"):
        run(["rustfmt", path], root)
    sys.exit(0)


if __name__ == "__main__":
    main()
