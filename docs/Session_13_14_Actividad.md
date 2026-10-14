# Sesiones 13–14 — Pausa para revisar el estado de nuestro proyecto

**Duración: 60 minutos · Trabajo en equipo · Proyectos P01, P02 y P03.**

Hoy leerán su propio proyecto, conversarán sobre su estado y decidirán qué conviene corregir después. **No se pide programar, crear diagramas nuevos, instalar herramientas ni configurar otro workflow durante esta actividad.**

El objetivo es responder: **¿nuestros requisitos, modelos, diseño y código cuentan la misma historia? ¿Qué está bien y qué necesita cambiar?**

## 1. Abran lo que ya tienen

En su repositorio, revisen:

- `docs/sesion-06-requisitos.md`: reglas, acuerdos y pendientes.
- `docs/sesion-07-modelos.md`: historia, caso de uso, éxito y rechazo.
- `docs/sesion-08-09-plan.md`: tareas, riesgos y estado del incremento.
- `docs/sesion-12-arquitectura.md`: responsabilidades, interfaces y decisiones.
- Código, modelos de datos/clases, diagramas, tests, README y última evidencia de CI disponibles.

Si un archivo no existe, anoten la ausencia y su efecto. Revisen el repositorio del equipo y su versión actual; un ejemplo resuelto sirve como apoyo, pero no acredita automáticamente el avance de su proyecto.

## 2. Cómo trabajaremos

| Minutos | Trabajo |
|---|---|
| 0–10 | Leer esta guía y abrir las evidencias anteriores. |
| 10–35 | Revisar los diez puntos de la tabla con archivos concretos. |
| 35–45 | Recorrer sobre el código una operación importante y su rechazo/repetición. |
| 45–55 | Acordar hasta tres correcciones prioritarias y lo que conviene conservar. |
| 55–60 | Guardar la revisión breve y compartir su enlace. |

Cada integrante debe explicar una parte del proyecto. Hoy la revisión es interna al equipo; no necesitan intercambiar documentos con otro grupo.

## 3. Marquen el estado real

Para cada punto registren un estado, una evidencia y un hallazgo breve:

| Estado | Significado |
|---|---|
| **C — Conforme** | Lo esperado en esta etapa está respaldado por evidencia coherente. Indiquen si está documentado, implementado o probado. |
| **P — Parcial** | Existe una parte, pero falta completar otra. Especifiquen cuál. |
| **R — Revisar** | Hay una contradicción, un defecto o un elemento esperado que falta. |
| **NV — No verificado** | Existe una afirmación, pero todavía no pueden respaldarla. |
| **F — Futuro** | Trabajo posterior según el plan acordado; indiquen cuándo se abordará. No usen F para ocultar una corrección actual. |

**Evidencia concreta:** archivo y sección, función/clase, test, commit o ejecución existente. «Lo tenemos» o «seguro funciona» no bastan. No hace falta ejecutar tests nuevos: lean los resultados disponibles y reconozcan sus límites.

## 4. ¿Estamos alineados con lo trabajado?

| # | Punto a revisar | Pregunta para comparar con su proyecto |
|---|---|---|
| 1 | **Requisitos — sesión 6** | ¿Las reglas tienen IDs y resultados comprobables? ¿Distinguen acuerdos de suposiciones? ¿El código usa la política que el cliente aprobó? |
| 2 | **Flujo — sesión 7** | ¿Actor, objetivo, recorrido aceptado y rechazo/repetición corresponden a la misma operación? ¿Queda claro qué cambia y qué se conserva? |
| 3 | **Plan — sesiones 8–9** | ¿Las tareas marcadas terminadas tienen evidencia? ¿Los riesgos y pendientes siguen vigentes? ¿El siguiente paso responde a una necesidad real? |
| 4 | **Responsabilidades — sesión 12** | ¿Pueden localizar interacción, reglas y acceso a datos? ¿Una regla está duplicada en distintos lugares? ¿El diagrama describe el código o señala claramente una propuesta? |
| 5 | **Estilo arquitectónico — sesión 13** | ¿Pueden explicar cómo se organiza el sistema y por qué? Revisen las dependencias y un compromiso de su elección. Capas lógicas no significa tres computadoras; no tienen que aplicar todos los estilos ni MVC. |
| 6 | **Entidades y datos — sesiones 13–14** | ¿Identifican entidades, IDs, estados y relaciones? ¿El diseño de datos/esquema que tengan coincide con esas reglas? Distingan diseño propuesto de persistencia implementada. |
| 7 | **Clases y relaciones — sesión 14** | ¿Las clases o candidatas tienen un propósito claro? ¿Las asociaciones y multiplicidades son correctas? Si hay herencia, ¿expresa una especialización o se está usando solo para conectar elementos? |
| 8 | **Interfaz y secuencia — sesiones 12–14** | ¿Los mensajes del modelo tienen una operación receptora con entradas/salidas compatibles? ¿Quién consulta, decide y guarda? ¿El rechazo llega antes de los cambios que deben evitarse? |
| 9 | **Pruebas y CI existentes** | ¿Los tests invocan la operación y comprueban datos además de respuestas? ¿La evidencia corresponde a una versión identificada? Un YAML sin ejecución no demuestra que CI esté funcionando. |
| 10 | **Documentación y comprensión** | ¿README permite entender cómo ejecutar lo que existe? ¿La decisión explica objetivos, alternativas y compromisos? ¿Todos pueden explicar una contribución y un límite del proyecto? |

