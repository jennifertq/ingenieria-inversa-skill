# Flujo de trabajo en CaludeCode (nube): CLI, sesiones MCP y errores conocidos

Todo lo de esta guía se ejecutó y comprobó en una sesión de Claude Code en la
nube con `rea-agents@6.7.0`, Ghidra 12.1.4, pwntools 4.15.0, Node 22.22
(sistema) y Node 24.22 (solo SQLite). Si cambias alguna versión, vuelve a
validar estas rutas.

## Índice

1. Preparación y comprobación del entorno
2. Elegir entre MCP, `rea-session.py` y CLI
3. Gestión de salidas (archivos, vistas, filtros)
4. Comandos validados, uno por uno
5. Sesiones MCP por lotes (`rea-session.py`)
6. Errores conocidos y su solución
7. Tiempos medidos
8. Lo que no está disponible y cómo pedirlo

## 1. Preparación y comprobación del entorno

El hook `.claude/hooks/session-start.sh` llama a `scripts/setup-rea-tools.sh`
al iniciar la sesión y deja estas variables en el entorno:

| Variable | Valor | Para qué |
|---|---|---|
| `GHIDRA_INSTALL_DIR` | `/opt/rea-tools/ghidra_12.1.4_PUBLIC` | Proveedor `ghidra` (descompilación nativa) |
| `REA_PWNTOOLS_PYTHON` | `/usr/bin/python3` | `inspect-binary-layout` |
| `REA_NODE24` | `/opt/rea-tools/node24/node_modules/.bin/node` | `inspect-sqlite-database` |
| `REA_BIN` | ruta real de `rea.mjs` | Lanzar REA con otro Node |

Comprobación rápida (no modifica nada):

```bash
rea --version                       # 6.7.0
echo "$GHIDRA_INSTALL_DIR"          # no vacío
rea doctor --client claude_code --json > /tmp/rea/doctor.json; echo $?
```

`doctor` devuelve código 1 aunque todo funcione si el registro MCP global no
existe o falta algún motor opcional (Hopper, IDA, JADX…). Lee `scope_checks` e
`informational_checks`; no lo interpretes como fallo general.

Si las herramientas faltan (por ejemplo, el hook falló):

```bash
source scripts/setup-rea-tools.sh
# rea 6.7.0 | ghidra ok | pwntools 4.15.0 | node24 v24.22.0
```

Es idempotente: si ya está todo, termina en ~6 s.

## 2. Elegir entre MCP, `rea-session.py` y CLI

| Situación | Usa | Motivo |
|---|---|---|
| Herramientas `rea` visibles en la sesión | MCP directo | Sesión persistente, `detail: "summary"`, IDs retenidos |
| 2+ consultas nativas al mismo binario | `scripts/rea-session.py` | 1.ª consulta ~15 s, siguientes ~0,1 s |
| Una consulta suelta o un análisis JS | CLI `rea …` | Simple; redirige siempre a archivo |
| Leer un Evidence grande ya guardado | `scripts/rea-view.py` | Resumen/páginas sin cargar el archivo |

El proyecto declara el servidor en `.mcp.json` (`npx -y rea-agents@6.7.0 mcp`).
Claude Code pide aprobarlo la primera vez; mientras no esté aprobado, usa
`rea-session.py`.

## 3. Gestión de salidas

Crea una carpeta por investigación y no la pongas dentro del repo:

```bash
mkdir -p /tmp/rea
```

Reglas:

- **Siempre** `--format json > /tmp/rea/<nombre>.json`. Sin redirección, la
  salida va al contexto. Ejemplo real: Express (206 archivos JS) → 130 MB.
- `--json` funciona por compatibilidad, pero la opción documentada es
  `--format json`.
- El CLI **no** tiene `--detail summary`: es solo del esquema MCP.
- `--filter-output a,b.c` reduce la salida a esas claves. Útil:
  `evidence_id,limitations,normalized_result.<campo>`.
- `--token-count` **vuelve a ejecutar** el análisis completo solo para contar;
  en análisis caros, mide el tamaño del archivo (`wc -c`) en su lugar.
- `--token-limit N` / `--token-offset N` paginan por tokens la salida
  formateada, pero cortan JSON por la mitad: úsalos solo para leer, no para
  parsear.

Leer un Evidence grande con `scripts/rea-view.py` (envuelve el archivo como
fuente `inline` de `rea inspect-analysis-view`):

```bash
python3 -I scripts/rea-view.py /tmp/rea/app.json summary
python3 -I scripts/rea-view.py /tmp/rea/app.json page modules 0 16
python3 -I scripts/rea-view.py /tmp/rea/app.json item modules jag_node_<id>
```

