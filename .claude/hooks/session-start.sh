#!/bin/bash
# Prepara las sesiones de Claude Code en la nube para la skill reverse-engineer-anything:
# instala REA y sus motores (scripts/setup-rea-tools.sh) y exporta sus variables.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
source scripts/setup-rea-tools.sh

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export GHIDRA_INSTALL_DIR=\"$GHIDRA_INSTALL_DIR\""
    echo "export REA_PWNTOOLS_PYTHON=\"$REA_PWNTOOLS_PYTHON\""
    echo "export REA_NODE24=\"$REA_NODE24\""
    echo "export REA_BIN=\"$REA_BIN\""
  } >> "$CLAUDE_ENV_FILE"
fi
