# ingenieria-inversa-skill

Skill de [Claude Code](https://claude.com/claude-code) para hacer **ingeniería
inversa en español** con [REA](https://github.com/morluto/rea) (Reverse
Engineer Anything): explicar cómo funciona un binario o una app sin su código
fuente, descompilar funciones, inventariar paquetes y documentar cada
conclusión con evidencia.

Está basada en la skill `reverse-engineer-anything` de REA (v42, licencia MIT),
reestructurada, traducida y **validada de principio a fin** en sesiones de
Claude Code en la nube.

## Qué puede analizar

| Objetivo | Herramienta | Estado |
|---|---|---|
| Apps JavaScript / Electron / `.asar` | `analyze_javascript_application` | ✅ validado |
| Ejecutables y bibliotecas nativas (Ghidra) | `analyze_function`, `procedure_pseudo_code`, `search_strings`, `xrefs` | ✅ validado (también sin símbolos) |
| Estructura ELF, símbolos, mitigaciones | `inspect_binary_layout` | ✅ validado |
| Metadatos de Go y Rust | `inspect_go_binary`, `inspect_rust_binary` | ✅ validado |
| Paquetes ZIP | `inspect_artifact` | ✅ validado |
| Bases SQLite | `inspect_sqlite_database` | ✅ validado (Node 24) |
| APK, firmware, PCAP, WASM, .NET… | ver la guía de rutas | requiere motores adicionales |

## Instalación

### Opción A: usar este repo como proyecto (recomendada en la nube)

Abre una sesión de Claude Code con este repositorio. El hook
`SessionStart` ejecuta `scripts/setup-rea-tools.sh`, que instala
`rea-agents@6.7.0`, Ghidra 12.1.4, pwntools 4.15.0 y Node 24 (≈30 s la
primera vez) y exporta sus variables. Claude Code te pedirá aprobar el
servidor MCP `rea` declarado en `.mcp.json`.

### Opción B: copiar la skill a otro proyecto

```bash
mkdir -p .claude/skills
cp -r .claude/skills/reverse-engineer-anything /ruta/a/tu-proyecto/.claude/skills/
cp scripts/setup-rea-tools.sh scripts/rea-session.py scripts/rea-view.py /ruta/a/tu-proyecto/scripts/
# opcional: el hook y el servidor MCP
cp -r .claude/hooks /ruta/a/tu-proyecto/.claude/ && cp .mcp.json /ruta/a/tu-proyecto/
```

Si copias el hook, añade también el bloque `hooks` de `.claude/settings.json`.

### Requisitos

Linux x86-64, Node.js 22.19+ (o 24.11+), Java 21 para Ghidra, Python 3 con
pip, y acceso a `registry.npmjs.org`, `pypi.org` y descargas de GitHub.

## Uso

Pídelo en lenguaje natural, por ejemplo:

- "Analiza `/usr/bin/whoami`: ¿cómo obtiene el nombre del usuario?"
- "Descompila la función que valida la licencia en `./app`."
- "¿Qué módulos tiene esta app Electron y qué hace cada uno?"
- "¿Con qué versión de Go se compiló este binario y qué protecciones tiene?"

La skill responde separando **observado**, **inferido** y **desconocido**, y
cita los `evidence_id` de REA.

## Estructura

```
.claude/
  skills/reverse-engineer-anything/
    SKILL.md                      # instrucciones principales (español)
    LICENSE                       # MIT de REA
    references/
      cloud-cli-workflow.md       # comandos, salidas, errores y tiempos validados
      worked-examples.md          # 6 ejemplos reales de principio a fin
      reporting.md                # cómo redactar conclusiones
      target-routing.md           # ruta para cada tipo de objetivo
      native-and-artifacts.md     # binarios nativos, .NET, paquetes
      javascript-applications.md  # JS/Electron/ASAR
      android-applications.md     # APK
      runtime-observation.md      # navegador/Electron en ejecución
      evidence-workflows.md       # paginación y verificación de Evidence
      connection-and-recovery.md  # diagnóstico y reparación
  hooks/session-start.sh          # instala las herramientas al iniciar sesión
  settings.json                   # registra el hook
.mcp.json                         # servidor MCP rea (npx rea-agents@6.7.0)
scripts/
  setup-rea-tools.sh              # instalación idempotente de REA y motores
  rea-session.py                  # varias consultas MCP en una sesión (~150× más rápido)
  rea-view.py                     # leer por partes Evidence grandes sin llenar el contexto
docs/historial-de-validacion.md   # cómo se investigó, adaptó y validó
```

## Lo que aporta frente a la skill original

- Todo en español, con el entorno de trabajo primero y `SKILL.md` de 165 líneas.
- Receta para no llenar el contexto: una app de 206 archivos JS genera 130 MB
  de Evidence; `rea-view.py` lo reduce a un resumen de 10 KB.
- `rea-session.py`: en el CLI cada consulta a Ghidra tarda ~16 s; en una sesión
  MCP solo la primera, las siguientes ~0,1 s.
- Recetas para binarios sin símbolos (imports ambiguos, referencias a cadenas).
- Versiones fijadas (`rea-agents@6.7.0`, Ghidra 12.1.4) y validadas juntas.
- Errores reales documentados con su solución.

## Licencia

MIT. Incluye trabajo derivado de REA © 2026 morluto (ver `LICENSE`).
