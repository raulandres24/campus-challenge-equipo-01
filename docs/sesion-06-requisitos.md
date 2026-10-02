# Sesión 6 — Hallazgos y requisitos del proyecto

- Proyecto: Reserva de Salas de Estudio — UPB Santa Cruz
- Integrantes: Raúl Vaca, Hugo Zúñiga, Alejandro Párraga
- Fecha: 01/10/2026
- Cliente o fuente consultada: docente Sergio Barrientos (actúa como cliente), encargo inicial (RES-01 a RES-08) y acuerdos de la sesión 4 (`docs/sesion04.md`)
- Flujo seleccionado: **reserva / modificación** — crear una reserva de sala y modificar su horario o asistentes antes de que comience.

## 1. Hallazgos de la entrevista

| ID | Pregunta | Respuesta o hallazgo | Fuente | Estado |
|---|---|---|---|---|
| ENT-01 | ¿Cuánto tiempo debe pasar entre el fin de una reserva y el inicio de la siguiente en la misma sala? | Se propone un intervalo de 15 minutos de desalojo. | Docente, entrevista sesión 4 (`docs/sesion04.md`) | Confirmado |
| ENT-02 | ¿Un estudiante puede tener dos reservas activas en el mismo bloque horario? | Una sola sala por horario, aunque sean salas distintas. | Docente, entrevista sesión 4 (`docs/sesion04.md`) | Confirmado |
| ENT-03 | Si un cambio de reserva es rechazado (ej.: sala A 10:00–12:00 movida a 12:30–13:50 con otra reserva a las 14:00), ¿la reserva original se mantiene o se pierde? | El sistema debe mostrar un mensaje preguntando "¿Deseas mantenerla?". Si responde que no o presiona Esc, la reserva original se cancela. | Docente (Sergio), entrevista sesión 6 | Confirmado |
| ENT-04 | ¿Es coherente exigir en los términos y condiciones que solo puedan reservar estudiantes con matrícula al día? | Sí, es coherente: no puede reservar quien no tenga su matrícula al día. | Docente (Sergio), entrevista sesión 6 | Confirmado (falta definir cómo se verifica) |
| ENT-05 | Si mantenimiento bloquea una sala y ya había una reserva en ese horario, ¿qué debe hacer el sistema con esa reserva? | La reserva se cancela y se avisa al estudiante por email o por mensaje de WhatsApp que su reservación fue cancelada. | Docente (Sergio), entrevista sesión 6 | Confirmado (falta definir el canal: email, WhatsApp o ambos) |
| ENT-06 | ¿Qué pasa con las reservas existentes si se registra un bloqueo de mantenimiento en esa sala y horario? | La persona encargada de la gestión de las salas puede inhabilitarlas. | Docente (Sergio), entrevista sesión 6 | Confirmado |
| ENT-07 | Si dos personas reservan la misma sala a la misma hora, en el mismo segundo, ¿a nombre de quién queda la reserva? | A nombre de quien presionó primero el botón. | Docente (Sergio), entrevista sesión 6 | Confirmado |
| ENT-08 | ¿Se puede modificar o cancelar una reserva que ya comenzó? | No se puede modificar una vez que empezó; solo se puede modificar antes de que empiece. | Docente (Sergio), entrevista sesión 6 | Confirmado para modificar (cancelar: pendiente) |

## 2. Alcance del flujo

- Incluye: crear una reserva validando matrícula al día, sala existente, capacidad, choque de horario con 15 min de desalojo y una sola reserva por estudiante en el bloque; resolver solicitudes simultáneas por orden de llegada; modificar horario o asistentes de una reserva antes de que comience, con las mismas validaciones; mensaje con la causa del rechazo.
- No incluye: bloqueos de mantenimiento y su notificación por email/WhatsApp (RES-06; las reglas ya quedan registradas en ENT-05 y ENT-06 para modelarlas en la sesión 7), historial de correcciones (RES-07), agenda completa por espacio (RES-08), reservas recurrentes, pagos, integración con calendarios externos.

## 3. Requisitos

### RES-RF-01 — Choque de horario con margen de desalojo

