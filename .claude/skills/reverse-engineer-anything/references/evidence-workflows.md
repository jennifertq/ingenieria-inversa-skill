# Flujos de trabajo de Evidence, comparación y verificación

Las herramientas que producen Evidence devuelven el registro de Evidence completo
directamente en el `structuredContent` de MCP y en el JSON de la CLI. Lee
`normalized_result` para los datos de la operación y cita `evidence_id` cuando otra
herramienta o tu explicación necesite una referencia estable. Conserva la
autoridad, las limitaciones, la cobertura y las incógnitas residuales. Si un
resultado está incompleto o paginado, continúa solo cuando los datos restantes
importen para la tarea; no obtengas un bundle o recurso solo para leer un
resultado que ya se devolvió inline. Cuando ya esté retenida la Evidence completa
de `inspect_binary_layout` o
`analyze_javascript_application`, llama a
`inspect_analysis_view` para obtener un resumen, una sección/símbolo/módulo o una
página estable en lugar de repetir el productor.

El inventario completado de `inspect_artifact` también admite un resumen y
`view: {kind: "inventory", collection: "occurrences", logical_paths: ["package.json", "main.js"]}`.
Omite `logical_paths` para paginar todas las ocurrencias disponibles; `[]` no selecciona ninguna.
Las otras colecciones de inventario son `nodes`, `edges` e
`integrity_contradictions`. Mantén `source_complete` separado del agotamiento de
páginas: la falta de una coincidencia en Evidence de origen parcial no demuestra
ausencia. Usa el ID de Evidence padre devuelto para las vistas posteriores y
exporta antes de cerrar la sesión cuando el origen deba sobrevivirla.
Cuando `tools/list` anuncie `inspect_artifact.detail`, solicita `"summary"` para
retener su origen completo y recibir esa vista de inmediato. Sin esa opción
anunciada, mantén la llamada completa existente. La inspección por CLI devuelve
Evidence completa y portable; guárdala antes de proyectar una vista inline seleccionada.

Usa `record_unknown` para dar seguimiento a las preguntas sin resolver de la
investigación del usuario y nombrar la autoridad o el entorno que aún se
requiere. Proporciona los IDs de evidencia que apoyan y que contradicen. Actualiza
directamente el registro de la sesión.
Usa `update_unknown` con la revisión actual; vuelve a leer tras una revisión
obsoleta en lugar de reintentar a ciegas. Solo la evidencia observada que califique
puede verificar una resolución.

Usa comparaciones con conjuntos de páginas completos y compatibles cuando afirmes
equivalencia o ausencia:

- `compare_artifacts` compara páginas de inventario por ruta de ocurrencia,
  contenido, metadatos y relaciones del grafo.
- `compare_functions` compara Evidence de funciones explícitas, no coincidencias
  difusas de binarios completos.
- `compare_bundles` compara la membresía canónica del bundle y el historial de
  incógnitas.
- `find_changed_behavior` combina comparaciones existentes; las diferencias
  estáticas siguen siendo candidatas, no prueba causal.
- `build_call_path` necesita dossiers de funciones explícitos de un mismo
  artefacto/proveedor; una frontera incompleta hace que la ausencia sea desconocida.
- `correlate_static_and_runtime` usa mapeos explícitos; los patrones coincidentes
  son hipótesis, no causalidad.
- `verify_reconstruction` evalúa una especificación tipada finita. Un resultado
  aprobado cubre solo las afirmaciones comparables declaradas, no la equivalencia global.

Las capturas de procesos son evidencia de comportamiento opcional (opt-in), no un
sandbox de seguridad. Las capturas V3 no se pueden actualizar a V4; vuelve a
ejecutar el escenario original. Distingue la salida de la raíz de la finalización
de los descendientes y exige frescura cuando la tarea lo necesite.
Un objetivo que agota el tiempo y debe escribir un informe final necesita
`finalization_ms`: REA envía SIGTERM a la raíz capturada, sigue observando y envía
SIGKILL una vez solo si el objetivo no ha terminado al final del intervalo.
`exit.finalization.signals` lista cada intento con su resultado de entrega; la
señal de salida observada queda en `exit.signal`, `exit.code` es null en toda
salida por plazo vencido, y el código de un finalizador que terminó por sí solo
está en `exit.finalization.exit_code` (null en una salida por señal o cuando no se
observó ninguna salida).

