# Conexión y recuperación de tareas

> **CaludeCode:** en este repo no ejecutes `rea setup` (instalaría la skill
> original en `~/.claude/skills` y taparía la adaptada). El servidor ya está
> declarado en `.mcp.json`; si no aparece, apruébalo en Claude Code o usa
> `scripts/rea-session.py`. Los pasos de `setup` de abajo son para otros equipos.

Lee esta guía solo ante un bloqueo observado de conexión, comando, aprobación o
proveedor. Mantén a la vista el objetivo y la pregunta del usuario. Explica qué
impidió la operación y cuál es el siguiente paso útil; tras la reparación,
continúa la investigación.

Los comandos de abajo usan un `rea` instalado. Si no hay ninguno disponible, usa
la invocación del paquete indicada en `SKILL.md` cuando esté autorizado adquirir
REA. Sigue los esquemas del servidor conectado y la ayuda de la CLI instalada en
lugar de suponer que la rama principal del repositorio y una versión anterior
exponen los mismos argumentos.

## Elige el remedio según la falla observada

| Observación                                                     | Significado y siguiente paso                                                                                                                                                                                                                                                                                          |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No hay herramientas de REA en la sesión activa                  | Inspecciona el registro con `rea doctor --client claude_code --json`. Instalar solo la skill no registra MCP.                                                                                                                                                                                                       |
| Registro ausente, mal formado u obsoleto                        | Prepara un plan de configuración acotado; aplica solo los cambios autorizados, con copias de respaldo.                                                                                                                                                                                                                |
| Registro alineado, pero sin herramientas conectadas             | Reinicia/reconecta el cliente. Doctor verifica el registro; no puede establecer la conexión del agente actual. Inspecciona el error de arranque del cliente si la reconexión falla.                                                                                                                                  |
| `MCP tool call requires approval, but approval policy is never` | Codex rechazó la llamada antes de que REA la ejecutara. No instales un motor ni repitas la configuración para resolver esta decisión de política del cliente. Consulta la sección de aprobación más abajo.                                                                                                           |
| REA devuelve `provider_unavailable` o una entrada de herramienta no disponible | Lee el diagnóstico del proveedor de esa operación o `binary_session.result.tool_availability`. Expande los nombres de herramientas de cada grupo y hereda los requisitos compartidos del cliente salvo que se sobrescriban. Usa la disponibilidad, el motivo y la remediación de la operación; un catálogo completo de herramientas no implica que todas las operaciones estén disponibles. |
| Falta `rea` en un shell hijo, o Node es incompatible            | Inspecciona el PATH real del shell y el lanzador/runtime. Una instalación con prefijo puede no estar en el PATH de un shell de inicio de sesión; esto no demuestra que el registro MCP esté roto.                                                                                                                    |

Si el cliente no puede lanzar su helper de shell/sandbox o leer la skill
instalada, inspecciona su diagnóstico de arranque. Por ejemplo, Codex puede
rechazar alias de helpers cuando CODEX_HOME está bajo `/tmp`; usa un perfil
autorizado fuera del directorio temporal del sistema operativo. La configuración
de REA no puede reparar el ejecutor del cliente. Conserva el sandbox en lugar de
desactivarlo silenciosamente para que funcione un comando de análisis.

El JavaScript estático y el inventario de ZIP comunes no necesitan Hopper ni
Ghidra. La inspección de HAR es offline y no requiere un navegador en vivo. La
descompilación nativa, el análisis de Android y la extracción de firmware tienen
sus propios prerrequisitos que aporta el usuario. Usa inventario/evidencia
estática compatible cuando responda parte de la pregunta, y nombra por separado
la evidencia no disponible. No sustituyas el objetivo por otro. Etiqueta como
tales las observaciones hechas con herramientas comunes de shell; solo la salida
real de REA aporta Evidence de REA.

## Repara el registro cuando sea necesario

Para Claude Code:

```bash
rea doctor --client claude_code --json
rea setup --client claude_code --dry-run --json
```

Usa el ID del cliente compatible actual: `claude_code`, `claude_desktop`, `codex`,
`cursor`, `gemini_cli`, `windsurf`, `devin`, `opencode`, `antigravity`,
`copilot_cli`, `commandcode`, `qwen_code`, `vscode`, `trae`, `grok_build`, `omp`, `pi`,
`hermes`, `qoder`, `droid`, `zcode`, `dsh` o `grok_bot`. Si no lo conoces, inspecciona `doctor --json` antes de elegir un
alcance. `grok_bot` usa un paso de registro por chat en lugar de un `mcp.json` local.
Para clientes no compatibles, usa registro stdio manual con versión fijada o la CLI.