Medido: 130 MB → resumen de 10 KB en ~28 s. La página lista `node_id`, `kind`
y `path`; usa el `node_id` exacto para `item` (una ruta puede tener varios
roles). `coverage.next_offset` indica la siguiente página; `exhausted: true`
significa que no hay más.

Formato de entrada de `inspect-analysis-view` (por si lo llamas a mano):

```json
{"source": {"kind": "inline", "evidence": { ...Evidence completo... }},
 "view": {"kind": "summary"}}
```

`source.kind` acepta `inline` (CLI) o `retained-evidence` con `evidence_id`
(solo dentro de la misma sesión MCP). `view` es un objeto, nunca un texto.

## 4. Comandos validados

Todos los Evidence comparten la misma forma: `evidence_id`, `subject` (ruta y
SHA-256), `provider`, `operation`, `parameters`, `raw_result`,
`normalized_result`, `confidence`, `limitations`, `relationship_coverage`,
`locations`, `evidence_links`. Cita siempre `evidence_id` y revisa `limitations`.

### 4.1 App JavaScript / Electron / ASAR

```bash
rea analyze-javascript-application /ruta/app --format json > /tmp/rea/app.json
python3 -I scripts/rea-view.py /tmp/rea/app.json summary
```

- Acepta carpeta o `.asar` (`--artifact-format auto|asar|directory`).
- Limita el alcance con `--source-path <ruta relativa>` (repetible) cuando la
  pregunta es sobre archivos concretos.
- Límites útiles: `--max-heap-mb` (1024), `--analysis-timeout-ms` (300000),
  `--max-semantic-nodes` (100000).
- Integridad declarada que no coincide: falla por defecto; `--integrity-policy
  record-and-continue` la registra y sigue.
- El resumen trae `statistics` (archivos relevantes, JS analizados, nodos AST),
  `coverage` y `unknowns`. Las `limitations` recuerdan que el JS se parsea
  como texto inerte y que nada se ejecutó.

### 4.2 Binario nativo con Ghidra (CLI, una consulta)

```bash
rea analyze   /ruta/bin --provider ghidra --format json > /tmp/rea/overview.json
rea function  /ruta/bin check_license --provider ghidra --format json > /tmp/rea/f.json
rea decompile /ruta/bin main --provider ghidra --format json > /tmp/rea/main.json
rea search    /ruta/bin "Licencia" --provider ghidra --format json > /tmp/rea/s.json
rea search    /ruta/bin check --kind procedures --provider ghidra --format json > /tmp/rea/p.json
rea xrefs     /ruta/bin check_license --provider ghidra --format json > /tmp/rea/x.json
```

- `analyze` → `binary_overview`: `segments`, `procedure_count`, `string_count`.
- `function` → `analyze_function`: `procedure`, `pseudocode`, `assembly`,
  `callers`, `callees`, `incoming_references`, `outgoing_references`,
  `unresolved_calls`, `referenced_strings`, `basic_blocks`, `native_api`,
  `native_value_flow`. Pseudocódigo en `raw_result.value.pseudocode`.
- `decompile` → `procedure_pseudo_code` (solo el pseudocódigo).
- `search` → lista `{address, value}`; `--mode regex`, `--case-sensitive`.
- `xrefs` → direcciones que referencian el símbolo.
- Cada llamada cuesta ~16 s (importación + autoanálisis de Ghidra). Para más de
  una, usa `rea-session.py` (sección 5).
- Binarios sin cabecera: `--target-format raw-binary --architecture <cpu>
  --entry-point 0x…`.

### 4.3 Estructura ELF (pwntools)

```bash
rea inspect-binary-layout /ruta/bin --format json > /tmp/rea/layout.json
```

Devuelve `image_type`, `entry_point`, `sections`, `segments`, `symbols`,
`relocations`, `linkage` y `mitigations` (PIE, NX, pila ejecutable, canario,
RELRO). Las mitigaciones son `evidence_kind: "inferred"`: indicadores estáticos,
no prueba de comportamiento.

### 4.4 Go y Rust

```bash
rea inspect-go-binary   /ruta/bin --format json > /tmp/rea/go.json
rea inspect-rust-binary /ruta/bin --format json > /tmp/rea/rust.json
```

- Go: `build_info` con `go_version`, módulos y ajustes de compilación
  (`GOOS`, `GOARCH`, `CGO_ENABLED`…). Sin metadatos no prueba que no sea Go.
- Rust: lee la sección `.dep-v0` de cargo-auditable. Un binario compilado sin
  cargo-auditable devuelve metadatos nulos: no significa "sin dependencias".

