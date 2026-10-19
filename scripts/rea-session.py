#!/usr/bin/env python3
"""Ejecuta varias herramientas de REA en UNA sesión MCP (stdio) y guarda cada resultado.

Con el CLI cada consulta nativa reimporta el binario en Ghidra (~16 s). En una
sesión MCP solo la primera consulta paga ese coste; las siguientes tardan ~0,1 s.

Uso:
  rea-session.py PLAN.json OUT_DIR

PLAN.json es una lista de llamadas, en orden:
  [
    {"tool": "open_binary", "args": {"path": "/abs/bin", "provider_id": "ghidra"}},
    {"tool": "analyze_function", "args": {"procedure": "main"}, "name": "main"},
    {"tool": "search_strings", "args": {"pattern": "license"}},
    {"tool": "close_binary", "args": {}}
  ]

Cada resultado se escribe en OUT_DIR/<NN>-<name|tool>.json y por pantalla solo
sale una línea resumen (tiempo, error, evidence_id, tamaño): el contenido
completo nunca entra en el contexto del agente.
"""

import json
import os
import subprocess
import sys
import time


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1]) as f:
        plan = json.load(f)
    out_dir = argv[2]
    os.makedirs(out_dir, exist_ok=True)

    proc = subprocess.Popen(
        ["rea", "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    next_id = 0

    def send(message: dict) -> None:
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def request(method: str, params: dict) -> dict:
        nonlocal next_id
        next_id += 1
        send({"jsonrpc": "2.0", "id": next_id, "method": method, "params": params})
        while True:
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("rea mcp terminó inesperadamente")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") == next_id:
                return message

    request("initialize", {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "rea-session", "version": "1"},
    })
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    failures = 0
    try:
        for index, step in enumerate(plan, 1):
            label = step.get("name") or step["tool"]
            started = time.time()
            response = request("tools/call", {"name": step["tool"], "arguments": step.get("args", {})})
            elapsed = time.time() - started
            result = response.get("result") or {"isError": True, "error": response.get("error")}
            payload = result.get("structuredContent")
            if payload is None:
                text = "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    payload = {"text": text, "error": result.get("error")}
            path = os.path.join(out_dir, f"{index:02d}-{label}.json")
            with open(path, "w") as f:
                json.dump(payload, f)
            is_error = bool(result.get("isError"))
            failures += is_error
            evidence = payload.get("evidence_id") if isinstance(payload, dict) else None
            print(f"{index:02d} {label:24s} {elapsed:6.1f}s error={is_error} "
                  f"evidence={evidence} bytes={os.path.getsize(path)} -> {path}")
    finally:
        proc.kill()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
