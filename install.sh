#!/usr/bin/env bash
# Engineering OS — one-command installer.
#
#   Claude Code:          curl -fsSL https://raw.githubusercontent.com/soummyaanon/engineering-os/main/install.sh | bash
#   Any other agent:      curl -fsSL …/install.sh | bash -s -- --agent codex     (cursor, gemini-cli, github-copilot, windsurf, opencode, …)
#   Include optional:     … | bash -s -- --all
#
# Env: EOS_HOME (default ~/engineering-os), EOS_REPO (default the GitHub repo)
#
# The whole script lives in main() so bash reads it completely before running anything —
# otherwise child processes could swallow the rest of the script from the curl pipe.

main() {
  set -euo pipefail

  local EOS_HOME="${EOS_HOME:-$HOME/engineering-os}"
  local EOS_REPO="${EOS_REPO:-https://github.com/soummyaanon/engineering-os.git}"
  local BIN_DIR="${EOS_BIN_DIR:-$HOME/.local/bin}"
  local agent="claude-code" prev=""
  for arg in "$@"; do
    [ "$prev" = "--agent" ] && agent="$arg"
    case "$arg" in --agent=*) agent="${arg#--agent=}" ;; esac
    prev="$arg"
  done

  bold() { printf '\033[1m%s\033[0m\n' "$*"; }
  ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
  warn() { printf '\033[33m!\033[0m %s\n' "$*"; }
  die()  { printf '\033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

  bold "Engineering OS installer  (target: $agent)"

  # 1. prerequisites
  local t
  for t in git python3 node npx; do
    command -v "$t" >/dev/null 2>&1 || die "$t is required. Install it first (macOS: 'brew install node' for node/npx; python3 comes with Xcode Command Line Tools)."
  done
  if [ "$agent" = "claude-code" ] && ! command -v claude >/dev/null 2>&1; then
    warn "Claude Code CLI not found (https://claude.com/claude-code) — skills and rules will still be placed in ~/.claude"
  fi
  ok "prerequisites"

  # 2. get / update the repo
  if [ -d "$EOS_HOME/.git" ]; then
    git -C "$EOS_HOME" pull --ff-only -q </dev/null && ok "updated $EOS_HOME"
  elif [ -e "$EOS_HOME" ]; then
    die "$EOS_HOME exists and is not a git checkout. Move it or set EOS_HOME=/other/path."
  else
    git clone -q --depth 1 "$EOS_REPO" "$EOS_HOME" </dev/null && ok "cloned to $EOS_HOME"
  fi

  # 3. avoid double-loading if the marketplace copy is also installed (Claude Code only)
  if [ "$agent" = "claude-code" ] && command -v claude >/dev/null 2>&1 \
     && claude plugin list </dev/null 2>/dev/null | grep -q 'eos@engineering-os'; then
    warn "eos is also installed from the plugin marketplace — removing that copy so it doesn't load twice"
    claude plugin uninstall eos@engineering-os </dev/null >/dev/null 2>&1 || warn "run: claude plugin uninstall eos@engineering-os"
  fi

  # 4. install (plugin + hooks + rules + community skills, or skills + rules for other agents)
  python3 "$EOS_HOME/bin/eos" install "$@" </dev/null

  # 5. put `eos` on PATH
  mkdir -p "$BIN_DIR"
  ln -sf "$EOS_HOME/bin/eos" "$BIN_DIR/eos"
  case ":$PATH:" in
    *":$BIN_DIR:"*) ok "eos CLI → $BIN_DIR/eos" ;;
    *) warn "add $BIN_DIR to PATH for the eos CLI:  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.zshrc" ;;
  esac

  if [ "$agent" = "claude-code" ]; then
    bold "Done. Open a NEW Claude Code session and try:  /eos:map <task>"
  else
    bold "Done. Restart $agent to load the Engineering OS skills."
  fi
}

main "$@"