- Tipo: funcional
- Origen: RES-04 del encargo; ENT-01
- Prioridad y razón: alta — es la regla central que evita cruces, el problema principal del cliente.
- Estado: aprobado por el cliente (sesión 4)
- Requisito: si una solicitud de reserva empieza antes de que hayan pasado 15 minutos desde el fin de otra reserva activa de la misma sala, o se superpone con ella, el sistema debe rechazarla y no registrar la nueva reserva.
- Criterio de aceptación:
  - Situación inicial: sala A con una reserva activa de 10:00 a 12:00.
  - Acción: el estudiante 92346 solicita la sala A de 12:10 a 13:00.
  - Resultado esperado: rechazo indicando conflicto de horario/desalojo; la agenda de la sala A sigue con una sola reserva (10:00–12:00).

### RES-RF-02 — Una reserva por estudiante en el mismo bloque

- Tipo: funcional
- Origen: RES-04 del encargo; ENT-02
- Prioridad y razón: alta — evita que un estudiante acapare salas.
- Estado: aprobado por el cliente (sesión 4)
- Requisito: si un estudiante ya tiene una reserva activa que se superpone con el horario solicitado, en cualquier sala, el sistema debe rechazar la nueva reserva y conservar la existente.
- Criterio de aceptación:
  - Situación inicial: el estudiante 92345 tiene la sala A de 10:00 a 11:00.
  - Acción: el mismo estudiante solicita la sala B de 10:30 a 11:30.
  - Resultado esperado: rechazo indicando que ya tiene una reserva en ese horario; solo existe la reserva de la sala A.

### RES-RF-03 — Modificación rechazada: confirmar si se mantiene la original

- Tipo: funcional
- Origen: RES-05 del encargo; ENT-03 (pregunta propia del equipo)
- Prioridad y razón: alta — define qué pasa con la reserva del estudiante cuando su cambio falla.
- Estado: aprobado por el cliente
- Requisito: si, antes del inicio de la reserva, el nuevo horario o la nueva cantidad de asistentes de una modificación no cumple las reglas de reserva, el sistema debe rechazar el cambio, no aplicar el nuevo horario y preguntar al estudiante "¿Deseas mantenerla?". Si responde que sí, la reserva original se conserva sin alteraciones; si responde que no o presiona Esc, la reserva original se cancela.
- Criterio de aceptación:
  - Situación inicial: sala A (capacidad 6) con reserva de 92345 de 10:00 a 12:00 y otra reserva de 14:00 a 15:00; son las 09:00.
  - Acción: mover la primera a 12:30–13:50 y luego responder al mensaje.
  - Resultado esperado: el cambio se rechaza por no respetar los 15 min antes de las 14:00 y aparece el mensaje "¿Deseas mantenerla?".
    - Si responde "Sí": la reserva sigue de 10:00 a 12:00 con sus mismos asistentes.
    - Si responde "No" o presiona Esc: la reserva de 10:00 a 12:00 queda cancelada y la sala A se libera en ese horario. La reserva de 14:00 no cambia en ningún caso.

### RES-RF-04 — Capacidad de la sala

- Tipo: funcional
- Origen: RES-03 y RES-04 del encargo
- Prioridad y razón: alta — asignar salas acordes al tamaño del grupo es parte del problema del cliente.
- Estado: aprobado (superar la capacidad); pendiente de aclaración (asistentes iguales a la capacidad)
- Requisito: si la cantidad de asistentes supera la capacidad de la sala, el sistema debe rechazar la reserva o modificación y no registrar cambios. El caso de asistentes iguales a la capacidad queda pendiente de confirmar con el cliente.
- Criterio de aceptación:
  - Situación inicial: sala A de capacidad 6, horario libre.
  - Acción: solicitud para 7 asistentes.
  - Resultado esperado: rechazo por capacidad; no aparece reserva nueva en la agenda.

### RES-RF-05 — Solo reservan estudiantes con matrícula al día

- Tipo: funcional
- Origen: RES-01 y RES-04 del encargo; ENT-04 (pregunta propia del equipo)
- Prioridad y razón: media — regla confirmada, pero falta definir de dónde se obtiene el estado de matrícula.
- Estado: aprobado por el cliente (regla); pendiente de aclaración (forma de verificarlo)
- Requisito: si el estudiante que solicita una reserva no tiene su matrícula al día, el sistema debe rechazar la solicitud indicando ese motivo y no registrar ninguna reserva. La condición debe figurar en los términos y condiciones de la aplicación.
- Criterio de aceptación:
  - Situación inicial: estudiante 92347 con matrícula no al día; sala A libre de 10:00 a 11:00.
  - Acción: 92347 solicita la sala A de 10:00 a 11:00.
  - Resultado esperado: rechazo con el mensaje de matrícula no vigente; la agenda de la sala A no cambia.