Usa `inspect_analysis_view` con `view: {kind: "api-surface"}` sobre Evidence HAR
retenida de `inspect_web_network_capture` para agrupar las líneas de solicitud
observadas por método, origen y plantilla de ruta. Las coincidencias de formato
son inferencias, no identidad del handler ni esquemas. Las páginas de grupos
citan ordinales de registros padre; consulta la cobertura de registros y las
exclusiones antes de afirmar completitud. No se reproduce ninguna solicitud.
Cuando el esquema conectado anuncie `include_query_parameter_names`, selecciónalo
en la vista para obtener los nombres observados distintos con los ordinales de
registro originales. Los valores de query se omiten; los nombres no establecen
parámetros obligatorios ni un esquema completo del servidor. Conserva la Evidence
padre original para las URLs exactas.

Usa `inspect_analysis_view` con `view: {kind: "environment-manifest"}` sobre la
misma Evidence HAR retenida para proyectar las líneas de solicitud del origen
principal en herramientas con nombre, con plantillas de ruta, parámetros, nombres
de query observados, formas de body sin valores y punteros a registros para un
entorno de agente. Activa `template_rules` solo cuando los identificadores
registrados lo necesiten; cada plantilla, parámetro y hermano fusionado es una
inferencia, no se copia ningún valor de header, cookie o body, y las tres
incógnitas declaradas permanecen sin resolver.

## Trabajar primero con resúmenes


Empieza con el resultado predeterminado y usa su Evidence inline y el contexto
del grafo. Para una aplicación JavaScript o un layout ELF de tamaño desconocido o
grande, llama a `analyze_javascript_application` o `inspect_binary_layout` con
`"detail": "summary"` y luego inspecciona el `parent_evidence_id` retenido con
`inspect_analysis_view`.
Pagina las identidades de módulos y selecciona el `node_id` devuelto antes de
solicitar un ítem; una sola ruta de archivo puede representar varios roles del
grafo. No repitas un análisis idéntico ni una llamada rechazada sin un cambio en
la entrada o un bloqueo resuelto.
Vuelve a verificar el estado de la sesión cuando un cambio de ciclo de vida haga
útil ese estado. Haz un seguimiento focalizado solo cuando el resultado devuelto
deje sin responder una pregunta específica.

Si MCP informa `resource_constraint` con `details.resource: "transport"`, llama a
`inspect_analysis_view` con la referencia de Evidence de la misma sesión que
informó, para obtener un resumen, una sección/módulo o una página estable. Usa
`trace_application_feature` una vez que se conozca una semilla, o llama a
`export_evidence_bundle` para escribir la sesión completa en una ruta
seleccionada. El análisis sigue completo en el ledger; evita repetirlo solo para
solicitar la misma respuesta sobredimensionada. La salida JSON completa de la CLI
también se transmite sin un único frame de MCP.

Cuando se desconozca el ID padre retenido, usa `get_evidence_bundle` con
`detail: "summary"` y filtros exactos por operación, SHA-256 del objetivo, digest
del perfil de análisis o dirección canónica del procedimiento. Selecciona el ID de
Evidence devuelto para la siguiente vista en lugar de solicitar el bundle completo.
`retention: "complete-record"` significa que el registro completo está almacenado;
el truncamiento nativo de flujo de valores y los metadatos desconocidos siguen
siendo aparte. Para un bundle portable exportado, usa `rea inspect-evidence-bundle`
con un JSON que contenga `path`, `detail: "summary"` y los mismos `filters`. Leer
ese archivo sigue requiriendo validar todo su contenido dentro del presupuesto de
memoria local.

Un cliente también puede truncar un resultado exitoso de herramienta sin un error
de transporte de REA. Trata esa vista previa como incompleta; usa el ID padre
retenido para vistas más pequeñas o exporta cuando se necesite el registro
completo. No analices la vista previa como JSON canónico ni repitas el productor.
Para JavaScript, lee las
[recetas de vista de módulos y de trazado](javascript-applications.md) antes de
profundizar en un grafo grande; un trazado bidireccional amplio puede expandir
relaciones de contención no relacionadas incluso después de un análisis resumido.

Toda conclusión debe distinguir observaciones, inferencias e incógnitas. Cita IDs
de Evidence, conserva las limitaciones y la cobertura incompleta, y nunca des a
entender que el análisis estático observó una ejecución. Las solicitudes de
runtime ejecutan el objetivo y el ciclo de vida declarados; no amplíes el
objetivo ni la acción más allá de esos campos.

Dentro de la investigación solicitada por el usuario, llama directamente a las
herramientas de análisis disponibles. REA no requiere concesiones de permisos ni
indicadores de aprobación por llamada. El cliente del agente puede requerir
aprobación de forma independiente. Sigue el alcance declarado de la solicitud y
los requisitos reales de acceso del host; usa la guía de recuperación ante un
rechazo observado por política del cliente.
