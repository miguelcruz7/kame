# Diagnóstico aislado de vídeo Cockpit por 4G — 2026-10-20

**ID:** `F1-VIDEO-4G-20261020-01`  
**Objetivo:** recuperar imagen YOLO estable en Cockpit por 4G sin alterar el estudio paralelo de desconexiones.  
**Fecha/zona:** 2026-10-20, Europe/Madrid; preparación del worktree desde las 20:15 CEST. Las lecturas anteriores de esta conversación no tienen hora exacta conservada y no se les asigna la de esta preparación.  
**Entorno Git:** base `621a432c45de30500211aa906de82ccbda6cf549`, rama local `codex/video-cockpit-4g`, worktree independiente adjunto al chat. La carpeta original permanece en `codex/local-git-authorization-rules` con cambios previos ajenos a este diagnóstico.  
**Autorización:** inicialmente preparación aislada mientras seguía activo el estudio paralelo. Posteriormente el usuario autorizó trabajar en la carpeta principal y continuar el plan, abriendo esta intervención de vídeo. Al final solicitó omitir los 15 minutos y dejar de observar. Sin autorización para push, PR o integración.  
**Estado:** reproducción YOLO recuperada en la sesión Edge del usuario y confirmada por él. Observación detenida a petición expresa; no se acredita el ensayo de 15 minutos.

## Evidencia y fuentes

| Fuente | Resultado | Límite |
| --- | --- | --- |
| Mensaje del usuario en este chat, 2026-10-20 | Cockpit alterna indicaciones conectado/desconectado y nunca muestra vídeo; entrada mediante la extensión de BlueOS sobre ZeroTier. | No se atribuye el indicador del vehículo al vídeo. Su estudio permanece independiente. |
| Aviso literal comunicado por el usuario | All available video stream IPs are being blocked. | Falta captura y lectura de los valores efectivos de esa sesión. |
| Lecturas HTTP anteriores de este chat, antes de establecer el aislamiento | BlueOS y Cockpit HTTP 200; una fuente YOLO, `running=true`, sin error declarado; mapping `Stream 1` a YOLO y ajustes guardados `allowed-stream-ips=[]`, `enable-auto-ice-ip-fetch=false` para los usuarios consultados. | No prueban la configuración efectiva del navegador ni la recepción de imagen. No se repitieron durante esta fase aislada. |
| Lecturas anteriores RTSP y WebSocket de este chat | DESCRIBE de `/yolo` devolvió 200 y SDP H.264 con `profile-level-id=42C01F`; el puerto 6021 aceptó el handshake WebSocket con HTTP 101. | No se capturaron frames actuales ni una negociación multimedia completa. |
| Inspección de navegador anterior de este chat | La pestaña temporal no permitió obtener una interfaz utilizable y se cerró. | No reproduce ni explica el comportamiento del navegador del usuario. No se volvió a abrir durante el aislamiento. |
| Archivo local previo del estudio paralelo `local/registros/F1-COCKPIT-4G-20261020-01/inspect-1.json`, consultado sin modificar | Nombre de contenedor de Cockpit correspondiente a `v1.16.0-beta.1`. | Es evidencia previa del otro estudio, no una consulta nueva ni confirmación del código servido al navegador afectado. No se copian sus registros. |
| Análisis local del código oficial del tag `v1.16.0-beta.1` | Mecanismo de filtro, aviso y sincronización descrito debajo. | Comparación estática; no se ha cotejado el bundle instalado ni la versión/caché de la sesión afectada. |

Las respuestas anteriores están conservadas en la conversación; no se presentan como nuevos archivos crudos ni se inventan hashes para ellas. El análisis estático de esta fase se conserva en `local/registros/F1-VIDEO-4G-20261020-01/` **inicialmente en el worktree de vídeo y trasladado después a la carpeta principal**, excluido de Git: fuentes oficiales descargadas desde Internet por el PC, manifiesto de URL/hash y nota de preparación. No se usó el enlace del barco para descargar esas fuentes.

