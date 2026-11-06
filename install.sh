#!/usr/bin/env bash
# Engineering OS — one-command installer.
#   curl -fsSL https://raw.githubusercontent.com/soummyaanon/engineering-os/main/install.sh | bash
# Options (pass after `bash -s --`):  --all  also install optional skills
# Env: EOS_HOME (default ~/engineering-os), EOS_REPO (default the GitHub repo)
set -euo pipefail

EOS_HOME="${EOS_HOME:-$HOME/engineering-os}"
EOS_REPO="${EOS_REPO:-https://github.com/soummyaanon/engineering-os.git}"
BIN_DIR="${EOS_BIN_DIR:-$HOME/.local/bin}"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[33m!\033[0m %s\n' "$*"; }
die()  { printf '\033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

bold "Engineering OS installer"

# 1. prerequisites
for t in git python3 node npx; do
  command -v "$t" >/dev/null 2>&1 || die "$t is required. Install it first (macOS: brew install ${t/npx/node}; python3 ships with Xcode CLT)."
done
command -v claude >/dev/null 2>&1 || warn "Claude Code CLI not found — install it (https://claude.com/claude-code); skills will still be placed in ~/.claude."
ok "prerequisites"

# 2. get / update the repo
if [ -d "$EOS_HOME/.git" ]; then
  git -C "$EOS_HOME" pull --ff-only -q && ok "updated $EOS_HOME"
elif [ -e "$EOS_HOME" ]; then
  die "$EOS_HOME exists and is not a git checkout. Move it or set EOS_HOME=/other/path."
else
  git clone -q --depth 1 "$EOS_REPO" "$EOS_HOME" && ok "cloned to $EOS_HOME"
fi

# 3. avoid double-loading if the marketplace copy is also installed
if command -v claude >/dev/null 2>&1 && claude plugin list 2>/dev/null | grep -q 'eos@engineering-os'; then
  warn "eos is also installed from the plugin marketplace — removing that copy so it doesn't load twice"
  claude plugin uninstall eos@engineering-os >/dev/null 2>&1 || warn "could not uninstall; run: claude plugin uninstall eos@engineering-os"
fi

# 4. install plugin + hooks + rules + community skills
python3 "$EOS_HOME/bin/eos" install "$@"

# 5. put `eos` on PATH
mkdir -p "$BIN_DIR"
ln -sf "$EOS_HOME/bin/eos" "$BIN_DIR/eos"
case ":$PATH:" in
  *":$BIN_DIR:"*) ok "eos CLI → $BIN_DIR/eos" ;;
  *) warn "add $BIN_DIR to PATH to use the eos CLI:  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.zshrc" ;;
esac

bold "Done. Open a NEW Claude Code session and try:  /eos:map <task>"
