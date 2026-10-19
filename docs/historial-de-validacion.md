# Historial de investigación y validación

> Registro de cómo se investigó REA, se adaptó la skill y se validó, versión a versión.
> Las rutas que menciona (`clonar-repositorios/`, `.claude/…`) corresponden al repositorio de
> trabajo donde se hizo; en este repo la skill está en `.claude/skills/reverse-engineer-anything/`.

## REA — Reverse Engineer Anything

- **Origen:** https://github.com/morluto/rea (commit `974487f`, clonado 2026-10-19)
- **Licencia:** MIT (copia en `LICENSE`)
- **Lenguaje:** TypeScript · npm `rea-agents`

## Qué es
Servidor MCP + skills para que un agente haga ingeniería inversa de binarios nativos,
apps JavaScript/Electron, ensamblados .NET, Android, firmware y sitios web, usando
Hopper, Ghidra o IDA. El análisis corre en local y cada conclusión trae evidencia.

## Contenido relevante
- `.agents/skills/reverse-engineer-anything/` — skill para usuarios (SKILL.md + 6 referencias).
- `.agents/skills/rea-*` — skills internas para desarrollar REA (no aplican aquí).
- `src/`, `native/`, `bridge/` — el servidor MCP (se instala con npm, no se copia).

## ¿Nos sirve?
Sí, como skill de Claude Code. Solo da instrucciones; las herramientas requieren
registrar el MCP aparte: `npx rea-agents setup` (elegir Claude Code).

## Adaptación / adopción
- Copiada a `.claude/skills/reverse-engineer-anything/` (estructura compatible con Claude Code).
- Se añadió LICENSE MIT junto a la skill para cumplir la atribución.
- No se copió el código del servidor: se instala desde npm oficial.

## Análisis y correcciones de la skill (versión `42-caludecode.1`)
| Hallazgo | Corrección |
|---|---|
| Ejemplos de diagnóstico/instalación usan `--client codex` | Cambiados a `--client claude_code` (SKILL.md y connection-and-recovery.md) |
| `npx rea-agents@latest` (cambia sin aviso; riesgo de cadena de suministro) | Fijado a `rea-agents@6.7.0` |
| Párrafo repetido ("setup never installs… Node.js, npm, Homebrew…") | Eliminado el duplicado |
| Solo se activaba con peticiones en inglés | Disparadores en español en `description` |
| No contemplaba el entorno en la nube (sin MCP registrado, sin Hopper/Ghidra/IDA) | Nueva sección *CaludeCode environment* |

**Verificado:** enlaces relativos a `references/` correctos; `npx rea-agents@6.7.0
analyze-javascript-application <dir> --json` funciona en la sesión en la nube
(Node 22.22, cumple `^22.19.0`) y devuelve Evidence con `evidence_id`.

**Limitaciones que siguen:** el análisis nativo/firmware/.NET requiere motores
(Ghidra, Hopper, IDA, Binwalk…) que no están en el contenedor; la observación
en tiempo de ejecución necesita navegador/Electron del usuario.

## Validación completa (versión `42-caludecode.2`, 2026-10-19)
Instalado en el contenedor: rea-agents 6.7.0, Ghidra 12.1.4, pwntools 4.15.0
(+pyelftools 0.33, Unicorn 2.1.2) y Node 24.22 (solo para SQLite). Todo con
`scripts/setup-rea-tools.sh`.