Si usan funciones y diccionarios, revisen también sus responsabilidades y relaciones. Las clases candidatas pueden estar documentadas como propuestas: no necesitan convertir hoy todas las funciones en clases ni introducir herencia para completar la revisión.

Si falta un diagrama de clases/secuencia o un diseño de datos previsto para estas sesiones, regístrenlo como pendiente con su propósito. **No lo construyan hoy.** La integración completa con MySQL/MariaDB, una interfaz final y el despliegue se revisan según sus etapas posteriores; no se presentan como terminados solo porque exista un dibujo o una prueba en memoria.

## 5. Revisen un caso crítico de su proyecto

Elijan una fila y recorran el caso leyendo requisito, modelo, función y test disponible. No necesitan modificar ni volver a implementar el sistema.

| Proyecto | Caso y preguntas importantes |
|---|---|
| **P01 — Equipos** | Un préstamo ya devuelto recibe otra devolución. ¿Dónde se reconoce que está cerrado? ¿Se conserva la devolución y el estado del equipo? Si usan préstamo/equipo/persona como entidades, ¿distinguen historial de préstamos de la restricción de un único préstamo activo por equipo? |
| **P02 — Reservas** | R1 ocupa 09:00–10:00 y R2 10:00–11:00 en la misma sala. Se propone R1 a 10:30–11:30, cumpliendo las demás condiciones acordadas. ¿Dónde se detecta el conflicto y se conservan ambas reservas? Una sala puede tener muchas reservas históricas: eso no permite horarios activos incompatibles. |
| **P03 — Talleres** | En un taller de cupo 2, P-01 y P-02 están confirmados. P-02 repite y después P-03 solicita plaza. ¿Se conserva la inscripción existente? ¿P-03 obtiene la espera/rechazo acordado? ¿Siguen exactamente dos confirmados? Distingan número de registros históricos/en espera de plazas ocupadas. |

Busquen **una correspondencia correcta o una discrepancia real**. Por ejemplo: «El modelo indica consultar el duplicado antes del cupo, pero la función hace lo contrario». Si no encuentran una discrepancia, documenten por qué el caso revisado es coherente; no inventen un defecto.

## 6. Qué cambiaremos después

Elijan **hasta tres prioridades**, usando este orden como ayuda:

1. **Alta:** incumple una regla aprobada, altera datos indebidamente o impide comprobar el flujo.
2. **Media:** responsabilidades mezcladas, contratos/modelos desactualizados o documentación que dificulta continuar.
3. **Baja:** mejora de nombres, presentación o simplificación que no cambia el comportamiento.

Para cada corrección indiquen **problema, cambio concreto, evidencia de que quedó resuelto y responsable**. «Mejorar el código» no define una acción. «Separar la regla de duplicado del menú y conservar el test del estado completo» sí.

Registrar una corrección no significa ejecutarla hoy. Conserven las partes que funcionan; la revisión no obliga a rehacer el proyecto. Si todo está conforme, expliquen la evidencia y el siguiente trabajo del plan.