### RES-RF-06 — Modificación solo antes del inicio

- Tipo: funcional
- Origen: RES-05 del encargo; ENT-08 (pregunta propia del equipo)
- Prioridad y razón: alta — define hasta cuándo un estudiante puede cambiar su reserva.
- Estado: aprobado por el cliente
- Requisito: si una reserva ya comenzó, el sistema debe rechazar cualquier modificación de horario o asistentes, informar que la reserva ya está en curso y conservarla sin cambios.
- Criterio de aceptación:
  - Situación inicial: reserva de 92345 en sala A de 10:00 a 12:00; son las 10:30.
  - Acción: el estudiante intenta moverla a 11:00–13:00.
  - Resultado esperado: rechazo indicando que la reserva ya comenzó; la reserva sigue de 10:00 a 12:00 con sus mismos asistentes.

### RES-RF-07 — Solicitudes simultáneas por orden de llegada

- Tipo: funcional
- Origen: RES-04 del encargo; ENT-07 (pregunta propia del equipo)
- Prioridad y razón: media — es un caso poco frecuente, pero si no se controla se crean dos reservas cruzadas.
- Estado: aprobado por el cliente
- Requisito: si dos estudiantes solicitan la misma sala en horarios que se superponen casi al mismo tiempo, el sistema debe registrar la reserva solo a nombre de quien envió primero la solicitud y rechazar la segunda por conflicto de horario.
- Criterio de aceptación:
  - Situación inicial: sala A libre de 10:00 a 11:00.
  - Acción: 92345 envía la solicitud 10:00–11:00 y, inmediatamente después, 92346 envía la misma solicitud.
  - Resultado esperado: existe una sola reserva de la sala A de 10:00 a 11:00, a nombre de 92345; la solicitud de 92346 se rechaza por conflicto de horario.

### RES-RC-01 — Mensaje con la causa del rechazo

- Tipo: calidad
- Origen: adapta el ejemplo de calidad de la guía; aplica a RES-04 y RES-05
- Prioridad y razón: media — no cambia las reglas, pero sin él el estudiante no sabe qué corregir.
- Estado: propuesto (confirmar con el cliente)
- Requisito: cuando una reserva o modificación se rechaza por una regla de negocio, el sistema debe mostrar la causa concreta: sala inexistente, capacidad superada, conflicto de horario/desalojo, estudiante con reserva en el bloque, matrícula no al día o reserva ya iniciada.
- Criterio de aceptación:
  - Situación inicial: cualquiera de los escenarios de rechazo de RES-RF-01 a RES-RF-07.
  - Acción: ejecutar la solicitud rechazada.
  - Resultado esperado: el mensaje nombra la causa aplicable; un mensaje genérico como "Error" no cumple.

### RES-RT-01 — Lógica en Python

- Tipo: restricción
- Origen: encargo del curso
- Prioridad y razón: alta — es obligación del encargo.
- Estado: aprobado (encargo del curso)
- Requisito: las reglas principales del flujo de reserva/modificación deben implementarse en Python.
- Criterio de comprobación posterior:
  - Situación inicial: incremento entregado en el repositorio.
  - Acción: revisar el código y ejecutar las pruebas con pytest.
  - Resultado esperado: las reglas de RES-RF-01 a RES-RF-07 están implementadas en Python.

## 4. Escenarios del flujo

