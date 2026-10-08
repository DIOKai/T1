#!/bin/sh
# T1 one-line setup for macOS / Linux:
#
#   curl -fsSL https://raw.githubusercontent.com/DIOKai/T1/main/scripts/setup.sh | sh
#
# Clones (or updates) T1 into ~/T1, then runs install_local.py --all --auto-update:
# skills, rules, plugins, MCP servers, Remotion skills, and a SessionStart hook that pulls T1
# each time Claude Code starts so every computer stays in sync.
# Set T1_DIR to use another folder. Safe to run again.
set -eu

T1="${T1_DIR:-$HOME/T1}"
REPO="${T1_REPO:-https://github.com/DIOKai/T1}"
missing=""
command -v git >/dev/null 2>&1 || missing="$missing git"
command -v python3 >/dev/null 2>&1 || missing="$missing python3"
if [ -n "$missing" ]; then
  echo "Missing:$missing  (macOS: xcode-select --install / brew install python; Linux: your package manager)"
  echo "Install them, then run this line again."
  exit 1
fi
command -v claude >/dev/null 2>&1 || echo "Note: the claude CLI is not on PATH, so plugins/MCP will be skipped (skills and rules still install)."
command -v npx >/dev/null 2>&1 || echo "Note: Node.js (npx) not found: Remotion skills and the fivem MCP need it."

if [ -d "$T1/.git" ]; then
  echo "Updating $T1"
  git -C "$T1" pull --ff-only
else
  echo "Downloading T1 into $T1"
  git clone "$REPO" "$T1"
fi

python3 "$T1/scripts/install_local.py" --all --auto-update
echo "Done. Restart Claude Code (desktop app or CLI)."