### 4.5 Paquetes y archivos

```bash
rea inspect-artifact /ruta/paquete.zip --format json > /tmp/rea/pkg.json
```

Devuelve `observations`, `hypotheses`, `contradictions`, `next_probes`. El
inventario ZIP lista solo el directorio central; bytes fuera de entradas (p. ej.
firma APK) no se interpretan aquí.

### 4.6 SQLite (requiere Node 24)

```bash
"$REA_NODE24" "$REA_BIN" inspect-sqlite-database /ruta/app.db --format json > /tmp/rea/db.json
"$REA_NODE24" "$REA_BIN" inspect-sqlite-database /ruta/app.db --table users \
  --column id --column email --row-limit 20 --format json > /tmp/rea/users.json
```

- Sin `--table` solo devuelve el inventario del esquema (`rows: null`).
- `--schema-scope database` da el esquema completo.
- Las filas indican `truncated` y `order: "unspecified"`.
- Usa una copia quieta de la base; con WAL, copia `.db` y `-wal` a la vez.

### 4.7 Binarios sin símbolos (stripped)

Validado con `/usr/bin/whoami` (GNU coreutils, ELF x86-64 stripped). Las
funciones propias aparecen como `FUN_<dirección>`; las pistas están en los
imports y en las cadenas.

**1. Imports primero.** `rea inspect-binary-layout <bin>` lista los símbolos
dinámicos. El nombre está en `symbols[].name.display` (es un objeto, no un
texto):

```bash
python3 -c "import json;n=json.load(open('/tmp/rea/layout.json'))['normalized_result'];print(sorted({s['name']['display'] for s in n['symbols'] if s['name']['display']}))"
```

**2. Un import es ambiguo por nombre.** `procedure_callers` con `"geteuid"`
falla con:

```
Ghidra procedure name is ambiguous: geteuid; select an exact entry address
from [EXTERNAL:0x14, 0x102400, 0x1090b8]
```

Las tres entradas son la función externa, el stub de llamada (PLT) y la
entrada de la tabla de imports (GOT). Usa la **dirección del stub**, que es la
que aparece en el código (aquí `0x102400`):
`{"tool": "procedure_callers", "args": {"procedure": "0x102400"}}`.
El mensaje de error ya trae la lista; no hace falta otra consulta.

**3. Quién usa una cadena.** `find_xrefs_to_name` busca **nombres**, no el
texto de la cadena: con `"cannot find name for user ID %lu"` devuelve
`name_not_found`. Dos formas que sí funcionan:

- CLI: `rea xrefs <bin> 0x1065a8 --provider ghidra --format json` → `["0x1027b6"]`.
- MCP: `search_strings` da la dirección → `inspect_address_context` con esa
  dirección da la etiqueta de Ghidra (`result.name.value`, p. ej.
  `s_cannot_find_name_for_user_ID_%lu_001065a8`) → `find_xrefs_to_name` con
  esa etiqueta → `xrefs: ["0x1027b6"]`.

Después, `resolve_containing_procedure` con la dirección de la referencia da la
función que la contiene (`0x102590`).

**4. Funciones grandes.** `analyze_function` sobre un `main` devolvió
**519 KB** (incluye ensamblador, bloques, referencias y flujo de valores).
Guárdalo en archivo y extrae solo lo necesario:

```bash
python3 -c "
import json;d=json.load(open('/tmp/rea/s/02-fn.json'));n=d['normalized_result']
print(d['evidence_id']); print([c['name'] for c in n['callees']])
print([s['value'] for s in n['referenced_strings']]); print(d['raw_result']['value']['pseudocode'])"
```

Si solo necesitas el código, `procedure_pseudo_code` (o `rea decompile`) es
mucho más pequeño.

## 5. Sesiones MCP por lotes (`rea-session.py`)

```bash
cat > /tmp/rea/plan.json <<'EOF'
[
  {"tool": "open_binary", "args": {"path": "/ruta/abs/bin", "provider_id": "ghidra"}},
  {"tool": "binary_overview", "args": {}},
  {"tool": "list_procedures", "args": {}},
  {"tool": "search_strings", "args": {"pattern": "Licencia"}},
  {"tool": "analyze_function", "args": {"procedure": "check_license"}, "name": "check_license"},
  {"tool": "procedure_callers", "args": {"procedure": "check_license"}},
  {"tool": "close_binary", "args": {}}
]
EOF
python3 -I scripts/rea-session.py /tmp/rea/plan.json /tmp/rea/session
```

Salida real (resumida):

