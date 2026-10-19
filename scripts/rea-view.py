#!/usr/bin/env python3
"""Proyecta una vista pequeña de un Evidence JSON grande de REA (modo CLI).

El CLI no tiene `--detail summary`; esto envuelve el archivo como fuente
`inline` y llama a `rea inspect-analysis-view`, así el agente nunca carga el
Evidence completo (puede pesar cientos de MB).

Uso:
  rea-view.py EVIDENCE.json summary
  rea-view.py EVIDENCE.json page modules [offset] [limit]
  rea-view.py EVIDENCE.json item modules NODE_ID
"""

import json
import subprocess
import sys
import tempfile


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    evidence_path, kind, *rest = argv[1:]
    if kind == "summary":
        view = {"kind": "summary"}
    elif kind == "page" and rest:
        offset = int(rest[1]) if len(rest) > 1 else 0
        limit = int(rest[2]) if len(rest) > 2 else 16
        view = {"kind": "page", "collection": rest[0], "offset": offset, "limit": limit}
    elif kind == "item" and len(rest) == 2:
        view = {"kind": "item", "collection": rest[0], "selector": {"node_id": rest[1]}}
    else:
        print(__doc__, file=sys.stderr)
        return 2

    with open(evidence_path) as f:
        evidence = json.load(f)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump({"source": {"kind": "inline", "evidence": evidence}, "view": view}, tmp)
    return subprocess.call(["rea", "inspect-analysis-view", tmp.name, "--format", "json"])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
