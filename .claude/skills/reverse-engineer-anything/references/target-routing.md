# Rutas por tipo de objetivo

Esta es la referencia detallada de rutas de la skill. Los nombres de
herramientas son herramientas MCP; los equivalentes de CLI usan guiones
(`inspect_go_binary` → `rea inspect-go-binary`). Las rutas validadas en el
entorno cloud de CaludeCode se listan en [cloud-cli-workflow.md](cloud-cli-workflow.md).


Elige la primera herramienta según el objetivo que proporcionó el usuario. Usa `open_binary` para
flujos de trabajo nativos o de archivos comprimidos con objetivo activo; las herramientas sin objetivo reciben su propia
ruta o endpoint explícito y no lo necesitan.

- Archivo ASAR o árbol JavaScript/Electron extraído:
  `analyze_javascript_application`.
- Inventario de miembros de archivo comprimido/paquete (ZIP/APK/IPA/MSIX/AppX o DMG):
  `open_binary` con la ruta local proporcionada; usa `inspect_artifact` cuando su
  grafo y sus hallazgos ayuden a responder la pregunta.
- Código, clases, métodos o referencias entrantes de un APK de Android:
  `inspect_android_package`, luego herramientas de Android específicas cuando estén anunciadas.
  El inventario de miembros del archivo comprimido sigue usando la ruta de archivos comprimidos anterior.
- Ensamblado PE/CLI administrado: `inspect_managed_artifact`.
- Imagen de firmware: `inspect_firmware_regions` cuando esté anunciada. Usa
  `extract_firmware` cuando se solicite extracción, con un directorio de salida absoluto nuevo
  elegido por quien llama. Estas herramientas usan Binwalk/Unblob proporcionados por quien llama en
  Linux; consulta la [guía de firmware](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/firmware-analysis.md).
- PE/ELF .NET NativeAOT: análisis nativo con Ghidra. El código nativo puede producir pseudocódigo;
  consulta el flujo de trabajo de NativeAOT en [native-and-artifacts.md](native-and-artifacts.md) para
  la recuperación opcional de metadatos y su límite de host/diseño soportado.
- Página de navegador del usuario ya abierta: `list_browser_targets`.
- Acción de navegador que el agente debe realizar (hacer clic, escribir, navegar):
  `capture_browser_scenario` con acciones declaradas. Consulta
  [observación en tiempo de ejecución](runtime-observation.md) para conectar/lanzar
  y las herramientas de navegador específicas de seguimiento.