## 7. Entrega breve: una revisión, no otra implementación

Creen **`docs/sesion-13-14-revision.md`** en su repositorio. Escriban solo estos cuatro apartados:

**1. Proyecto y versión revisada:** integrantes, fecha real, operación, rama/commit y enlaces a las evidencias anteriores.

**2. Diagnóstico:** completen una fila por cada punto de la sección 4.

| Punto # | Estado | Evidencia concreta | Hallazgo: qué está bien o qué falta |
|---|---|---|---|
| 1 — Requisitos | P | `docs/sesion-06-requisitos.md` (`RES-RF-01` a `RES-RF-07`, `RES-RC-01`); `reservas/services.py` | Las reglas tienen ID, criterio de aceptación y separan lo aprobado de lo pendiente, y el código usa 15 min, matrícula al día y una reserva por bloque. Falta `RES-RF-04` (capacidad): está aprobada, pero `Sala` no tiene capacidad ni `Reserva` asistentes (`reservas/models.py`). |
| 2 — Flujo | C | `docs/sesion-07-modelos.md` (`RES-CU-01`, E1, E2, §4 estados); `api_modificar_reserva` en `reservas/views.py`; `tests/test_modificar_reserva.py` | Actor, objetivo, éxito, rechazo y qué se conserva coinciden con el código y están probados. Documentado, implementado y probado. |
| 3 — Plan | R | `docs/sesion-08-09-plan.md` §7 («No iniciada» en A–D); README «Qué hace hoy»; commits `85f7d67` y `fd4212a` | El plan dice que ninguna tarea se inició, pero backend, pruebas y pantalla ya están hechos. Faltan horas reales y el estado actualizado con evidencia. El riesgo de la regla de 10 minutos sigue vigente (pregunta P1 del README). |
| 4 — Responsabilidades | R | `reservas/views.py` (interacción), `reservas/services.py` (reglas), `reservas/models.py` (datos), `proyecto/clases/` | Se localizan las tres responsabilidades, pero las reglas de crear están en `proyecto/clases/` y las de modificar en `services.py`; el desalojo de 15 min aparece en `Reserva.choca_con`, `hay_choque_con_buffer` y dos constantes distintas. No existe `sesion-12-arquitectura.md`. |
| 5 — Estilo arquitectónico | P | README «Arquitectura» (diagrama FE → MW → DB y tabla de capas con su ubicación en el código) | Se explica cómo se organiza y dónde está cada capa. Faltan las alternativas consideradas y el compromiso de la elección (por ejemplo, qué cuesta mantener dos capas de reglas). |
| 6 — Entidades y datos | P | `reservas/models.py` (`Estudiante`, `Sala`, `Reserva`; estados `CONFIRMADA`/`CANCELADA`); migraciones `0001` y `0002`; README (MongoDB aprobado el 07/10/2026) | Entidades, IDs, estados y relaciones están implementados en MongoDB. Faltan capacidad y asistentes. La restricción «sin reservas activas incompatibles» solo existe en el código (`_verificar_disponibilidad_sala` filtra `CONFIRMADA`), no como restricción de datos. No hay un documento de diseño de datos. |
| 7 — Clases y relaciones | P | `reservas/models.py` (`Reserva` → `Estudiante` y `Sala`, ambas `ForeignKey`, 1 a muchos); `proyecto/clases/` (`Estudiante`, `Sala`, `Reserva`, `SistemaReservas`) | Las asociaciones y multiplicidades de los modelos son correctas y no hay herencia. Las clases «livianas» de `proyecto/clases/` repiten los nombres de los modelos y confunden. Pendiente: diagrama de clases (propósito: mostrar Estudiante–Reserva–Sala y multiplicidades). |
| 8 — Interfaz y secuencia | R | `api_modificar_reserva` (`reservas/views.py`) y `modificar_reserva_si_esta_disponible` (`reservas/services.py`); tabla de la API en el README | El contrato de la API está documentado y probado, y el rechazo llega antes de guardar (los valores nuevos se asignan al final). Pero la vista evalúa la ventana de anticipación **antes** que «ya comenzó», contra el orden del modelo (ver sección 3). Pendiente: diagrama de secuencia (propósito: mostrar quién consulta, decide y guarda). |
| 9 — Pruebas y CI | P | `tests/test_modificar_reserva.py` (`test_rechazo_por_desalojo_conserva_la_reserva_original` lee lo guardado en la base); `docs/TRAZABILIDAD_PRUEBAS.md`; ejecución de esta revisión | Las pruebas invocan la operación y comprueban los datos, no solo la respuesta. No hay corrida completa registrada con su commit, y el workflow de CI no existe. La trazabilidad admite que falta probar «No»/Esc, capacidad y simultaneidad. |
| 10 — Documentación y comprensión | P | `README.md`; `docs/BRECHA_REQUISITOS.md`, `docs/AUTENTICACION.md`, `docs/CONFIGURACION_DJANGO.md`; `restricciones.md` | El README permite instalar, ejecutar y probar, y la bitácora registra la respuesta del docente con fecha. Pero tres documentos describen una versión anterior, la tabla de roles del README contradice al plan 8–9 y `restricciones.md` es una nota interna con una credencial de desarrollo en un repositorio público. |

