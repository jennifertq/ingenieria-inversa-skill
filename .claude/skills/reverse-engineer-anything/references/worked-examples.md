# Ejemplos de principio a fin (resultados reales)

Ejecutados en CaludeCode con rea 6.7.0 y Ghidra 12.1.4. Los `evidence_id` son
los obtenidos en la validación; en tu sesión serán otros si cambia el objetivo.

## Ejemplo 1 — ¿Cómo valida la licencia este ejecutable?

**Petición:** "Tengo `lic`, un ejecutable Linux. ¿Qué clave acepta?"

**Plan de preguntas**

1. ¿Qué mensajes muestra al validar? → cadenas.
2. ¿Qué función decide? → referencias a esas cadenas / función candidata.
3. ¿Cuál es la regla exacta? → pseudocódigo.
4. ¿Quién la llama y con qué entrada? → llamadores.

**Ejecución (una sola sesión MCP, ~16 s en total)**

```bash
mkdir -p /tmp/rea
cat > /tmp/rea/plan.json <<'EOF'
[
  {"tool": "open_binary", "args": {"path": "/abs/lic", "provider_id": "ghidra"}},
  {"tool": "search_strings", "args": {"pattern": "Licencia"}},
  {"tool": "list_procedures", "args": {}},
  {"tool": "analyze_function", "args": {"procedure": "check_license"}, "name": "check_license"},
  {"tool": "analyze_function", "args": {"procedure": "main"}, "name": "main"},
  {"tool": "close_binary", "args": {}}
]
EOF
python3 -I scripts/rea-session.py /tmp/rea/plan.json /tmp/rea/lic
python3 -c "import json;d=json.load(open('/tmp/rea/lic/04-check_license.json'));print(d['raw_result']['value']['pseudocode'])"
```

**Resultados**

- Cadenas: `0x102004 "Licencia valida"`, `0x102014 "Licencia invalida"`.
- Procedimiento: `check_license` en `0x101149`; `main` llama a `check_license`
  y a `puts`.
- Pseudocódigo de Ghidra (`ev_6dc29a88…`):

```c
bool check_license(char *param_1) {
  ...
  do {
    iVar2 = iVar2 + (int)cVar1 * (int)lVar3;   // suma carácter × posición (1-based)
    cVar1 = param_1[lVar3];
    lVar3 = lVar3 + 1;
  } while (cVar1 != '\0');
  return iVar2 % 0x61 == 0x2a;                  // % 97 == 42
}
```

**Respuesta al usuario (formato recomendado)**

> **Observado** (`ev_6dc29a88…`, pseudocódigo de Ghidra): `check_license`
> recorre la clave sumando `carácter × posición` (empezando en 1) y la acepta
> si la suma módulo 97 es 42. `main` imprime "Licencia valida" o "Licencia
> invalida" según el resultado.
> **Inferido:** cualquier clave cuya suma ponderada cumpla `s % 97 == 42` es
> válida; no hay más comprobaciones en esta función.
> **Desconocido / límites:** análisis estático; no se ejecutó el programa. Los
> nombres de variables son de Ghidra, no originales.

Equivalente con CLI (más lento, ~16 s por línea):

```bash
rea search   /abs/lic Licencia --provider ghidra --format json > /tmp/rea/s.json
rea function /abs/lic check_license --provider ghidra --format json \
  --filter-output evidence_id,raw_result.value.pseudocode
```

## Ejemplo 2 — Panorama de una app JavaScript grande sin llenar el contexto

**Petición:** "¿Qué módulos tiene esta app Node/Electron y qué hace?"

```bash
rea analyze-javascript-application /abs/app --format json > /tmp/rea/app.json   # Express: 67 s, 130 MB
wc -c /tmp/rea/app.json
python3 -I scripts/rea-view.py /tmp/rea/app.json summary > /tmp/rea/app-summary.json   # ~10 KB
python3 -I scripts/rea-view.py /tmp/rea/app.json page modules 0 16
python3 -I scripts/rea-view.py /tmp/rea/app.json item modules jag_node_<id>
```

**Resultados (Express 4.21.2)**

- Resumen: 360 archivos relevantes, 260 JS analizados, 0 omitidos;
  `coverage.status: complete-within-view`.
- Página de módulos: entradas `{node_id, kind: "javascript-module", path}`,
  p. ej. `node_modules/debug/node.js`, `node_modules/parseurl/index.js`.
- `limitations`: relaciones CommonJS/ESM recuperadas de sintaxis inerte;
  cobertura del grafo incompleta; nada se ejecutó.

**Siguiente paso típico:** elegir el módulo que responde a la pregunta (por
ejemplo, el que define una ruta HTTP) y pedir su `item`; para seguir una
funcionalidad, ver `trace_application_feature` en `javascript-applications.md`.

## Ejemplo 3 — ¿Con qué se compiló este binario y qué protecciones tiene?

```bash
rea inspect-go-binary     /abs/bin --format json --filter-output normalized_result.build_info.go_version
rea inspect-binary-layout /abs/bin --format json --filter-output normalized_result.mitigations,normalized_result.image_type
```

**Resultados reales**

- Go: `go_version: "go1.24.7"`, `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=1`,
  `-buildmode=exe`.
- ELF en C: `image_type: ET_DYN`, `position_independent: true`,
  `nx_indicator: true`, `stack_canary_indicator: false`, `relro: "Full"`,
  todo con `evidence_kind: "inferred"`.

