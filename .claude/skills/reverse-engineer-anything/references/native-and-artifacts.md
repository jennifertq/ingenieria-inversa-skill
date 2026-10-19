# Artefactos nativos, administrados y empaquetados

## Metadatos de compilación de Go

Usa `inspect_go_binary` para un ELF, PE o Mach-O thin local explícito cuando la
pregunta se refiera a la versión del compilador embebida, las versiones de módulos/dependencias,
los reemplazos locales o la configuración de compilación. No se requiere `open_binary`, instalación de Go ni
ejecución del objetivo. El equivalente en la CLI es `inspect-go-binary PATH`.
Conserva el SHA-256 del artefacto, los rangos del archivo original, los bytes de módulo enmarcados y cada
línea de texto de módulo no analizada. Un registro ausente es un desconocido, no prueba de un
binario que no sea Go; los metadatos observados no autentican sus afirmaciones. La recuperación de funciones,
código fuente y tipos sigue siendo una cuestión aparte de análisis nativo.

## Metadatos de dependencias de Rust

Usa `inspect_rust_binary` para un ELF, PE o Mach-O thin local explícito cuando
la pregunta se refiera a la lista de crates de cargo-auditable embebida en `.dep-v0`
(Mach-O: `__DATA,.dep-v0`). No se requiere `open_binary`, instalación de Rust ni
ejecución del objetivo. El equivalente en la CLI es `inspect-rust-binary PATH`.
Conserva el SHA-256 del artefacto, el orden de los paquetes, los índices de dependencias y el rango
de archivo de la sección. Una sección ausente es metadato nulo, no prueba de que el binario no tenga
dependencias. Un tipo de paquete omitido permanece nulo. Un hash de commit de rustc se
infiere de una ruta de solo lectura `/rustc/<40-hex>/` y por sí solo no
identifica el compilador. Consulta [Binarios de Rust](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/rust-binaries.md).

## Instantáneas de SQLite

Usa `inspect_sqlite_database` con una instantánea local explícita de la base de datos para obtener su
esquema y, opcionalmente, filas de una única tabla ordinaria exacta. Requiere Node.js
24.x >=24.15 o 26+ con la API nativa `DatabaseSync.limits`. También consume el
`-wal` hermano existente; conserva ambos digests originales al citar su resultado.
La salida predeterminada es un inventario compacto; una tabla seleccionada expande solo su propio
esquema y muestrea 20 filas. Selecciona `columns` para evitar celdas irrelevantes o grandes,
y solicita `schema_scope: "database"` solo para obtener los detalles completos del esquema.
Elige `row_limit` cuando una muestra finita sea útil y mantén explícitos el truncamiento y
el orden de filas no especificado. Las tablas virtuales, las tablas shadow y las vistas son
hechos de esquema, no objetivos de lectura de filas. REA inspecciona copias privadas y deja
intactos los archivos fuente; obtén una instantánea coherente y en reposo de la base de datos/WAL
antes de la inspección. Consulta [Instantáneas de SQLite](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/sqlite-databases.md).

## Crashes de Linux registrados

Usa `inspect_recorded_crash` con una ruta explícita a un core ELF de Linux x86-64 para
inspeccionar registros históricos de hilos, señales, notas en bruto y rangos del archivo
original. Es independiente del objetivo activo del desensamblador. Los valores de registros
vinculados a la fuente y los bytes de notas son observaciones; las notas ausentes, la asociación
señal-hilo y la identidad actual del ejecutable/biblioteca siguen siendo desconocidas. Los PID son
metadatos históricos y nunca autorizan adjuntarse ni controlar procesos en vivo.

La faceta opcional `include_debugger_context` agrega candidatos de mapeo mediante
GDB/pwndbg proporcionado por quien llama, en una sesión propia solo sobre el core. Los nombres mostrados no
establecen la identidad actual del archivo; cero flags reportados dejan los permisos como desconocidos.
El contexto solicitado no disponible falla con indicaciones de configuración. Consulta
[crashes registrados](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/recorded-crashes.md)
para los perfiles exactos, los límites y la cobertura de verificación.

## Layout de ELF sin conexión

Usa `inspect_binary_layout` con una ruta explícita a un ELF local para obtener secciones
respaldadas por archivo, símbolos, relocalizaciones, nombres de enlace e inferencias estáticas de mitigaciones
sin abrir un objetivo de desensamblador. Cuando ese registro completo ya esté
retenido, llama a `inspect_analysis_view` para obtener un resumen, la faceta de mitigaciones o de enlace,
una sección o símbolo, o una página estable. No vuelvas a ejecutar el decodificador para
leer un solo objeto.

