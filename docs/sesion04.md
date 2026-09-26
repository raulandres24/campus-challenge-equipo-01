# Iteración de la Sesión 04

## Equipo y proyecto
Reserva de salas de estudio — UPB Santa Cruz

| Integrante | Rol inicial / GitHub |
|---|---|
| Hugo Zúñiga | Configuración inicial y rotación |
| Raúl Vaca | Rotación |
| Alejandro Párraga | Rotación |

Cliente simulado: UPB Santa Cruz (Bolivia), sistema de reserva de salas de estudio. El docente, Sergio Barrientos, actúa como cliente.

Facilita y controla el tiempo: Trabajamos con los tres roles rotando entre Hugo, Raúl y Alejandro. Quien escribe el código, quien revisa la lógica, y quien valida o ejecuta las pruebas. Nos coordinamos mediante programación en grupo (Pair/Mob programming) intercambiando posiciones periódicamente.

## Backlog ordenado

| Orden | ID | Capacidad | ¿A quién ayuda y para qué? | Duda pendiente |
|---|---|---|---|---|
| 1 | PB-01 | Crear una reserva | Al solicitante, para reservar directamente una sala sin cruce de horarios. | ¿Cuántas salas puede reservar un alumno por horario? — (aclarada, ver abajo) |
| 2 | PB-02 | Consultar espacios disponibles | Al solicitante y al operador, para encontrar un espacio según la fecha, horario y capacidad. | ¿Existe un intervalo de tiempo entre reservas para el desalojo? — (aclarada, ver abajo) |
| 3 | PB-03 | Validar código de solicitante | Al solicitante, para verificar que está registrado antes de reservar. | ¿Qué hace válido un código de estudiante (formato o padrón)? |
| 4 | PB-04 | Modificar una reserva | Al solicitante para modificar su reserva y al operador para ayudarlo. | ¿Hasta cuánto tiempo antes se permite modificar? — (aclarada) |
| 5 | PB-05 | Cancelar una reserva | Al estudiante para cancelar su reserva y al operador. | ¿Penalizaciones por cancelar tarde? |

**Razón de la prioridad:** Se eligió trabajar PB-01 (Crear reserva) en esta iteración porque es el núcleo (core) del sistema de reservas. Sus reglas principales (capacidad, conflicto de horario e intervalo de limpieza) ya fueron aclaradas con el cliente. Es un objetivo alcanzable en esta sesión simulando los datos de las salas y estudiantes mediante diccionarios en memoria.

## Objetivo y alcance

> Al finalizar, el solicitante podrá crear una reserva de una sala de estudio para un bloque horario, siempre que la sala tenga capacidad suficiente para los asistentes, no exista conflicto de horario con otra reserva de esa sala (respetando el intervalo de 15 minutos de desalojo) y el estudiante no tenga ya otra reserva activa en ese mismo bloque.

**Alcance:**
- Se implementa PB-01 (crear reserva).
- Se aplicará Desarrollo Guiado por Pruebas (TDD) simulando la base de datos con diccionarios de Python en memoria para simplificar la lógica de esta iteración.
- Los errores no detendrán el programa; la función retornará un diccionario informando si el estado es CONFIRMADA o RECHAZADA, con un mensaje explicativo.
- Fuera de alcance en esta sesión: Validar existencia del estudiante en base de datos real, base de datos SQL, interfaz gráfica.

## Aclaraciones del cliente

| Pregunta | Respuesta del cliente | Efecto sobre el comportamiento esperado |
|---|---|---|
| ¿Existe un intervalo de tiempo entre reservas para el desalojo? | Se propone un intervalo de 15 minutos. | El sistema calculará una diferencia obligatoria de 15 minutos entre el fin de una reserva y el inicio de la siguiente para la misma sala. |
| ¿Cuántas salas puede reservar un alumno por horario? | Una sola sala. | El sistema buscará en el historial temporal; si el estudiante ya tiene reserva activa en ese bloque, se rechaza la nueva. |
| ¿Hasta cuánto tiempo antes se permite modificar? | Hasta 10 minutos después de haber sido realizada. | (Se aplicará cuando se programe el PB-04). |

## Ejemplos de aceptación

| Caso | Estado inicial y entrada | Resultado esperado | Regla que lo justifica |
|---|---|---|---|
| Uso normal | Salas en memoria: Sala A (capacidad 6). Libre de 10:00 a 12:00. Entrada: Estudiante 92345, Sala A, inicio "10:00", fin "12:00", 4 asistentes. | Retorna estado "CONFIRMADA" y el mensaje de éxito. | Los asistentes no superan la capacidad y el bloque está totalmente libre. |
| Límite | Estado inicial: Hay una reserva en la Sala A de "07:45" a "09:45". Entrada: Estudiante 92345, Sala A, inicio "10:00", fin "12:00". | Retorna estado "CONFIRMADA". | El fin (09:45) y el inicio (10:00) respetan exactamente los 15 minutos obligatorios de limpieza. |
| Rechazo (Situación excepcional) | Estado inicial: Sala A (cap. 6). Estudiante 92345 ya tiene una reserva en la Sala B para las 10:00. Entrada: Intenta reservar la Sala A a las 10:00. | Retorna estado "RECHAZADA" con mensaje "El estudiante ya cuenta con un espacio reservado en ese horario". | Un alumno solo puede reservar una sala por bloque horario. |

## Plan y seguimiento

**Definition of Done:**
- [ ] Los ejemplos acordados tienen pruebas ejecutables que pasan.
- [ ] El código fue revisado por otro integrante.
- [ ] La contribución está integrada en `main` y fue comprobada allí.
- [ ] El README permite ejecutar las pruebas.
- [ ] El equipo puede demostrar el resultado y explicar sus límites.

**Interfaz mínima acordada:**
    # proyecto/reglas.py
    def convertir_a_minutos(hora_texto): -> int
    def crear_reserva(salas, reservas, estudiante_codigo, sala_id, hora_inicio, hora_fin, asistentes): -> dict

    # Estructura de datos en memoria (Diccionarios):
    # salas = {"A": {"capacidad": 6}}
    # reservas_activas = [{"sala_id": "A", "estudiante_codigo": 92345, "inicio_min": 600, "fin_min": 720}]

| Tarea | Personas que colaboran | Estado | Evidencia o ubicación |
|---|---|---|---|
| T1. Armar backlog, ejemplos de aceptación y docs | Hugo, Raúl, Alejandro | Terminado | docs/sesion04.md |
| T2. Escribir esqueleto de funciones y primera prueba fallida | Hugo, Raúl, Alejandro | Por hacer | tests/test_reglas.py |
| T3. Implementar conversión de horas y validación de capacidad | Hugo, Raúl, Alejandro | Por hacer | proyecto/reglas.py |
| T4. Implementar validación de cruce de horarios (regla 15 min) | Hugo, Raúl, Alejandro | Por hacer | proyecto/reglas.py |
| T5. Integrar rama a main vía Pull Request y pasar suite final | Hugo, Raúl, Alejandro | Por hacer | Repositorio GitHub |

## Verificación e integración
(Pendiente de llenar al terminar la sesión con los resultados del `pytest`).

## Retroalimentación
(Pendiente de llenar tras mostrarle al cliente/ingeniero).

## Retrospectiva
(Pendiente de llenar al finalizar el laboratorio).

## Planificación y adaptación
(Pendiente).