#!/usr/bin/env bash
# Instala REA y sus motores en un contenedor Linux (sesiones de Claude Code en la nube).
# Uso:  source scripts/setup-rea-tools.sh    (deja exportadas las variables de entorno)
# Idempotente: lo ya instalado se reutiliza. Versiones fijadas y validadas juntas.
set -uo pipefail

TOOLS="${REA_TOOLS_DIR:-/opt/rea-tools}"
REA_VERSION=6.7.0
GHIDRA_VERSION=12.1.4
GHIDRA_DATE=20260921
mkdir -p "$TOOLS"

# 1. REA CLI + servidor MCP
command -v rea >/dev/null && [[ "$(rea --version 2>/dev/null | tail -1)" == "$REA_VERSION" ]] ||
  npm i -g "rea-agents@$REA_VERSION" >/dev/null 2>&1

# 2. Ghidra 12.1.x (descompilación nativa; requiere Java 21)
GHIDRA_DIR="$TOOLS/ghidra_${GHIDRA_VERSION}_PUBLIC"
if [[ ! -d "$GHIDRA_DIR" ]]; then
  curl -sSL -o "$TOOLS/ghidra.zip" \
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_${GHIDRA_DATE}.zip" &&
    unzip -q "$TOOLS/ghidra.zip" -d "$TOOLS" && rm -f "$TOOLS/ghidra.zip"
fi

# 3. pwntools 4.15.0 + pyelftools 0.33 + Unicorn 2.1.2 (inspect-binary-layout)
python3 -c "import pwn" 2>/dev/null ||
  pip install -q "pwntools==4.15.0" "pyelftools==0.33" "unicorn==2.1.2" 2>/dev/null

# 4. Node 24.15+ solo para inspect-sqlite-database (Node 22 no trae DatabaseSync.limits)
[[ -x "$TOOLS/node24/node_modules/.bin/node" ]] ||
  (mkdir -p "$TOOLS/node24" && cd "$TOOLS/node24" && npm i -q node@24 >/dev/null 2>&1)

export GHIDRA_INSTALL_DIR="$GHIDRA_DIR"
export REA_PWNTOOLS_PYTHON="$(command -v python3)"
export REA_NODE24="$TOOLS/node24/node_modules/.bin/node"
export REA_BIN="$(readlink -f "$(command -v rea)")"

echo "rea $(rea --version 2>/dev/null | tail -1) | ghidra $([[ -d $GHIDRA_DIR ]] && echo ok || echo FALTA)" \
  "| pwntools $(python3 -c 'import pwn;print(pwn.version)' 2>/dev/null || echo FALTA)" \
  "| node24 $("$REA_NODE24" --version 2>/dev/null || echo FALTA)"