El manifiesto privado `fuentes.json` tiene SHA-256 `e530484a3cedd7c97446dcc9fe14b1374afefbcbfcb7c82027604b2ab8c81741`; `preparacion.json` registra fecha UTC, commit, aislamiento y siguiente paso. Los archivos crudos de esta fase no contienen credenciales.

## Diagnóstico estático

- En [session.ts](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/libs/webrtc/session.ts), `onIncomingICE` ignora un candidato por IP solo cuando la selección permitida no está vacía y no contiene una coincidencia. Una lista vacía no bloquea por IP. Hay un filtro independiente de protocolos que también deberá inspeccionarse.
- En [video.ts](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/stores/video.ts), la rutina del aviso se configura si la selección automática estaba habilitada al inicializar el módulo. Emite el aviso comunicado cuando existen IP disponibles y la selección no vacía no coincide con ninguna. También intenta añadir direcciones de interfaces WIRED/USB automáticamente.
- En [settingsSyncer.ts](https://github.com/bluerobotics/cockpit/blob/v1.16.0-beta.1/src/composables/settingsSyncer.ts), los ajustes comienzan con el almacenamiento del navegador; la sincronización posterior depende del usuario y vehículo. Un conflicto puede conservar el valor local y escribirlo en BlueOS. Abrir otra pestaña no constituye por sí solo una lectura pasiva.

**Conclusión:** el aviso evidencia una selección incompatible en el momento en que fue emitido, si la sesión usa esta lógica. La discrepancia con los valores leídos en BlueOS es compatible con ajustes locales antiguos, inicialización anterior a la sincronización, otro usuario o código/caché distintos. Son hipótesis; falta identificar la situación efectiva. No se concluye que el enlace 4G esté saturado ni que el filtro sea el único fallo.

## Cambios y comprobaciones de esta fase

- Creado y adjuntado un worktree desde el commit acordado; creada únicamente allí la rama `codex/video-cockpit-4g`.
- Añadido el procedimiento selectivo en la [guía de vídeo](../../software/video/README.md#diagnóstico-de-ip-de-vídeo-bloqueadas), este registro y sus referencias en estado e índice.
- Sin cambios de detector, encoder, servicios, IP, perfiles, usuario, selección ICE, telemetría ni otros ajustes del vehículo. Valores antes/después en el barco: no modificados durante esta fase; no se ha tomado aún el respaldo de la futura intervención.
- No se abrieron streams, pestañas de Cockpit, sesiones RTSP/WebRTC ni pruebas de caudal en esta fase. No se leyó ni duplicó ninguna credencial.
- `python3 .github/checks/check_repository.py` no pudo arrancar porque el alias de Windows remite a Microsoft Store. Se ejecutó con `python .github/checks/check_repository.py`: **correcto**, 56 archivos, 145 enlaces/anclas, sintaxis/configuración y patrones de secretos; generación de misiones y pruebas locales del visor correctas, sin consultar el vehículo. No se ejecutó SITL porque no cambia navegación ni su arranque.
- `git diff --check`: **correcto**. Revisado el alcance de los documentos y los valores incluidos: solo diagnóstico de vídeo, sin secretos ni cambios operativos. Estas comprobaciones no sustituyen validación del barco.

## Traslado a la carpeta principal — 20:44 CEST

El usuario autoriza trabajar en la rama normal. Se trasladan los cuatro documentos de vídeo a la carpeta principal, rama `codex/local-git-authorization-rules`, conservando sus modificaciones anteriores y el diagnóstico independiente de desconexiones. No se cambia de rama, se integra en `main`, se hace push ni se abre PR. El worktree de vídeo se conserva como respaldo de la preparación inicial.

Las fuentes privadas de este diagnóstico se copian a `local/registros/F1-VIDEO-4G-20261020-01/` de la carpeta principal, comprobando SHA-256 de cada archivo. El manifiesto `traslado.json` y las copias de los documentos afectados previas al traslado permiten revisar o revertir solo estas inserciones. No se duplican credenciales ni archivos del estudio de conectividad.

Este traslado no modifica Cockpit, red o servicios ni añade una lectura del barco. La autorización cambia la ubicación de trabajo; no acredita que el estudio paralelo haya terminado ni abre una ventana de reproducción.

Comprobaciones en la carpeta principal: `python .github/checks/check_repository.py` correcto (59 archivos, 156 enlaces/anclas, sintaxis, patrones de secretos, misiones y visor); `git diff --check` correcto. Se verificaron los hashes de los seis archivos privados copiados y de siete archivos ajenos conservados sin modificación. La advertencia de Git sobre CRLF en AGENTS pertenece al cambio local previo; no se editó ese archivo.

## Corrección y resultado — 20:46–21:01 CEST

- En la pestaña real de Edge, usuario `jloureda`, perfil **Boat default / Map view**, Settings → Video mostraba IP permitida `192.168.10.2` y selección automática activada. Difería de BlueOS, que guardaba `[]` y selección automática desactivada. Se respaldaron los ajustes de BlueOS y se capturó la configuración local antes del cambio.
- Se desactivó la selección automática y se sustituyó la IP local permitida por `10.133.182.55`, presente entre los candidatos anunciados. Se recargó una vez la pestaña. No se modificaron perfiles, mapping, protocolos, encoder, servicios, red ni telemetría. El mapping local conserva un segundo widget de la cámara original, sin reproducción; su estado de espera no pertenece al YOLO recuperado.
- Tras recargar apareció imagen YOLO 960×540. Las observaciones del reproductor devolvieron `readyState=4`, reproducción activa y sin error; el tiempo multimedia avanzó de ~124,8 a ~388,4 s entre observaciones. Son muestras, no una medición continua de congelaciones. El usuario confirmó que parecía funcionar bien y pidió detener la observación.
- La Pi salía por `eth1`; Ethernet no tenía portadora. Lectura inicial de heartbeat desarmado y estado final de interfaz desarmado. Los tres servicios de vídeo figuraban activos, `NRestarts=0`, 58,7 °C y `get_throttled=0x0`. La decodificación local obtuvo cinco frames YOLO 960×540. También se comprobó que el RTSP interno respondía tanto por loopback como por `192.168.2.2`: no se cambió el Redirect.
- Hubo intentos de diagnóstico SSH con timeout y una conexión interrumpida; no acreditan por sí solos otra causa. El gestor registró avisos de posición de pipeline sin avanzar. Al recuperarse imagen sin intervención del servidor, no se hicieron cambios por esos avisos. La herramienta bloqueó la apertura de la página interna de estadísticas del navegador; no se intentó eludir esa restricción.
- La lectura final de BlueOS seguía mostrando IP permitidas `[]` y selección automática desactivada: la corrección demostrada se conserva en el navegador afectado tras su recarga, no se declara instalada en otros navegadores. No se midió latencia física ni se completaron tres reaperturas o la comprobación Wi-Fi.

**Causa operativa identificada:** selección de ruta de vídeo del navegador incompatible con el acceso remoto usado. La selección explícita de ZeroTier y la recarga recuperaron YOLO sin cambiar el bitrate ni reiniciar servicios. Esto no resuelve ni modifica el diagnóstico independiente de desconexiones del vehículo.

**Evidencia privada:** `local/registros/F1-VIDEO-4G-20261020-01/ventana-20261020T184618Z/`, con captura anterior, imagen recuperada/final, configuración de BlueOS antes/después, lecturas de servicios/ruta/RTSP y nota de cambios del navegador. `evidence-sha256.json` contiene hashes de 30 archivos; las mediciones anteriores permanecen con su origen. Los intentos fallidos no se presentan como comprobaciones superadas.

**Reversión:** en el navegador del usuario, restaurar IP permitida `192.168.10.2` y selección automática activada desde la captura anterior, solo si se decide deshacer esta corrección; eso restablecería la configuración que impedía el acceso usado. No restaurar perfiles completos ni respaldos históricos. No hay cambios de servicios o encoder que revertir.

**Cierre solicitado por el usuario:** se detuvo la observación y se omite expresamente el ensayo de 15 minutos. Se entrega recuperación funcional confirmada, sin afirmar estabilidad prolongada ni validación Wi-Fi. No se programan pruebas ni seguimiento automático.