Muestra las rutas exactas del plan, las copias de respaldo, los cambios y el
reemplazo de la skill incluida. Obtén aprobación para las escrituras cuando ese
alcance concreto no esté ya autorizado y luego aplica el mismo alcance con
`rea setup --client claude_code --yes`. Agrega
`--install-hopper` solo cuando se necesite por separado y se apruebe explícitamente. No instales ni actualices
prerrequisitos no relacionados. Reinicia/reconecta, verifica que las
herramientas realmente aparezcan y retoma la tarea original. Si siguen
ausentes, inspecciona la falla de arranque en lugar de repetir la configuración
en bucle.

## La aprobación de herramientas de Codex es independiente de que REA esté listo

Las herramientas de REA no tienen un protocolo de concesión de permisos. Aun así,
Codex puede requerir aprobación porque una operación crea recursos propios, lanza
un helper o tiene efectos de limpieza. Una herramienta anunciada o un resultado
exitoso de doctor no anula esa política del cliente. `workspace-write` por sí solo
no resuelve un rechazo de aprobación de MCP, y `approval_policy = "never"` no
significa que todas las herramientas MCP estén preaprobadas.

Cuando haya aprobación interactiva disponible, usa el flujo de aprobación del
cliente para la operación solicitada. En una ejecución desatendida, continúa con
un flujo de CLI autorizado si el entorno de ejecución lo permite, o informa la
operación bloqueada y la aprobación necesaria para continuar. No reintentes la
misma llamada rechazada, no amplíes silenciosamente las aprobaciones ni
reescribas los efectos de MCP como de solo lectura.

Para un operador que quiera explícitamente preaprobar operaciones concretas en un
perfil desechable de Codex, la versión actual de Codex admite configuración por
herramienta. Por ejemplo, abrir y cerrar una sesión de análisis se puede acotar
de forma independiente:

```toml
[mcp_servers.rea.tools.open_binary]
approval_mode = "approve"

[mcp_servers.rea.tools.close_binary]
approval_mode = "approve"
```

Usa el ID real del servidor y solo las operaciones cuyos efectos se aprobaron;
este ejemplo no aprueba inspección, extracción ni ejecución en runtime.
Muestra la edición de configuración propuesta y conserva las entradas no
relacionadas y las copias de respaldo antes de escribir. Una política
administrada puede restringir la configuración del cliente. Consulta la
[referencia de configuración de Codex](https://learn.chatgpt.com/docs/config-file/config-reference)
para ver los ajustes compatibles del cliente instalado. Esta es una opción de
recuperación opcional, no un prerrequisito para toda tarea de REA.

## Continúa mediante una CLI instalada

Verifica el entorno de comandos solo si el lanzador falla:

```bash
command -v rea
command -v node
node --version
rea --version
```

Usa el lanzador público en su ruta de instalación conocida con un Node existente
y compatible en el PATH cuando el shell hijo pierda una instalación con prefijo.
Evita los puntos de entrada internos `dist/cli.js` o los cambios globales de
toolchain. MCP puede tener su propio lanzador válido aun cuando un shell no pueda
resolver `rea`.

Para un árbol JavaScript o ASAR aportado por el usuario, elige los archivos de
salida en el espacio de trabajo autorizado y guarda la Evidence completa antes de
leer una vista:

```bash
rea analyze-javascript-application /absolute/path/to/app --json > app-evidence.json
jq -c '{source: {kind: "inline", evidence: .}, view: {kind: "summary"}}' app-evidence.json > app-view.json
rea inspect-analysis-view app-view.json
```

Estos comandos no registran MCP ni instalan un motor de análisis. El JSON de
JavaScript de la CLI es completo y puede ser muy grande; redirígelo en lugar de
cargarlo en el contexto. Usa un procesador JSON existente si falta `jq`, sin
instalar uno solo para esta receta. Inspecciona una página de módulo o un ítem
usando la misma fuente inline y las [recetas de JavaScript](javascript-applications.md).
Conserva la cobertura del grafo, las limitaciones y las incógnitas. El análisis
nativo por CLI sigue requiriendo el motor seleccionado, y todas las operaciones
de CLI conservan los permisos de ejecución del host.
