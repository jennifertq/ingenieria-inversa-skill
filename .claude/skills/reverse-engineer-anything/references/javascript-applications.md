# Artefactos de aplicaciones JavaScript y Electron

Para JavaScript capturado o empaquetado que requiera recuperar código fuente legible, use
`recover_javascript_sources` con un `path` absoluto y sin
`output_directory`. Proporcione los archivos runtime/compartidos/lazy relacionados en
`additional_paths` cuando se anuncie, y luego analice juntos el directorio `analysis_input`
devuelto. Cada entrada conserva su propia instantánea, digest y procedencia por
rango de bytes; las entradas y el código recuperado nunca se ejecutan. La recuperación requiere un
Wakaru proporcionado por quien llama en Linux x64; consulte [la guía de recuperación](https://github.com/morluto/rea/blob/rea-agents-6.7.0/docs/javascript-recovery.md).

Use `analyze_javascript_application` directamente sobre el ASAR o el árbol
extraído que proporcione el operador. Cuando la pregunta se refiera a rutas de código fuente conocidas y el
esquema conectado anuncie `source_paths`, seleccione rutas exactas inventariadas como
`["package.json", "main.js", "preload.js"]`. Incluya explícitamente los manifiestos o
source maps de soporte; las dependencias no se analizan implícitamente. REA conserva
el inventario completo y la identidad del artefacto, pero lee el texto fuente y analiza
solo los archivos seleccionados. El resultado y el resumen registran `source_selection`; los archivos
fuera del alcance y sus relaciones permanecen desconocidos, por lo que una cobertura parcial de la
aplicación no significa que el código fuente seleccionado haya fallado. Use `--source-path` repetido
en cualquiera de las rutas CLI estáticas de aplicación. Omita la selección cuando la pregunta
requiera un análisis completo de la aplicación. `detail: "summary"` reduce la entrega
y por sí solo no reduce el trabajo de análisis.

Los especificadores `#alias` exactos se resuelven mediante el mapa `imports` del paquete
que contiene al importador, hacia archivos locales del paquete; los paquetes `node_modules`
anidados usan su propio mapa. Los destinos de importación con comodines, recursivos y de paquetes externos
quedan sin resolver con esa limitación. Cuando el tamaño sea desconocido o grande y el esquema conectado anuncie
`detail`, solicite `detail: "summary"`. Esto devuelve un registro Evidence de `inspect_analysis_view`
con un ID distinto y un `normalized_result.parent_evidence_id`
para el análisis completo y conservado de la aplicación. El contenido de los source maps forma parte de
ese análisis estático. Lea hallazgos, cobertura, limitaciones y desconocidos, y luego
siga una pregunta específica sin responder. Los servidores antiguos sin `detail` devuelven
el Evidence completo de la aplicación en línea cuando cabe.

Cuando el esquema conectado anuncie `max_heap_mb` y `analysis_timeout_ms`,
estos seleccionan el heap old-space del analizador de código fuente aislado y el plazo
por archivo fuente. Los valores predeterminados son 1024 MiB y 300000 ms. No cambian el heap del proceso
MCP. Un REA alojado en Bun no aplica la elección de heap; en Windows, en cambio,
limita la memoria comprometida del analizador a esa elección más una reserva de runtime
de 512 MiB.
Los análisis limitados por recursos conservan los hechos estáticos completados e
informan cobertura semántica parcial con alcances desconocidos específicos; esto no
significa que el código fuente esté mal formado. Inspeccione esos límites antes de reintentar un archivo fuente.
Cuando las relaciones expandidas excedan la memoria disponible del padre, inspeccione la
vista de ítem de módulos del archivo para obtener `static_analysis` y
`semantic_module_analysis` conservados. Sus hechos siguen disponibles aunque los enlaces del grafo
sean desconocidos. El agotamiento acumulado de resultados puede detener el análisis antes de examinar cada archivo;
el inventario y los alcances desconocidos restantes distinguen ese caso.
Un timeout o una cancelación después de iniciado el análisis del código fuente conserva Evidence parcial
en la misma sesión. Una referencia `error.details.partial_observation` devuelta
puede pasarse directamente a `inspect_analysis_view`. Si el SDK cancela localmente, recupere su ID registrado desde
el bundle de Evidence antes de inspeccionar el análisis parcial.

## Leer un módulo sin repetir el análisis

Use el ID padre realmente devuelto, en la misma conexión, como `source.evidence_id`.
Los siguientes IDs son marcadores de posición que deben reemplazarse por los valores devueltos. Cuando el
ID de nodo del módulo aún no se conozca, pagine las identidades antes de seleccionar un ítem.
Las páginas devuelven solo IDs de nodo, rutas y roles; elija un tamaño de página útil y siga
`coverage.next_offset` cuando otra página sea relevante:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "ev_ACTUAL_PARENT_ID"
  },
  "view": { "kind": "page", "collection": "modules", "offset": 0, "limit": 16 }
}
```

Seleccione la entrada de página relevante por su `node_id` exacto y su rol registrado:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "ev_ACTUAL_PARENT_ID"
  },
  "view": {
    "kind": "item",
    "collection": "modules",
    "selector": { "node_id": "jag_node_ACTUAL_NODE_ID" }
  }
}
```

