# Reparto de tareas — requisitos faltantes (RES-01 a RES-08)

Basado en `docs/BRECHA_REQUISITOS.md`. Propuesta de reparto para que Raúl, Hugo y Alejandro puedan avanzar en paralelo sin pisarse. Ajustable en equipo.

## Raúl — RES-05: Modificar y cancelar reserva

Prioridad más alta: el modelo `Reserva` ya tiene `ESTADO_CONFIRMADA` / `ESTADO_CANCELADA` listos para usarse, solo falta la lógica y la vista.

- Vista `modificar_reserva` (y/o `cancelar_reserva`) en `reservas/views.py`, reutilizando las validaciones que ya existen en `Reserva.clean()`.
- Reglas a implementar (ya aprobadas por el docente, ver `docs/sesion-06-requisitos.md`):
  - **RES-RF-06**: no se puede modificar una reserva que ya comenzó.
  - **RES-RF-03**: si el nuevo horario o la nueva cantidad de asistentes no cumple las reglas, rechazar el cambio y preguntar "¿Deseas mantenerla?"; según la respuesta, conservar o cancelar la reserva original.
- Un template simple (sin preocuparse del diseño final) para que el estudiante pueda pedir el cambio, por ejemplo desde una futura `/mis-reservas/`.

## Hugo — RES-02: Consultar disponibilidad por fecha, horario y capacidad

> Nota: `docs/sesion-06-requisitos.md` (sección "Siguiente paso") le había asignado a Hugo implementar `modificar_reserva` en `proyecto/clases/sistema_reservas.py` — el sistema viejo en memoria, que no está conectado a MongoDB. Conviene reasignar esa tarea a RES-02, que sí es trabajo nuevo sobre el backend real y no se cruza con lo que hace Raúl.

- Vista que reciba fecha, hora de inicio/fin y capacidad mínima, y devuelva qué salas están libres en ese rango (consultando `Reserva.objects` para descartar las que chocan).
- Puede apoyarse en la misma lógica de choque de horario que ya existe en `Reserva._choca_con()` — es el mismo cálculo, aplicado a "¿qué sala sirve?" en vez de "¿esta reserva es válida?".
- Este dato también es lo que `home.html` necesitaría si más adelante se agrega un buscador ahí.

## Alejandro — Plantillas para lo nuevo + RES-08 (agenda por sala)

Toma la parte de interfaz de lo que construyan Raúl y Hugo, siguiendo el mismo patrón de `base.html` y Tailwind ya establecido (solo extender `{% block content %}`, sin reinventar estilos):

- Template de resultados para la búsqueda de disponibilidad (RES-02, una vez Hugo tenga la vista lista).
- Template para modificar/cancelar una reserva, incluyendo el diálogo de "¿Deseas mantenerla?" (RES-05, una vez Raúl tenga la vista lista).
- **RES-08**: página de "agenda por sala" — cada sala con sus reservas activas y canceladas, usando el campo `estado` que ya existe en `Reserva`. No depende de nadie más, se puede empezar de inmediato.

## Pendiente sin asignar todavía

- **RES-01 (estado del espacio) + RES-06 (bloqueos de mantenimiento)**: van juntos, ya que un bloqueo de mantenimiento es lo que pondría a una sala en estado "no disponible". El propio equipo los dejó fuera de alcance en sesión 6, para una sesión futura.
- **RES-07 (historial de correcciones administrativas)**: depende de que RES-05/RES-06 ya existan.

## Orden sugerido

Raúl y Hugo pueden trabajar en paralelo desde ya (RES-05 y RES-02 no se tocan entre sí). Alejandro puede adelantar RES-08 de inmediato porque no depende de nadie, y tomar las plantillas de RES-02/RES-05 cuando Hugo y Raúl tengan al menos las vistas básicas funcionando (aunque sea sin estilo).