| Caso | Requisito relacionado | Datos y acción | Resultado esperado |
|---|---|---|---|
| Normal | RES-RF-03 | A las 07:00, reserva de 92345 en sala A, 10:00–12:00; se mueve a 08:00–09:30 sin otras reservas en conflicto. | Modificación aceptada; la reserva queda 08:00–09:30 y conserva sus asistentes. |
| Límite | RES-RF-01 | Sala A con reserva de 14:00 a 15:00; se solicita otra de 12:30 a 13:45 (exactamente 15 min de margen). | Se acepta (el margen exacto cumple la regla). |
| Límite | RES-RF-07 | Dos estudiantes solicitan la sala A de 10:00 a 11:00 casi en el mismo instante. | Solo se registra la del primero; la segunda se rechaza por conflicto. |
| Rechazo | RES-RF-03 | Mover la reserva a 12:30–13:50 con otra reserva a las 14:00; el estudiante responde "Sí" a "¿Deseas mantenerla?". | Cambio rechazado por desalojo; la reserva original sigue de 10:00 a 12:00. |
| Rechazo | RES-RF-06 | A las 10:30, intentar modificar una reserva de 10:00–12:00. | Rechazo por reserva ya iniciada; la reserva no cambia. |
| Rechazo | RES-RF-05 | Estudiante con matrícula no al día solicita una sala libre. | Rechazo con motivo de matrícula; no se crea la reserva. |

Estos escenarios están especificados. Evidencia ejecutada hasta hoy: en `main`, `pytest` pasa 6 de 6 pruebas (`tests/test_reglas.py`), entre ellas el rechazo por no respetar los 15 minutos (RES-RF-01) y el rechazo por reserva del mismo estudiante en otra sala (RES-RF-02). Los escenarios de modificación (RES-RF-03, RES-RF-06), simultaneidad (RES-RF-07) y matrícula (RES-RF-05) todavía no tienen prueba ejecutada porque esas funciones no están implementadas en `main`.

## 5. Preguntas y decisiones pendientes

| Pregunta | A quién consultar | Impacto mientras no se resuelva |
|---|---|---|
| Si los asistentes son exactamente iguales a la capacidad de la sala, ¿se acepta la reserva? | Docente (cliente) | Queda abierto el caso límite de RES-RF-04. |
| ¿Se puede cancelar una reserva que ya comenzó? (ENT-08 solo respondió sobre modificar) | Docente (cliente) | No se puede definir el límite temporal de la cancelación. |
| ¿Cómo sabe el sistema si la matrícula está al día? (¿lo carga un administrador, se consulta a otro sistema de la UPB?) | Docente (cliente) | No se puede implementar RES-RF-05 hasta definir la fuente del dato. |
| Al presionar Esc en "¿Deseas mantenerla?", ¿se confirma que la reserva se cancela, o debería mantenerse para evitar cancelaciones accidentales? | Docente (cliente) | Afecta el comportamiento de RES-RF-03 en un caso límite. |
| Ante una cancelación por mantenimiento, ¿se avisa por email, por WhatsApp o por ambos? (ENT-05) | Docente (cliente) | Afecta el diseño de RES-06 y qué datos de contacto se deben guardar del estudiante. |
| En la sesión 4 se acordó que una reserva puede modificarse "hasta 10 minutos después de haber sido realizada"; hoy (ENT-08) se indicó que puede modificarse mientras no haya comenzado. ¿Siguen vigentes ambas reglas o la nueva reemplaza a la anterior? | Docente (cliente) | Define el límite de tiempo de RES-RF-03 y RES-RF-06; hasta aclararlo se aplica la regla de hoy. |
| ¿Qué formato tiene el código de estudiante? | Docente (cliente) | Las pruebas usan 5 dígitos (92345) como dato ficticio, sin confirmar. |

## 6. Revisión por otro equipo

Sección omitida por indicación del docente: en esta sesión no se realizó el intercambio con otro equipo.

## 7. Siguiente paso

- Tarea: implementar `modificar_reserva` en `SistemaReservas`, rechazando el cambio si la reserva ya comenzó y aplicando las mismas validaciones de creación, con sus pruebas pytest.
- Requisito relacionado: RES-RF-03 y RES-RF-06
- Responsable inicial: Hugo Zuñiga
- Issue: no se creó todavía; el equipo no usa issues por ahora.

## 8. Participación y asistencia utilizada

- Aportes de cada integrante: [Quién preguntó: Raul Vaca y Alejandro Parraga, Quién registró: Raul Vaca, Quién revisó: Hugo Zuñiga y Raul Vaca]
- Asistencia de IA: Claude (Anthropic), para estructurar el documento a partir del encargo, de `docs/sesion04.md` y de las respuestas que el equipo obtuvo en la entrevista. El equipo realizó la entrevista, registró las respuestas y revisó los estados; las reglas de la sesión 4 se verificaron contra `docs/sesion04.md` y las pruebas se ejecutaron con pytest.