## WASM sin conexión

Usa `inspect_wasm_artifact` con WABT proporcionado por quien llama para los bytes locales seleccionados.
Para conteos, validación e identidad WAT, selecciona `detail: "summary"` en la primera
llamada MCP. El registro Evidence original completo permanece retenido; usa
`normalized_result.parent_evidence_id` para exports exactos o páginas de texto. Un detail omitido
o completo mantiene el resultado completo existente.
Para un resultado completado, usa `inspect_analysis_view` con su referencia retenida
reportada para obtener un resumen o `view: {kind: "wasm", facet: "exports", offset: 0, limit: 32}`.
Las facetas también incluyen (nombres en inglés tal como los usa la herramienta) sections,
imports, candidates, glue, WAT, headers, details y tool profile. Los offsets de texto cuentan unidades de código UTF-16; sigue `next_offset`.
La fuente completa permanece retenida tras una respuesta MCP de tamaño excesivo. No se implica
ejecución del objetivo ni adquisición por red, y WAT es una representación decodificada.

## Objetivos nativos

Después de `open_binary`, usa directamente herramientas enfocadas de búsqueda, procedimientos o funciones.
Usa `binary_overview` cuando los metadatos del objetivo o el contexto de inventario ayuden a responder la
pregunta. Prefiere la búsqueda literal, nombres, descompilación, callers, callees y
referencias cruzadas. Las direcciones y el pseudocódigo recuperado son observaciones de análisis,
no código fuente original. La indisponibilidad del proveedor y los metadatos no soportados siguen siendo
desconocidos en lugar de falsos.

Para un dossier completado de `analyze_function`, usa `inspect_analysis_view` con
`view: {kind: "native", facet: "value_flow_operations", offset: 0, limit: 32}`
y el Evidence ID retenido exacto para leer hechos seleccionados sin volver a analizar.
Las facetas nativas también incluyen (nombres en inglés tal como los usa la herramienta)
procedure, pseudocode, assembly, basic blocks, comments, callers/callees, references,
unresolved calls, referenced strings y names, el registro de la API nativa (native API)
y resúmenes de flujo de valores (value-flow). Los offsets y límites del pseudocódigo cuentan unidades
de código UTF-16; usa el `next_offset` devuelto para continuar. Las limitaciones del proveedor
y los hechos no disponibles permanecen explícitos; el registro Evidence padre completo se retiene.

`inspect_macho` sobre un framework grande devuelve megabytes de imports y exports.
Selecciona `detail: "summary"` para obtener la identidad del slice, el UUID y los conteos por colección,
y luego pagina las filas con `view: {kind: "macho", facet: "exports", offset: 0, limit: 64}`
y `normalized_result.parent_evidence_id`. Las facetas son entrypoints,
architectures, build_metadata, load_commands, dependencies, imports, exports,
segments y provenance. `source_exhaustive: false` significa que pueden existir símbolos
no devueltos.

Para ver qué funciones o métodos de Objective-C llama realmente un Mach-O en una
ejecución, usa `observe_native_calls` con breakpoints explícitos y un
`duration_ms`/`max_events` acotado. Lanza un proceso nuevo bajo LLDB, así que el objetivo
se ejecuta y puede modificar archivos o usar la red. Los objetivos con hardened runtime necesitan el
entitlement `get-task-allow`.

Usa `binary_session` sin argumentos para verificar el objetivo abierto, el
proveedor seleccionado y la alineación. Su `result.tool_availability` predeterminado contiene un
inventario completo agrupado por hechos compartidos. Expande los `names` de cada grupo y
hereda los requisitos de cliente a nivel de inventario, salvo que un grupo los sobrescriba;
la disponibilidad, los motivos, la remediación, los modos y los flags permanecen en línea. Los arreglos
`effects` y `annotations` nombran los flags verdaderos a partir de vocabularios fijos, así que un
flag conocido omitido es falso. `tools/list` sigue siendo la fuente canónica de los esquemas completos
de herramientas cuando cambia el estado del objetivo o del proveedor.

Los grupos de capacidades del proveedor contienen la identidad del proveedor y limitaciones ordenadas.
Antepone los `shared_limitations` de cada conjunto a los `limitations` de un grupo para recuperar la
lista ordenada completa de la operación. Las capacidades candidatas describen posibles
proveedores. Las capacidades de sesión de nivel superior describen la ruta actual, y
`analysis_provider_binding` identifica el proveedor seleccionado.