**3. Caso crítico:** requisito relacionado, recorrido revisado, resultado esperado y correspondencia/discrepancia encontrada. Añadan **dos fortalezas concretas** que conviene conservar.

**4. Correcciones prioritarias:** hasta tres filas y una conclusión breve sobre el estado del incremento: puede continuar, necesita correcciones o está bloqueado; expliquen la razón.

| Prioridad | Problema | Cambio posterior | Cómo comprobaremos la corrección | Responsable / tarea del plan |
|---|---|---|---|---|
| Alta | La ventana de anticipación se evalúa antes que «ya comenzó»; una reserva iniciada puede terminar cancelada tras un rechazo por fecha. | En `api_modificar_reserva`, comprobar «ya comenzó» antes de la ventana (por ejemplo, exponiendo `_verificar_no_ha_comenzado`) y dejar de preguntar «¿Deseas mantenerla?» en ese caso. | Nueva prueba en `tests/test_modificar_reserva.py`: reserva iniciada + fecha fuera de ventana → rechazo con `preguntar_mantener: false` y reserva sin cambios. | Raúl; seguimiento de `RES-RF-06` (sin issue) |
| Media | Reglas de crear (`proyecto/clases/`) y de modificar (`services.py`) duplicadas; el desalojo de 15 min está en tres lugares. | Hacer que `api_reservar` use `services.reservar_si_esta_disponible` conservando el JSON de respuesta, y dejar una sola definición del margen de 15 min. | La suite completa pasa con MongoDB sobre un commit identificado y `reservas/views.py` ya no importa `proyecto.clases.sistema_reservas`. | Hugo; pendiente «Unificar `services.py` y `proyecto/clases/`» del README |
| Media | Documentación desactualizada: plan 8–9 con tareas «No iniciada», roles del README contradictorios, tres documentos de una versión anterior y `restricciones.md` con credencial de desarrollo. | Actualizar el estado del plan con evidencia, acordar y corregir la tabla de roles, actualizar o marcar como históricos `BRECHA_REQUISITOS.md`, `AUTENTICACION.md` y `CONFIGURACION_DJANGO.md`, y retirar o reescribir `restricciones.md`. | README, plan y roles coinciden entre sí; ningún archivo del repositorio trae credenciales; el plan cita el commit y la corrida de pruebas. | Raúl y Hugo; pendiente «Actualizar `docs/BRECHA_REQUISITOS.md`…» del README |

Guarden, hagan commit/push **de esta revisión** y compartan el enlace directo. Hoy no se exige crear issues nuevos, corregir código, producir diagramas ni obtener otra ejecución verde de CI.

## Consulta puntual, si la necesitan

- [Presentación combinada 13–14](output/Session_13_14_Styles_and_Object_Design_Final.pptx): estilos/capas, 2–9; clases/relaciones/interfaces, 10–16; secuencia/coherencia/documentación, 17–20.
- Guías anteriores: [sesión 6](../Session_06/Session_06_Actividad.md), [sesión 7](../Session_07/Session_07_Actividad.md), [sesiones 8–9](../Session_08_09/Session_08_09_Actividad.md) y [sesión 12](../Session_12/Session_12_Actividad_Breve.md).

**Resultado de hoy:** una descripción honesta del estado del proyecto y una lista corta de cambios con propósito claro.