- Tráfico de Fiddler Everywhere o una captura `.saz` nativa: lee el
  [flujo de trabajo de Fiddler](runtime-observation.md#fiddler-everywhere-traffic-debugging).
  Inspecciona SAZ guardados con `inspect_web_network_capture` y `format: "saz"`;
  conecta el servidor MCP independiente de Everywhere para tráfico en vivo.
- Captura retenida HAR/SAZ/mitmproxy nativa/qlog de aioquic: `inspect_web_network_capture`. Selecciona
  los ordinales de registro originales cuando sea útil; inspecciona campos del productor y archivos
  auxiliares de bytes/números sin obtener las URL registradas ni afirmar atribución en vivo. Consulta
  [capturas históricas](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/web-network-captures.md) para el
  perfil exacto del formato de origen y las exclusiones de credenciales. El soporte de qlog comienza con aioquic 1.5.0
  JSON 0.3; la cobertura de streams y las declaraciones de pérdida del endpoint no recuperan cuerpos
  ni establecen pérdida de red. Prefiere detail summary, luego páginas de kind qlog trace/stream;
  selecciona una traza, un ID de stream y una dirección para páginas de contribución/rango.
  Los hechos conservan el alcance de todos-los-eventos-registrados-antes-de-la-selección. Otros diseños de qlog
  y la correlación con PCAP no están soportados.
- Runtime de Electron del usuario ya abierto: `list_electron_targets`. Antes de un intento de Inspector en electron-main, verifica los fuses empaquetados con `inspect_electron_fuses`; `EnableNodeCliInspectArguments` deshabilitado significa que la app ignora `--inspect`.
- Descubrimiento de campos de paquetes: `inspect_packet_fields` busca protocolos instalados
  y nombres/tipos de campos antes de elegir campos para `inspect_packet_capture`.
  Consulta/pagina los registros relevantes; los registros de protocolos no establecen tráfico observado.
- Capturas de paquetes grabadas: `inspect_packet_capture` con campos de TShark seleccionados,
  filtros de visualización y reglas decode-as. Requiere Linux, prlimit de util-linux y `REA_TSHARK_COMMAND`; consulta la
  [guía de capturas](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/packet-captures.md).
  Los límites de paquetes cuentan paquetes de entrada antes del filtrado. La salida por defecto es de 50
  tramas coincidentes; usa `match_offset` / `match_limit` para páginas posteriores, o un límite null
  explícito para la salida coincidente completa. Conserva el digest de origen entre páginas.
  Esto no realiza captura en vivo.
  Para resúmenes de direcciones/DNS/SNI/protocolos usa `inspect_pcap_capture` con MCP
  detail summary, luego páginas retenidas de kind pcap. Requiere tshark de Wireshark 4.x
  y capinfos, con prlimit de Linux o Job Objects de Windows; consulta
  [resúmenes de paquetes](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/pcap-analysis.md).
  Selecciona una pregunta DNS exacta para páginas de direcciones; el agotamiento de páginas no prueba
  la completitud de la red. Esto lee grabaciones y no adquiere tráfico.
- Descubrimiento de decodificadores: `inspect_signal_decoders` busca IDs de decodificadores instalados
  o la ayuda de un decodificador seleccionado, incluidos canales y opciones. Consulta y pagina los
  detalles relevantes antes de elegir la configuración; esto no escanea hardware.
- Trazas lógicas/de señales grabadas: `decode_signal_recording` con decodificador,
  canal y configuración de protocolo explícitos. En Linux con prlimit de util-linux, proporciona sigrok-cli 0.7.2 mediante
  `REA_SIGROK_COMMAND`; consulta la [guía de grabaciones](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/signal-recordings.md).
  La salida por defecto es de 50 líneas literales; selecciona clases de anotación y pagina con
  `line_offset` / `line_limit`, o null explícito para toda la salida restante.
  Los conteos de ventana son líneas mostradas, no anotaciones ni muestras. Conserva los digests de origen entre páginas.
  Esto lee archivos existentes; no adquiere señales de hardware.
- Artefacto WebAssembly local explícito: `inspect_wasm_artifact`. Proporciona WABT 1.0.42
  mediante `REA_WABT_BIN_DIRECTORY`; conserva la identidad exacta de bytes/herramienta y el WAT decodificado.
  Selecciona explícitamente el código de enlace JavaScript y las rutas candidatas, y conserva la
  ambigüedad de URL/ruta. Sin obtención implícita ni ejecución del objetivo; el WAT no es el código fuente original.
  Consulta la [guía de WASM](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/wasm-artifacts.md).
- Portador local explícito de bytecode EVM: `inspect_evm_interface` con codificación `raw` o `hex`
  elegida por quien llama. Conserva los digests del portador/decodificado y trata los selectores,
  las cadenas de argumentos y la mutabilidad como candidatos inferidos; esto no realiza búsqueda en la
  cadena ni ejecución del objetivo. Para la interfaz inferida completa sin hex ni
  stdout duplicado, descubre el soporte y selecciona `detail: "summary"`; la Evidence
  completa queda retenida bajo su identidad original. Usa el
  `parent_evidence_id` devuelto para páginas exactas de función o de `bytecode_hex`/stdout/stderr.
  La cobertura de candidatos no establece la completitud de la interfaz. Consulta la
  [guía de bytecode EVM](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/evm-bytecode.md).
- Metadatos embebidos del compilador, módulos o configuración de compilación de Go: `inspect_go_binary`
  con el archivo local explícito. Esta inspección integrada sin objetivo no requiere
  instalación de Go ni desensamblador. Conserva los bytes crudos del módulo y los rangos de origen;
  la ausencia de metadatos no prueba que un binario no sea Go, y los registros de texto no analizados
  permanecen explícitos. Consulta la
  [guía de binarios Go](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/go-binaries.md).
- Metadatos embebidos de dependencias Rust de cargo-auditable: `inspect_rust_binary`
  con el archivo local ELF, PE o Mach-O thin explícito. Esta inspección integrada
  sin objetivo no requiere instalación de Rust ni desensamblador. Conserva
  el orden de paquetes, los índices de dependencias y el rango de archivo de la sección. Una sección
  `.dep-v0` ausente es metadato null, no prueba de que el binario no tenga dependencias.
  Un hash de commit de rustc es una inferencia a partir de una ruta de solo lectura `/rustc/<40-hex>/`.
  Consulta la
  [guía de binarios Rust](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/rust-binaries.md).

- Instantánea local explícita de base de datos SQLite: `inspect_sqlite_database`. Inspecciona
  con Node.js 24.x >=24.15 o 26+ que proporcione límites nativos de SQLite. Lee primero el esquema
  (inventario compacto por defecto), o selecciona una tabla ordinaria exacta
  y `columns` cuando se necesiten filas. Los valores por defecto son el esquema de la tabla seleccionada y
  20 filas; solicita `schema_scope: "database"` para el esquema almacenado completo. Conserva la identidad tanto de la base de datos como del WAL hermano existente; las muestras de filas
  informan truncamiento y tienen orden no especificado. Usa una instantánea en reposo en lugar
  de suponer que un par base de datos/WAL en vivo se copió de forma atómica. Consulta la
  [guía de SQLite](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/sqlite-databases.md).
- Archivo ELF de Linux explícito para diseño, símbolos, reubicaciones o evidencia estática de
  mitigaciones sin conexión: `inspect_binary_layout`. Esta operación sin objetivo usa
  pwntools proporcionado por quien llama sin abrir una base de datos de desensamblador. Conserva sus
  ubicaciones crudas y sus límites de inferencia/cobertura; consulta la
  [guía de binarios sin conexión](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/binary-diagnostics.md).
- Core ELF de Linux x86-64 proporcionado: `inspect_recorded_crash`. Lee cada hilo
  registrado, nota cruda y registro vinculado al origen sin abrir un objetivo en vivo.
  Los PID históricos no seleccionan procesos en vivo. Solicita `include_debugger_context`
  solo cuando los candidatos de mapeo exclusivos del core ayuden; consulta la
  [guía de fallos registrados](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/recorded-crashes.md).
- Árboles de tipo/nombre/idioma de recursos PE y referencias estáticas de grupos de iconos:
  `inspect_pe_resources` con una ruta explícita. Esta operación portable no requiere
  objetivo activo ni motor; las cargas opacas conservan rangos de archivo y SHA-256.
- Ejecutable nativo, biblioteca o base de datos de análisis: `open_binary`, luego
  usa directamente las herramientas de análisis específicas; llama a `binary_overview` cuando el contexto de metadatos o
  inventario sea útil y esté disponible desde el proveedor seleccionado.

Para una configuración existente de IDA MCP, usa `open_binary` con el binario de
entrada original y `provider_id: "ida"`; no pases una base de datos `.idb` ni `.i64`.
El perfil adjunto heredado vincula la entrada de la GUI ya abierta por SHA-256 y
deja su base de datos abierta. El perfil headless moderno crea y cierra una
base de datos privada propia sin guardar. La instalación y el registro reutilizan
[mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp); consulta la
[guía del proveedor IDA](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/ida-provider.md).
Pasa directamente a `analyze_function`, pseudocódigo o búsquedas de funciones/cadenas
después de abrir; IDA no proporciona `binary_overview`. Consulta la disponibilidad de la sesión
al componer flujos de trabajo más amplios. Los llamadores directos modernos y las facetas de dossier no soportadas
siguen siendo desconocidos; los resultados de IDA en vivo no se reproducen desde instantáneas.

Con `REA_KUNA_COMMAND` configurado, `provider_id: "kuna"` responde listas de
procedimientos, búsquedas, pseudocódigo, ensamblador y `analyze_function` desde la exportación
en caché de todo el programa de Kuna. Los llamadores/llamados usan un grafo separado sin cuerpos compartido por
la sesión; `xrefs` devuelve sitios entrantes de dirección exacta y filtra los alias de
reenvío. Estas consultas y búsquedas de inventario no disparan una exportación a C. Los objetivos
indirectos siguen siendo desconocidos y pueden hacer parcial la cobertura de relaciones. Las cachés de referencias
expiran al cerrar; un proceso de CLI nuevo repite el recorrido nativo de referencias.
Las referencias tipadas, CFG, las herramientas de memoria cruda y las anotaciones siguen sin soporte. Una primera
respuesta en frío puede provenir de una ejecución de una sola función (sus limitaciones lo indican); el ensamblador
espera a la exportación. Para pseudocódigo y ensamblador, `raw_result.source` nombra el
archivo `.c`/`.asm` en caché y el rango de bytes, que puedes buscar directamente en lugar de
llamar por cada función. Consulta la
[guía del proveedor Kuna](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/kuna-provider.md).

Si el usuario dice solo "mi app" sin un nombre, ruta u objetivo ya seleccionado
para esta tarea, pregunta cuál app antes de buscar artefactos. Las rutas en informes guardados
no relacionados y en fixtures de prueba cercanos no seleccionan el objetivo del usuario. Resuelve
un nombre de app real y legible a un único artefacto instalado claro cuando sea posible;
pregunta cuando las coincidencias sean ambiguas. Nunca elijas una app de ejemplo en nombre del usuario.

En una sesión sin objetivo, usa `open_binary` para vincular cualquier archivo comprimido/paquete u
objetivo nativo cuya herramienta de análisis opere sobre el objetivo activo. No llames a una
herramienta no anunciada; inspecciona `binary_session` con `{}` y su
`result.tool_availability` para conocer los motivos de disponibilidad y la remediación. Expande los
`names` de cada grupo en entradas, heredando los requisitos de cliente a nivel de inventario
a menos que el grupo los sobrescriba. En sus vocabularios cerrados de efectos y anotaciones,
las banderas listadas son verdaderas y las banderas conocidas omitidas son falsas. La unión de nombres agrupados
es el inventario completo de herramientas; usa `tools/list` para los esquemas canónicos de herramientas.
Los hechos de candidatos de proveedor describen proveedores posibles, mientras que las capacidades de sesión
de nivel superior describen la ruta actual y `analysis_provider_binding` nombra el
proveedor seleccionado. No trates esos alcances como intercambiables.
