#!/bin/bash
# Cloud-session setup: installs the Claude-Mem and claude-code-setup plugins,
# the Graphify CLI (code knowledge graph)
# and the Headroom CLI (context compression proxy). Local machines are left
# alone. Headroom telemetry is switched off for the session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export HEADROOM_BEACON=off' >> "$CLAUDE_ENV_FILE"
fi

export PATH="$HOME/.local/bin:$PATH"

# Plugins declared in .claude/settings.json are not auto-installed in
# non-interactive cloud sessions, so install any that are missing.
if command -v claude >/dev/null 2>&1; then
  installed=$(claude plugin list 2>/dev/null || true)
  for spec in "claude-mem@thedotmack thedotmack/claude-mem" \
              "claude-code-setup@claude-plugins-official anthropics/claude-plugins-official"; do
    set -- $spec
    if ! grep -q "$1" <<<"$installed"; then
      claude plugin marketplace add "$2" >/dev/null 2>&1 || true
      claude plugin install "$1" --scope user >/dev/null 2>&1 \
        || echo "session-setup: failed to install $1" >&2
    fi
  done
fi

# Graphify CLI: the project's PreToolUse hooks and graphify skill call it.
if ! command -v graphify >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    uv tool install graphifyy >/dev/null 2>&1 || echo "session-setup: graphify install failed" >&2
  else
    python3 -m pip install --user graphifyy >/dev/null 2>&1 || echo "session-setup: graphify install failed" >&2
  fi
fi

if command -v headroom >/dev/null 2>&1; then
  exit 0
fi

if command -v uv >/dev/null 2>&1; then
  uv tool install --python 3.13 "headroom-ai[proxy,code,mcp]" >/dev/null 2>&1 \
    || echo "session-setup: uv install failed" >&2
else
  python3 -m pip install --user "headroom-ai[proxy,code,mcp]" >/dev/null 2>&1 \
    || echo "session-setup: pip install failed" >&2
fi
exit 0