## Memoria estática y bytes del archivo original

Para Ghidra, `read_bytes` lee la memoria de análisis inicializada, incluidos los fixups
del loader; no lee un proceso en ejecución. Verifica `returned_bytes` y `complete`
antes de decodificar una tabla. Una lectura incompleta es cobertura faltante, no una cola
rellena con ceros. Usa `list_segments` para inspeccionar la inicialización del bloque seleccionado y los hechos
del espacio de direcciones, y conserva los hechos no disponibles como desconocidos.

Usa `address_to_file_offset` para anclar una dirección observada a los bytes del archivo
original. Un mapeo para la primera dirección no establece un mapeo contiguo
para toda una tabla, y los fixups del loader pueden hacer que los bytes de análisis difieran de los bytes
fuente. Mantén separados los rangos fuente y las observaciones de memoria de análisis.

Una tabla de punteros puede referirse a slots escribibles poblados por un constructor en lugar
de directamente a recursos inmutables. Un bloque no inicializado o un cero observado
no establece el valor posterior del slot en tiempo de ejecución. Sigue los `xrefs` y el ensamblador o pseudocódigo
del escritor correspondiente; distingue las asignaciones registradas del orden de ejecución
inferido. No reemplaces bytes ilegibles con ceros ni concluyas que un
recurso está ausente sin la evidencia de inicialización necesaria.

## DOS MZ con Ghidra

Para un objetivo DOS MZ admitido, usa `inspect_native_load_image` para verificar los bytes
cargados medidos, los mapeos de archivo, las relocalizaciones y la entrada contra la instantánea
inmutable. Mantén explícitos `mismatch` y `unsupported`. La importación verificada cubre la
imagen estática reportada, no el comportamiento en tiempo de ejecución de DOS ni del hardware PC-98.

Para la descompilación con Ghidra, `procedure_pseudo_code` también acepta `procedure: "file-offset:0x..."`; la CLI `rea decompile <path> --file-offset=0x... --provider ghidra` resuelve internamente el offset de bytes de la fuente. Un selector numérico de procedimiento con prefijo 0x no resuelto también recurre a un mapeo de archivo único. Los símbolos existentes y las direcciones de análisis tienen prioridad; varios mapeos fallan como ambiguos. Conserva las ubicaciones devueltas de file-offset y dirección, y las observaciones de selección en bruto. Las direcciones virtuales de ELF son distintas de los offsets de archivo; nunca asumas que un offset arbitrario más la base de la imagen es una dirección de análisis.

Los rangos completos del cuerpo de una función usan extremos inclusivos y pueden contener huecos. No
trates el intervalo envolvente como código.
Para objetivos empaquetados, conserva la identidad del artefacto original y la de los derivados por separado;
descompilar un stub de desempaquetado no recupera el programa desempaquetado.

Al leer metadatos de dispatch de Objective-C, distingue los métodos de implementación de clase
de los requisitos de protocolo: los métodos de clase reportan flags de requisito
nulos, mientras que las declaraciones de protocolo decodificadas conservan los hechos de requerido y opcional.
Los atributos de propiedad permanecen como tokens nombre/valor en bruto; usa el campo
`atomicity` de la propiedad para el marcador `N` decodificado o el comportamiento atómico predeterminado.
Los flags nulos de class/meta, los conteos de ivars, la atomicidad o los valores de solo lectura significan que el
proveedor seleccionado no estableció ese hecho. Los nombres de símbolos por sí solos no prueban
que una clase sea una clase raíz o que no tenga ivars.

## PE/CLI administrado

Comienza con `inspect_managed_artifact`. La inspección administrada canónica de REA es
libre de ejecución: no afirmes que cargó, reflejó, ejecutó ni resolvió el
ensamblado. Mantén explícitos los límites administrado/nativo y los hechos de reconstrucción no disponibles.
Un oráculo de reconstrucción aportado por el usuario es independiente del parser
canónico y no debe convertirse en una dependencia de configuración implícita.

Para preguntas de identidad/clasificación, `inspect_managed_artifact` puede seleccionar explícitamente
`detail: "summary"` en la primera llamada MCP. Retiene los metadatos completos
y devuelve una vista general enlazada con la clasificación/evidencia completa, módulo/MVID
anulables, frameworks, cobertura/problemas/limitaciones de metadatos y conteos de filas
devueltas. Las solicitudes completas predeterminadas no cambian. Lee las filas originales con
`inspect_analysis_view`, la fuente `normalized_result.parent_evidence_id` y
`view: {kind: "managed", collection: "attributes", offset: 0, limit: 16}`.
Las colecciones son `references`, `resources` y `attributes`. La paginación no
repite el análisis. Agotar las filas devueltas
no prueba metadatos completos ni ausencia bajo cobertura parcial/no disponible;
conserva los tokens locales de la compilación y su ámbito de artefacto/MVID.