**Cómo decirlo:** "Los metadatos embebidos indican Go 1.24.7 para linux/amd64
(observado en el archivo; no autentica el compilador). El ELF es PIE, con NX y
RELRO completo y sin indicador de canario de pila (indicadores estáticos)."

## Ejemplo 4 — ¿Qué datos guarda esta base SQLite?

```bash
"$REA_NODE24" "$REA_BIN" inspect-sqlite-database /abs/app.db --format json \
  --filter-output normalized_result.schema
"$REA_NODE24" "$REA_BIN" inspect-sqlite-database /abs/app.db --table users \
  --row-limit 20 --format json --filter-output normalized_result.rows
```

**Resultados reales:** tabla `users` (2 columnas); filas
`[{integer 1}, {text "a@b.c"}]`, `returned_rows: 1`, `truncated: false`,
`order: "unspecified"`.

**Cuidado:** si hay datos personales, muestra solo lo necesario para responder.

## Ejemplo 5 — ¿Qué hay dentro de este paquete?

```bash
rea inspect-artifact /abs/paquete.zip --format json > /tmp/rea/pkg.json
python3 -c "import json;d=json.load(open('/tmp/rea/pkg.json'))['normalized_result'];print([o['kind'] for o in d['observations']]);print(d['next_probes'])"
```

Resultado real con un ZIP de 2 archivos: una sola observación `root-manifest`
(identidad y SHA-256 del contenedor) y `next_probes: []`. Para ver los miembros
uno a uno, usa en una sesión MCP `open_binary` con la ruta del paquete y las
herramientas de inventario que anuncie `binary_session`; para analizar un
miembro concreto, extráelo (`rea extract-artifact` a un directorio nuevo y
vacío) y aplica la ruta de su tipo.

## Ejemplo 6 — Binario real sin símbolos: ¿cómo obtiene `whoami` el usuario?

**Objetivo:** `/usr/bin/whoami` (GNU coreutils, ELF x86-64 PIE, stripped,
SHA-256 `5b1df9f84f9037e9…`).

**Plan de preguntas**

1. ¿Qué funciones de usuario importa? → estructura ELF.
2. ¿Qué función interna las llama? → llamadores del stub PLT.
3. ¿Cuál es la lógica exacta y qué pasa si falla? → pseudocódigo + cadenas.

**Paso 1 — imports** (`ev_88293295…`): 55 símbolos; los relevantes son
`geteuid`, `getpwuid`, `puts`, `error` y `__errno_location`. Mitigaciones:
PIE, NX, canario de pila y RELRO completo (indicadores inferidos).

```bash
rea inspect-binary-layout /usr/bin/whoami --format json > /tmp/rea/whoami-layout.json
```

**Paso 2 — llamadores.** El primer intento con el nombre falló por ambigüedad
(`[EXTERNAL:0x14, 0x102400, 0x1090b8]`); con la dirección del stub sí:

```json
[
  {"tool": "open_binary", "args": {"path": "/usr/bin/whoami", "provider_id": "ghidra"}},
  {"tool": "procedure_callers", "args": {"procedure": "0x102400"}, "name": "callers-geteuid"},
  {"tool": "procedure_callers", "args": {"procedure": "0x102370"}, "name": "callers-getpwuid"},
  {"tool": "analyze_function", "args": {"procedure": "0x102590"}, "name": "fn-102590"},
  {"tool": "close_binary", "args": {}}
]
```

Resultado: `geteuid` (`ev_713c1fa2…`) y `getpwuid` (`ev_6fb18c5a…`) tienen un
único llamador, `0x102590`. La cadena de error `0x1065a8` se referencia desde
`0x1027b6` (`rea xrefs`), que está dentro de esa misma función.

**Paso 3 — pseudocódigo** (`ev_c58b4743…`, 519 KB; se extrajo solo el
pseudocódigo):

```c
if (_optind == param_1) {               // sin argumentos extra
  piVar5 = __errno_location();
  *piVar5 = 0;
  __uid = geteuid();
  if (((__uid != 0xffffffff) || (*piVar5 == 0)) &&
      (ppVar6 = getpwuid(__uid), ppVar6 != (passwd *)0x0)) {
    puts(ppVar6->pw_name);
    return 0;
  }
  uVar7 = dcgettext(0, "cannot find name for user ID %lu", 5);
  error(1, *piVar5, uVar7, __uid);
}
...
error(0, 0, "extra operand %s", ...);
```

**Respuesta al usuario**

> `whoami` obtiene el UID efectivo con `geteuid()`, lo traduce a nombre con
> `getpwuid()` e imprime `pw_name` con `puts()` (**observado**, `ev_c58b4743`).
> Limpia `errno` antes para distinguir un UID `-1` legítimo de un error. Si no
> hay entrada en la base de usuarios, termina con "cannot find name for user
> ID %lu" y código 1; con argumentos sobrantes, "extra operand %s".
> **Inferido:** `FUN_00102590` es el `main` (configura locale/gettext de
> coreutils, procesa opciones y llama a ambas funciones).
> **Límites:** análisis estático, sin ejecución; nombres de variables de Ghidra.

**Lecciones:** imports primero; dirección del stub en vez del nombre; `rea
xrefs` con la dirección de la cadena; nunca leer `analyze_function` entero.
Total: 10 consultas Ghidra en ~55 s con `rea-session.py` (≈160 s por CLI).
