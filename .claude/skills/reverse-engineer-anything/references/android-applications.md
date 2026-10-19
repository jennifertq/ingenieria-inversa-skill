# Artefactos de aplicaciones Android

Usa las herramientas de Android que anuncia el servidor conectado. La rama
principal del repositorio y npm 4.1.0 incluyen esta familia. Instalar solo la
skill no puede agregarla a un servidor más antiguo.

Empieza con `inspect_android_package` sobre la ruta del APK de quien llama para
obtener la identidad del paquete, las declaraciones del manifiesto, la cobertura y
la Evidence inline. Usa `search_android_classes` para encontrar candidatos,
`inspect_android_class` para los miembros de una clase, `inspect_android_method`
para la descompilación y `trace_android_references` para las referencias estáticas
entrantes. Cada llamada recibe su propia ruta de APK y selectores explícitos; no
abras primero una sesión nativa.
Elige un `overload_index` del inventario de la clase cuando los métodos sean
ambiguos en lugar de adivinar.

El proveedor requiere un JAR de JADX MCP headless 0.7.1 suministrado por separado
y Java 17 o posterior. `REA_JADX_MCP_JAR` selecciona la ruta absoluta del JAR; `JAVA_HOME`
puede seleccionar Java. La configuración de REA no instala ni configura ese JAR, y
los alcances de proveedor de doctor cubren Hopper/Ghidra, no JADX. Usa las
herramientas existentes e informa los prerrequisitos faltantes específicamente
para la tarea de Android.

Linux y macOS usan el límite de proceso propio POSIX. Windows x64 requiere los
controles nativos incluidos correspondientes y usa un Job Object propio con stdio
bidireccional. Se requiere un JDK completo, incluido `jdk.compiler`, en todos los
hosts; en Windows, `JAVA_HOME` selecciona `bin\java.exe`. Consulta la guía de
Android para conocer la cobertura real de verificación por host. Las llamadas usan
un worker y plazos del proveedor; el opcional
`REA_JADX_HEAP_MIB` selecciona el heap de la JVM y `REA_JADX_OPERATION_TIMEOUT_MS`
el plazo por operación (predeterminado 120000 ms; el timeout de herramientas del
cliente MCP también debe permitirlo). El APK nunca se ejecuta
y no se requiere un emulador.

Las entradas del manifiesto y el texto descompilado son observaciones estáticas,
no ejecución ni aplicación de políticas. Las referencias entrantes son relaciones
estáticas recuperadas; la reflexión, la carga dinámica y las llamadas no resueltas
siguen siendo desconocidas. Conserva los digests de artefactos, las ubicaciones,
los diagnósticos y la cobertura incompleta. Para miembros de archivos comprimidos
en lugar de análisis de código, usa `open_binary` e `inspect_artifact`.