`inspect_managed_members` siempre devuelve los `member_refs` de todo el ensamblado, incluso
para un solo tipo seleccionado. Para preguntas sobre un tipo seleccionado, selecciona
`detail: "summary"` con `type_names`; devuelve la selección (con los nombres
sin coincidencia), la cobertura y los conteos por colección. Pagina las filas con
`view: {kind: "managed-members", collection: "call_edges", offset: 0, limit: 64}`
sobre `types`, `exported_types`, `fields`, `methods`, `member_refs`, `call_edges`,
`field_accesses` o `user_strings`.

### .NET NativeAOT

Los binarios NativeAOT contienen código máquina nativo, por lo que los descompiladores CIL comunes
no pueden recuperar los cuerpos de método originales. Cuando faltan los metadatos administrados/CIL,
clasifícalo como una ruta de análisis nativo en lugar de afirmar una recuperación del código fuente.
Abre la imagen nativa con el proveedor profundo seleccionado e inspecciona funciones,
cadenas, llamadas y referencias; describe la salida del descompilador como pseudocódigo e
inferencia.

Las imágenes NativeAOT pueden ser ejecutables y bibliotecas compartidas PE/COFF, ELF o Mach-O.
Usa los bytes del archivo y los metadatos del loader en lugar de las extensiones para
identificarlas. Para apps empaquetadas, inventaría/extrae con las herramientas de artefactos de REA y conserva
la identidad exacta de la imagen contenida. Los archivos complementarios PDB, de depuración ELF o dSYM son
evidencia adicional solo cuando el proveedor los acepta y coinciden.

REA tiene un parser de instantáneas integrado de solo lectura para objetivos PE x64 con metadatos .NET 8 RTR
9.1. Un adaptador opcional de Ghidra headless agrega anotaciones en la base de datos y
una recuperación más amplia de metadatos en Linux; requiere un JAR de NativeAOT
configurado explícitamente. Son rutas independientes. El parser integrado también funciona en
Windows Ghidra P0; lee los literales congelados desde su reporte, porque
`search_strings` no los incluye. Consulta la
[guía de NativeAOT](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/ghidra-nativeaot.md)
para la configuración, los layouts soportados y las restricciones del host. Conserva la identidad del binario
y distingue los metadatos derivados de las observaciones de la base de datos de Ghidra. Los tipos
recuperados y el pseudocódigo nativo no son código fuente C# original. Windows Ghidra P0 no tiene
autoridad para mutar la base de datos.

## Paquetes y extracción

Usa `inspect_artifact` para bundles de aplicaciones, archivos comprimidos, ZIP/APK/IPA/MSIX/AppX,
ASAR o entradas DMG cuando el grafo de artefactos y los hallazgos ayuden a responder la
pregunta. Devuelve el grafo de artefactos completo en línea. Cita los IDs del manifiesto del grafo
cuando los uses.

Para un IPA o un `.app`, ZIP o DMG de macOS, pasa el registro Evidence del inventario a
`project_apple_application_graph`. Reporta las raíces de aplicación y los bundles anidados
por convención de rutas: extensiones de app, servicios XPC, frameworks, elementos de inicio
de sesión, extensiones de sistema y de drivers, y plug-ins. También lista los helpers
privilegiados, los plists de launchd, los symlinks y el `info_plist_path` de cada bundle y sus
ejecutables candidatos. Los roles son convenciones de rutas, no plists analizados; lee los
plists listados con `inspect_plist`.

Después de `open_binary` sobre un `.app` o Mach-O, usa `trace_dylib_resolution` para ver
a qué archivo llega cada carga `@rpath`, `@loader_path` y `@executable_path` para
cada ejecutable del bundle. También lista las cargas faltantes o débiles y los candidatos
`@rpath` anteriores que están ausentes. Acota los bundles grandes con `roots` o
`architecture`. Las rutas del sistema quedan sin determinar porque las provee la dyld shared cache.

