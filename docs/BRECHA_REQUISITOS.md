# Brecha contra el encargo inicial (RES-01 a RES-08)

Comparación entre el encargo del cliente (`P02 — Reservas de salas e instalaciones`, sesión 02) y lo que hoy existe en el backend real (Django + MongoDB, carpeta `reservas/`). Sirve de punto de partida para repartir lo que falta.

> El encargo original (RES-01 a RES-08) no está commiteado como archivo en este repo — lo compartió el docente aparte. Esta tabla resume su contenido para que el equipo no tenga que volver a buscarlo.

## Estado por requisito

| ID | Qué pide el encargo | Estado en `reservas/` | Detalle |
|---|---|---|---|
| RES-01 | Registrar espacios (id, capacidad, **estado**) y solicitantes | Parcial | `Sala` tiene nombre, capacidad, ubicación, proyector/pizarra. `Usuario` / `PadronPersona` cubren solicitantes (con verificación real contra el padrón, más robusto que lo pedido). **Falta** un campo de estado del espacio (disponible / en mantenimiento) — depende de RES-06. |
| RES-02 | Consultar disponibilidad por fecha, horario y capacidad | **Falta** | `home.html` lista todas las salas y todas las reservas activas, pero no hay un buscador/filtro por fecha + horario + capacidad. |
| RES-03 | Crear una reserva (solicitante, espacio, intervalo, asistentes) | Hecho | `/reservar/` (`crear_reserva` view + `ReservaForm`). |
| RES-04 | Aplicar reglas de horario, capacidad y conflictos antes de confirmar | Mayormente hecho | Capacidad (RES-RF-04), cruce de horario + 15 min de desalojo (RES-RF-01), una reserva por estudiante en el mismo bloque (RES-RF-02), restricción solo-docentes (Sala A y E). **Falta**: horario de apertura / días sin servicio (no existe ese concepto todavía) y orden de llegada en solicitudes simultáneas (RES-RF-07, sin probar). |
| RES-05 | Modificar o cancelar una reserva | **Falta por completo** | `Reserva` ya tiene `ESTADO_CONFIRMADA` / `ESTADO_CANCELADA` en el modelo, pero no hay vista ni formulario que los use. Es el flujo que el propio equipo eligió documentar en sesión 6 (RES-RF-03 y RES-RF-06, con criterios de aceptación ya escritos) — está especificado pero no implementado aquí. |
| RES-06 | Registrar bloqueos administrativos o de mantenimiento | **Falta** | No existe modelo de bloqueo. El equipo ya lo marcó fuera de alcance de la sesión 6 para una sesión futura. Las reglas ya están acordadas con el docente (ENT-05: la reserva afectada se cancela y se avisa al estudiante; ENT-06: el encargado de salas puede inhabilitarlas) pero no están modeladas en código. |
| RES-07 | Corregir una operación administrativa conservando motivo e historial | **Falta** | No hay modelo de auditoría/historial en ningún lado del proyecto. |
| RES-08 | Mostrar agenda por espacio, reservas activas y cancelaciones | Parcial | Hay una lista de reservas activas ordenada por fecha/hora, pero no agrupada por sala como una agenda, y no muestra cancelaciones (porque cancelar todavía no existe). |

## Prioridad sugerida

1. **RES-05 — Modificar / cancelar reserva.** Es la brecha más urgente: ya tiene requisitos aprobados por el cliente (RES-RF-03, RES-RF-06 en `docs/sesion-06-requisitos.md`) y el modelo ya tiene los campos de estado listos para usarse. Ojo: el "siguiente paso" de `docs/sesion-06-requisitos.md` asigna esto a Hugo pero apuntando al sistema viejo en memoria (`proyecto/clases/sistema_reservas.py`), que no está conectado a MongoDB — conviene decidir en equipo si se traslada esa lógica a `reservas/models.py` + `reservas/views.py`.
2. **RES-02 — Buscar disponibilidad por fecha/horario/capacidad.** Es la siguiente brecha visible para un usuario real; hoy solo se ve "todo lo que hay", no se puede filtrar.
3. **RES-01 (estado del espacio) y RES-06 (bloqueos de mantenimiento)** van juntos — conviene resolverlos en la misma tarea, ya que un bloqueo de mantenimiento es justamente lo que pondría a una sala en estado "no disponible".
4. **RES-07 (historial de correcciones) y la parte de RES-08 (agenda por espacio con cancelaciones)** dependen de que RES-05/RES-06 ya existan, así que van al final.

## Preguntas que siguen abiertas con el docente (de `docs/sesion-06-requisitos.md`)

- ¿Si los asistentes son exactamente iguales a la capacidad, se acepta la reserva?
- ¿Se puede cancelar una reserva que ya comenzó? (solo se confirmó que no se puede *modificar*)
- ¿El aviso de cancelación por mantenimiento es por email, WhatsApp o ambos?
- Al presionar Esc en "¿Deseas mantenerla?", ¿se confirma la cancelación o se mantiene la reserva por seguridad?
- ¿Sigue vigente la regla de sesión 4 ("modificable hasta 10 minutos después de creada") junto con la de sesión 6 ("modificable mientras no haya comenzado"), o la reemplaza?