```
02 binary_overview  14.8s error=False evidence=ev_7647…
03 list_procedures   0.0s error=False evidence=ev_6023…
04 search_strings    0.0s error=False evidence=ev_4482…
05 check_license     0.2s error=False evidence=ev_6dc2…
07 procedure_callers 0.0s error=False evidence=ev_076f…
```

- Cada resultado queda en `/tmp/rea/session/NN-<nombre>.json`. Extrae solo los
  campos que necesitas con un `python3 -c` corto; no lo leas entero.
- El primer paso que necesita análisis paga ~15 s; el resto, décimas.
- Termina siempre con `close_binary`.
- Consulta los nombres y argumentos exactos con `tools/list` (207 herramientas
  en 6.7.0); `binary_session` con `{}` muestra disponibilidad y motivos.
- Código de salida 1 si algún paso devolvió error.

## 6. Errores conocidos y su solución

| Mensaje | Causa | Solución |
|---|---|---|
| `SQLite inspection requires the native DatabaseSync.limits API…` | Node 22 | Usa `"$REA_NODE24" "$REA_BIN" inspect-sqlite-database …` |
| `Set REA_PWNTOOLS_PYTHON to an absolute caller-supplied Python…` | Variable no definida | `export REA_PWNTOOLS_PYTHON=$(command -v python3)` o `source scripts/setup-rea-tools.sh` |
| `GHIDRA_INSTALL_DIR is not set` | Hook no ejecutado | `source scripts/setup-rea-tools.sh` |
| `Unknown flag: --detail` | Opción solo de MCP | Redirige a archivo y usa `rea-view.py` |
| `source.kind … expected ["retained-evidence","inline"]` | Entrada mal formada en `inspect-analysis-view` | Usa `rea-view.py` o la forma de la sección 3 |
| `registration:claude_code … config_drift` en `doctor` | No hay registro MCP global | Normal aquí; usa `.mcp.json` o `rea-session.py`; no ejecutes `setup` |
| `Ghidra procedure name is ambiguous: <nombre>; select an exact entry address from [...]` | Import con varias entradas (externa, PLT, GOT) | Pasa la dirección del stub PLT que da el propio mensaje |
| `find_xrefs_to_name` → `name_not_found` con el texto de una cadena | Busca nombres, no contenido | `rea xrefs <bin> <dirección>` o etiqueta de `inspect_address_context` |
| `No procedure exists at the requested address` | Pasaste una dirección de datos a una herramienta de funciones | Usa `resolve_containing_procedure` sobre la dirección de la referencia |
| Salida enorme / contexto lleno | Falta redirección | `--format json > archivo` siempre |

## 7. Tiempos medidos

| Operación | Tiempo |
|---|---|
| `setup-rea-tools.sh` en frío (descarga Ghidra 570 MB) | ~27 s |
| `setup-rea-tools.sh` ya instalado | ~6 s |
| `analyze-javascript-application`, app mínima | ~2 s |
| `analyze-javascript-application`, Express (206 JS) | ~67 s, 130 MB |
| `rea-view.py summary` sobre 130 MB | ~28 s |
| CLI Ghidra (`analyze`, `function`, `decompile`, `xrefs`) | ~15–20 s cada uno |
| CLI `search` de cadenas con Ghidra | ~36 s |
| MCP: primera consulta Ghidra / siguientes | ~15 s / ~0,1 s |
| `inspect-go-binary`, `inspect-rust-binary`, `inspect-binary-layout`, SQLite | 1–3 s |

## 8. No disponible y cómo pedirlo

| Herramienta | Para | Estado |
|---|---|---|
| Hopper | Nativo en macOS | Imposible en Linux |
| IDA | Nativo (alternativa a Ghidra) | Requiere licencia del usuario |
| JADX (`REA_JADX_MCP_JAR`) | Código de APK | Pedir permiso; REA no lo descarga |
| Binwalk / Unblob | Firmware | Pedir permiso |
| TShark / capinfos | PCAP | Pedir permiso (`REA_TSHARK_COMMAND`) |
| WABT 1.0.42 | WASM | Pedir permiso (`REA_WABT_BIN_DIRECTORY`) |
| sigrok-cli 0.7.2 | Señales | Pedir permiso (`REA_SIGROK_COMMAND`) |
| Navegador / Electron del usuario | Observación en ejecución | Requiere el equipo del usuario |

Pregunta siempre antes de instalar: di qué necesitas, para qué pregunta, cuánto
pesa aproximadamente y que se perderá al cerrar el contenedor salvo que se
añada a `scripts/setup-rea-tools.sh`.