Usa `extract_artifact` cuando se necesiten archivos materializados. Extrae el objetivo
activo y acepta `integrity_policy` opcional; consulta los [contratos MCP](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/mcp-contracts.md).
Materializa todos los archivos regulares en un directorio temporal nuevo elegido por
REA. Los symlinks y las entradas cifradas son hechos del inventario, no archivos extraíbles.
El resultado reporta el directorio materializado; quien llama no elige el
destino. No se necesita ningún permiso adicional.

El recorrido nativo de DMG usa automáticamente un montaje de solo lectura en hosts macOS
soportados, con un directorio de montaje temporal propio y limpieza. No necesita flag de
aprobación. Los hosts no soportados o los fallos de montaje siguen siendo limitaciones explícitas; no
afirmes un inventario de hijos cuando solo está disponible la identidad raíz. La extracción es una
operación aparte que escribe en el sistema de archivos.

Para DOS COM sin encabezado, abre explícitamente con `format: "dos-com"` (CLI
`--target-format dos-com`). Inspecciona la imagen de carga antes de confiar en el análisis
de funciones: la entrada es `0x10100`, offset de archivo cero, con contexto de segmento en modo real
impuesto. El estado de PSP/pila/dispositivos sigue sin modelarse. Consulta la [guía de DOS](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/ghidra-dos.md).

Para otras imágenes sin encabezado (firmware embebido sin encabezados ELF/Mach-O/PE/MZ),
abre con `format: "raw-binary"`, `architecture` (`x86`, `x86_64`,
`arm`, `arm64`, `6502` o `m68k`) y `entry_point` (hex `0x`). El offset de archivo 0 se mapea en
esa dirección. Hopper e IDA rechazan esta interpretación; Ghidra usa
`BinaryLoader` con un lenguaje genérico: big-endian para `m68k`, little-endian
en los demás casos. Las variantes ARM big-endian, solo Thumb y Cortex-M no están soportadas.
`6502` selecciona NMOS 6502; la entrada y el mapeo completo del archivo deben caber dentro de
`0x0000..0xffff`. 65C02, 65816, contenedores de cartuchos, bank switching y la semántica de
mappers no están soportados. `m68k` requiere una entrada par y decodifica el superconjunto 68040
de la familia 68000; los contenedores Amiga/Atari y el descubrimiento de la entrada mediante la tabla de vectores
no están soportados. Windows Ghidra P0 admite imágenes raw solo para `6502`. Consulta la [guía de binarios raw](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/raw-binary.md).

### Anotaciones de funciones en Ghidra

Usa `annotate_native_function` para el nombre y/o los comentarios de entrada de una función, con al menos un cambio explícito. Revisa en línea la lectura de la anotación y el dossier actualizado. Los cambios son atómicos y de ámbito de sesión; los comentarios vacíos los borran, los campos omitidos los conservan. Las llamadas MCP posteriores observan las ediciones hasta el cierre. La CLI `annotate-native-function` devuelve el análisis actualizado antes de descartar la sesión. Los bytes del ejecutable original no cambian; las ediciones invalidan las instantáneas inmutables. Windows P0 no admite mutaciones de la base de datos. Solo para renombrar, `set_address_name` / `set_addresses_names` también funcionan con Ghidra: nombran entradas de funciones o direcciones de datos (etiquetas primarias) y devuelven booleanos compactos de éxito por dirección en lugar de un dossier.

## Inventario de recursos PE sin conexión

Usa `inspect_pe_resources` con un `path` absoluto, o
`rea inspect-pe-resources ./selected.exe --json`, para la inspección portable de recursos PE32/PE32+
sin abrir un objetivo nativo. Conserva el registro Evidence devuelto:
IDs de tipo/nombre/idioma y nombres UTF-16, rangos originales de directorio/datos/payload,
páginas de código, hashes de payload y referencias estáticas a grupos de íconos. La resolución de íconos
del mismo idioma es explícita; las referencias faltantes y las discrepancias de tamaño permanecen visibles.
Los demás payloads son opacos, y esta operación no decodifica imágenes ni simula
la carga de recursos de Windows. Consulta los presupuestos y el perfil de árbol soportado en
[diagnóstico de binarios sin conexión](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/binary-diagnostics.md).

Para diferencias exactas de imports/exports del módulo core, usa `compare_wasm_interfaces`
con dos registros Evidence de inspección completos (o referencias retenidas de la sesión actual)
y un ámbito explícito. Conserva los tipos desconocidos/nombres duplicados; la igualdad estática
de interfaces no es compatibilidad en tiempo de ejecución. La CLI acepta Evidence completo en línea
en `rea compare-wasm-interfaces input.json --json`.