Las páginas de módulos incluyen roles de módulo asset, bundled y source, por lo que una ruta puede
identificar varias entradas. Use `selector.path` solo cuando se haya establecido la unicidad;
el ID de nodo devuelto evita necesitar un inventario completo para probar la unicidad. Ante ambigüedad,
seleccione el ID de nodo coincidente de la página o de los candidatos del error. Siga
`next_offset` cuando otra página sea relevante. Un ítem expone las observaciones registradas
de ese nodo de módulo, su identidad, hashes, exports y rangos de código fuente; no
incluye cada observación sintáctica hija, arista relacionada ni el archivo fuente original.
La ausencia de un hecho en el ítem no es evidencia de ausencia en toda la aplicación.

Para identidades canónicas y conteos de rangos de código fuente conservados, use una página
tipada de referencias en lugar de leer cada ítem completo:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "ev_ACTUAL_PARENT_ID"
  },
  "view": {
    "kind": "javascript",
    "collection": "modules",
    "projection": "references",
    "where": { "path": "main.js", "kind": "javascript-module" },
    "offset": 0,
    "limit": 16
  }
}
```

Los filtros coinciden con cadenas conservadas exactas; omita un filtro para incluir todos los valores, use
`path: null` para rutas no disponibles y `path: ""` para una ruta vacía registrada.
Las filas conservan la `identity` canónica y los estados de soporte de observación distintos en
`basis`. `retained_source_range_count` cuenta observaciones de rangos de código fuente conservadas,
no imports en runtime ni sitios de referencia únicos. Use el `node_id` de una fila con la vista
de ítem anterior para obtener ubicaciones exactas y las observaciones de soporte completas. Siga
`coverage.next_offset`; el agotamiento de páginas describe solo las filas conservadas coincidentes.
Revise `source_coverage` para la selección de código fuente, la cobertura parcial/desconocida del grafo y
los conteos de desconocidos antes de sacar una conclusión negativa.

## Rastrear solo la pregunta restante

Use `trace_application_feature` sobre el Evidence padre de la aplicación para un único
ID de nodo literal, ruta, cadena, API, canal IPC, módulo o export nativo.
Seleccione `incoming` para relaciones que llegan a la semilla, `outgoing` para las que
salen de ella y `both` cuando la pregunta necesite ambas. El recorrido del rastreo incluye
relaciones de contención, por lo que incluso una semilla acotada puede expandir muchos nodos; un
rastreo bidireccional puede alcanzar módulos hermanos no relacionados. Es preferible un ítem o página
de módulo cuando sus observaciones ya responden la pregunta. No trate
todos los nodos alcanzados como participantes de la funcionalidad.

Reutilice el Evidence padre conservado cuando el servidor lo anuncie, o proporcione el Evidence completo
en línea. Incluya Evidence de Hopper o Ghidra solo cuando el digest de su artefacto
coincida exactamente.

## Recuperar una visualización sobredimensionada

Una respuesta sobredimensionada informa `resource_constraint` y
`details.resource: "transport"`. Reutilice
`details.reported_limits.evidence_reference` con `inspect_analysis_view` para obtener un
resumen, un módulo o una página estable de identidades de módulos.
`export_evidence_bundle` escribe la sesión canónica completa en un
archivo elegido por quien llama. Estos flujos conservan el Evidence original y la cobertura;
un seguimiento amplio también puede exceder el framing.

Un cliente puede truncar un resultado exitoso dentro de su envoltorio de texto sin un
`resource_constraint` de REA. Trate un aviso de truncamiento o un JSON incompleto como una
limitación de visualización; no afirme que se examinó el registro completo. Reutilice el ID
padre conocido para vistas más pequeñas, o exporte el Evidence completo a un archivo seleccionado
mientras la sesión siga abierta. Si el ID padre se perdió de la vista previa,
use el resumen del análisis previo o entradas explícitas del registro (ledger) para recuperarlo; no
invente un ID ni vuelva a ejecutar el análisis solo para reproducir la misma visualización.

Las preferencias de BrowserWindow, las superficies de preload y contextBridge, los registros
IPC, los utility processes y las solicitudes de bindings nativos son observaciones sintácticas
estáticas. Solo una coincidencia única de canal IPC literal exacto respalda un emparejamiento
inferido. Los canales dinámicos o ambiguos permanecen sin resolver. Un miembro `.node`
solicitado no es un export nativo verificado. Nunca afirme alcanzabilidad en runtime,
registro, valores predeterminados ni aplicación de políticas a partir del análisis estático.

Para comparar versiones, analice cada versión una vez y luego llame a
`compare_application_versions`. Acepte solo sus coincidencias por digest, source map, huella
estructural o semánticas no de módulo. Los ordinales de módulo y los nombres minificados
no son una identidad persistente. Informe agregado o eliminado solo con cobertura completa
del lado opuesto; de lo contrario, informe desconocido.

Cuando la pregunta sea cómo cambió la forma del objeto devuelto por un callable exportado exacto,
analice cada versión una vez y luego llame a
`compare_javascript_export_shapes` con rutas de módulo y nombres de export explícitos.
Use los IDs devueltos en la misma conexión, o registros Evidence completos en línea,
de ambas llamadas de análisis. Acepte el emparejamiento de variantes
solo mediante el discriminante literal exacto y único de la herramienta. Lea
`property_inventories` y la `presence` de cada cambio antes de tratar `unknown` como
"el nombre no fue observado": los inventarios listan los nombres de propiedades observados aun cuando
los valores siguen desconocidos, con un `source_range` para cada variante emparejada o no emparejada.
Los huecos de arreglos y las posiciones invalidadas por mutación no son propiedades observadas.
Una cobertura completa del padre informa `added`/`removed` solo de presencia
independientemente de los valores no resueltos. Cite el
Evidence de la comparación e informe los cambios como JSON Pointer; los valores dinámicos, las variantes
ambiguas y la cobertura incompleta de propiedades del padre permanecen desconocidos. Esto es inferencia
estática, no comportamiento en runtime. Cuando se necesite la semántica en runtime, ejecute
sondas de comportamiento contra las versiones relevantes de la aplicación y captúrelas
mediante los flujos de navegador, Electron o proceso disponibles.

## Reutilizar Evidence de aplicaciones

Cuando el servidor conectado lo anuncie, las herramientas de rastreo y comparación de aplicaciones
aceptan Evidence completo en línea o
`{"kind":"retained-evidence","evidence_id":"ev_<64 lowercase hex characters>"}`
para su entrada de aplicación (`application`, o `left`/`right`). `inspect_analysis_view`
usa la misma forma de referencia conservada en `source`, o Evidence portable en línea,
para proyectar un resumen, una página de módulos o un módulo con sus observaciones registradas.
Esta notación es
una plantilla: reemplácela por el ID realmente devuelto. Las versiones anteriores a 4.1.0 aceptan solo Evidence
completo en línea. Use el ID exacto
devuelto por el productor en la misma conexión MCP. La resolución no ejecuta
análisis ni selecciona un proveedor; los hallazgos permanecen en línea. Los arreglos de observaciones
nativas siguen requiriendo Evidence completo. `close_binary` borra las referencias conservadas;
exporte un bundle antes de cerrar, o proporcione Evidence portable en línea en otra
conexión. Una referencia faltante incluye su ID y orientación para recuperarla.

Para metadatos exactos de archivos/nativos o brechas de procesamiento, use
`view: {kind: "javascript-facts", where: {paths: ["package.json"]}, property_keys: ["name", "operation", "analysis_status"], limit: 32}`.
Las filas conservan la identidad canónica de nodo/observación y el Evidence original. Las rutas
coinciden con las ubicaciones artifact-path/source-range del Evidence; las propiedades faltantes se siguen
omitiendo y la cobertura de código fuente se mantiene separada del agotamiento de páginas. Agrupe rutas y
seleccione solo las claves de propiedad necesarias; el Evidence completo sigue accesible mediante exportación.
Si los nombres son desconocidos, active `include_available_property_keys: true`; lista
las claves originales por cada observación devuelta sin los valores no seleccionados. Mantenga emparejada la
identidad de nodo/observación de cada fila al componer hechos.
Estas filas seleccionan observaciones del grafo de la aplicación; las relaciones semánticas y
los registros semánticos de desconocidos permanecen en el Evidence padre completo y en las herramientas de rastreo.