| Ruta | Objetivo de prueba | Resultado |
|---|---|---|
| `analyze-javascript-application` | app Electron mínima / Express (206 archivos) | ✅ (Express: 67 s, **130 MB**) |
| `inspect-analysis-view` (inline) | Evidence de Express | ✅ 130 MB → 10 KB de resumen; paginación de módulos |
| `analyze` / `function` / `decompile` (Ghidra) | ELF en C con `check_license` | ✅ pseudocódigo correcto (`% 0x61 == 0x2a`), 15–20 s |
| `inspect-binary-layout` | mismo ELF | ✅ tras definir `REA_PWNTOOLS_PYTHON` |
| `inspect-go-binary` | binario Go | ✅ |
| `inspect-rust-binary` | binario Rust sin cargo-auditable | ✅ (metadatos nulos, como documenta) |
| `inspect-artifact` | ZIP | ✅ |
| `inspect-sqlite-database` | base SQLite | ❌ con Node 22 → ✅ con Node 24 |
| Servidor MCP `rea mcp` | stdio | ✅ 207 herramientas; las 103 citadas por la skill existen |
| `rea setup --dry-run` | Claude Code | ⚠️ instalaría la skill original en `~/.claude/skills` |

**Mejoras aplicadas tras validar:**
1. Sección de entorno reescrita con pasos reales (instalación, rutas validadas, no disponibles).
2. Receta para salidas grandes en modo CLI (redirigir a archivo + `scripts/rea-view.py`);
   la skill original solo explicaba `detail: "summary"`, que no existe en el CLI.
3. Corregido `--json` → `--format json` (el flag documentado por `rea --help`).
4. Aviso de no ejecutar `rea setup` aquí (sobrescribiría esta skill adaptada).
5. Node 24 para SQLite y `REA_PWNTOOLS_PYTHON` documentados.

**Pendiente / no validable aquí:** Hopper (solo macOS), IDA (licencia), JADX,
Binwalk/Unblob, TShark, WABT, sigrok y observación en tiempo de ejecución
(navegador/Electron del usuario).

## Versión `43-caludecode.1` — reestructuración y documentación exhaustiva

**Parte 1 (propuestas aprobadas):**
1. Contradicción resuelta: `rea setup` solo fuera de CaludeCode; aquí `.mcp.json` o `rea-session.py`.
2. El entorno de CaludeCode pasa a ser la sección 1 de `SKILL.md`.
3. `SKILL.md` de 386 → 165 líneas; el bloque de rutas original se movió íntegro a
   `references/target-routing.md` y la sección "summary-first" original a `evidence-workflows.md`.
4. `SKILL.md` y todas las guías nuevas en español (las guías originales quedan en inglés, sin cambios).
5. `references/worked-examples.md`: 5 ejemplos de principio a fin con resultados reales.

**Parte 2 (más detalle y exhaustividad):**
- `references/cloud-cli-workflow.md`: cada comando validado con sintaxis, campos de salida,
  límites, errores conocidos con solución y tiempos medidos.
- `references/reporting.md`: niveles observado/inferido/desconocido, plantilla de respuesta,
  registro de hallazgos y pautas de reconstrucción.
- `scripts/rea-session.py`: varias llamadas MCP en una sesión. Medido: CLI ~16 s por consulta
  nativa; sesión MCP 15 s la primera y ~0,1 s las siguientes (8 consultas: ~16 s vs ~130 s).
- `.mcp.json`: declara el servidor `rea` (npx rea-agents@6.7.0) para usarlo como herramientas
  directas tras aprobarlo en Claude Code.
- Nuevas pruebas: `search` (cadenas y procedimientos), `xrefs`, `--snapshot` (no acelera),
  SQLite con `--table`/`--column`, `inspect-artifact` sobre ZIP (solo manifiesto raíz).

## Versión `43-caludecode.2` — prueba con binario real sin símbolos
Prueba de la skill con `/usr/bin/whoami` (coreutils, stripped): respondió cómo
obtiene el usuario (`geteuid` → `getpwuid` → `puts(pw_name)`). Lagunas
detectadas y documentadas (sección 4.7 de `cloud-cli-workflow.md`, ejemplo 6):
1. Imports ambiguos por nombre en Ghidra (externa/PLT/GOT) → usar dirección del stub.
2. `find_xrefs_to_name` no busca texto de cadenas → `rea xrefs <dirección>` o etiqueta de Ghidra.
3. `analyze_function` de un `main` ≈ 519 KB → extraer solo campos necesarios.
