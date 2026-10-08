# Trazabilidad de las pruebas

- Proyecto: Reserva de Salas de Estudio — UPB Santa Cruz
- Fecha: 07/10/2026
- Total: **129 pruebas** en 9 archivos (104 funciones; 25 pruebas más salen de casos `parametrize`).
- Fuentes: [Sesión 6](sesion-06-requisitos.md) (requisitos), [Sesión 7](sesion-07-modelos.md) (historia y caso de uso), el encargo (RES-01 a RES-08) y la bitácora de decisiones del [README](../README.md).

## 1. Qué historias y casos de uso existen de verdad

| Tipo | ID | Qué es | Pruebas |
|---|---|---|---|
| Historia de usuario | `RES-HU-01` | El estudiante cambia el horario de su reserva antes de que comience | 18 (junto con el caso de uso) |
| Caso de uso | `RES-CU-01` | Modificar una reserva: ruta principal, E1 (cambio rechazado) y E2 (ya comenzó) | 18 (las mismas) |

**Solo hay una historia y un caso de uso escritos.** Las otras 111 pruebas no cuelgan de una historia ni de un caso de uso: cuelgan de requisitos (`RES-RF-xx`, `RES-RC-01`, `RES-RT-01`), del encargo (`RES-0x`) o de decisiones del docente anotadas en el README. Esa es la respuesta honesta a "¿cuáles son casos de uso y cuáles historias?": 18 pruebas de una sola historia y un solo caso de uso, y el resto son pruebas de reglas.

Cómo se reparten las 18 dentro de `RES-CU-01`:

| Parte del caso de uso | Pruebas |
|---|---|
| Precondición: la reserva es del estudiante que la modifica | 5 |
| Paso 1: botón "Modificar" visible en la reserva propia | 1 |
| Paso 3 y E2: la reserva ya comenzó | 5 |
| Pasos 6 a 8: ruta principal (normal, borde, reintento) | 3 |
| Paso 6: 15 minutos exactos se aceptan | 1 |
| E1: rechazo con causa, "¿Deseas mantenerla?" y reserva original intacta | 2 |
| E1 (extensión): cambio de fecha fuera de la ventana de anticipación | 1 |

## 2. Cobertura por requisito

Una prueba puede contar para más de un requisito, por eso la suma pasa de 129.

| Requisito | Qué exige | Pruebas | Estado |
|---|---|---|---|
| RES-RF-01 | 15 minutos de desalojo | 10 | Cubierto, incluido el límite exacto |
| RES-RF-02 | Una reserva por estudiante en el bloque | 3 | Cubierto |
| RES-RF-03 | Modificación rechazada y "¿Deseas mantenerla?" | 7 | **Parcial**: falta probar la respuesta "No" / Esc (la reserva pasa a Cancelada) |
| RES-RF-04 | Capacidad de la sala | 0 | **Sin prueba**: la regla existe en `proyecto/clases/` pero no en `services.py` |
| RES-RF-05 | Matrícula al día | 3 | Cubierto |
| RES-RF-06 | Modificar solo antes del inicio | 6 | Cubierto, incluido el minuto exacto |
| RES-RF-07 | Solicitudes simultáneas | 0 | **Sin prueba** |
| RES-RC-01 | Mensaje con la causa del rechazo | 7 | Cubierto |
| RES-RT-01 | Lógica en Python | todas | Cubierto |
| RES-01 | Solo estudiantes habilitados | 4 | Cubierto |
| RES-02 | Consultar disponibilidad | 3 | Cubierto en lo básico |
| RES-04 | Crear reserva | 7 | Cubierto |
| RES-05 | Modificar y cancelar | 9 (más las 18 de `RES-CU-01`) | Cubierto |
| RES-06 | Mantenimiento de salas | 4 | Parcial: bloquea reservar; cancelar reservas existentes y avisar quedó fuera de alcance (sesión 6) |
| RES-07 | Historial de correcciones | 0 | Fuera de alcance |
| RES-08 | Agenda por sala | 2 | Parcial |

Decisiones del docente que también tienen pruebas (no son `RES-RF`, están en la bitácora del README):

| Decisión | Pruebas |
|---|---|
| Salas por nivel (A y E de posgrado) | 14 |
| Padrón simulado y registro | 16 |
| Login único (FE → MW → DB del proyecto) | 9 |
| Anticipación para reservar | 25 |
| Reservas solo a nombre propio | 1 |
| Roles (docente y administrador) | 2 |
| Sesión (botón Salir) | 3 |

## 3. Tipos de prueba

| Tipo | Pruebas | Qué significa |
|---|---|---|
| Unitaria (pura) | 59 | Una función sola, sin MongoDB |
| Integración (MongoDB) | 56 | Varias funciones con la base de pruebas `test_...` |
| Integración (API + MongoDB) | 14 | Pasa por el cliente HTTP de Django: vista, sesión y base |

## 4. Brechas que conviene decir antes de entregar

1. **Capacidad (RES-RF-04)**: el requisito está aprobado y ninguna prueba lo verifica. Además `reservas/services.py` no la comprueba (solo la capa vieja de `proyecto/clases/`).
2. **Simultaneidad (RES-RF-07)**: sin prueba y sin control atómico en `services.py`.
3. **"¿Deseas mantenerla?" con "No" o Esc**: se prueba la pregunta, no la cancelación posterior.
4. **Historias y casos de uso faltantes**: registro, inicio de sesión, reservar, cancelar, salas por nivel y anticipación se probaron como reglas, sin historia ni caso de uso escritos.
5. Las pruebas de integración dependen de MongoDB real; en una máquina sin MongoDB solo corren las pruebas puras.

## 5. Detalle: las 129 pruebas, una por una

La columna "Prueba" lleva `×N` cuando una función se ejecuta con N casos de `parametrize`. La columna "#" cuenta pruebas ejecutadas (la cifra que muestra pytest).

### `test_modificar_reserva.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_no_ha_comenzado_acepta_antes_del_inicio` | No ha comenzado acepta antes del inicio | Unitaria (pura) | RES-RF-06 | CU-01 paso 3 |
| 2 | `test_ya_comenzo_rechaza_en_el_minuto_exacto_de_inicio` | Ya comenzo rechaza en el minuto exacto de inicio | Unitaria (pura) | RES-RF-06 | CU-01 E2 |
| 3 | `test_ya_comenzo_rechaza_si_esta_en_curso` | Ya comenzo rechaza si esta en curso | Unitaria (pura) | RES-RF-06 | CU-01 E2 |
| 4 | `test_duenio_se_reconoce_por_nombre_exacto` | Duenio se reconoce por nombre exacto | Unitaria (pura) | RES-RF-03 (solo el dueño modifica) | CU-01 precondición |
| 5 | `test_usuario_sin_nombre_no_es_duenio_de_ninguna_reserva` | Usuario sin nombre no es duenio de ninguna reserva | Unitaria (pura) | RES-RF-03 (solo el dueño modifica) | CU-01 precondición |
| 6 | `test_nombre_parcial_no_cuenta_como_duenio` | Nombre parcial no cuenta como duenio | Unitaria (pura) | RES-RF-03 (solo el dueño modifica) | CU-01 precondición |
| 7 | `test_normal_mover_a_horario_libre_cambia_solo_esa_reserva` | Normal mover a horario libre cambia solo esa reserva | Integración (MongoDB) | RES-05 (caso Normal) | HU-01 / CU-01 pasos 6-8 |
| 8 | `test_borde_se_puede_solapar_con_su_propio_horario_anterior` | Borde se puede solapar con su propio horario anterior | Integración (MongoDB) | RES-05 (caso Borde) | CU-01 paso 6 |
| 9 | `test_limite_15_minutos_exactos_antes_de_otra_reserva_se_acepta` | Limite 15 minutos exactos antes de otra reserva se acepta | Integración (MongoDB) | RES-RF-01 (caso Límite) | CU-01 paso 6 |
| 10 | `test_rechazo_por_desalojo_conserva_la_reserva_original` | Rechazo por desalojo conserva la reserva original | Integración (MongoDB) | RES-RF-03, RES-RF-01 | HU-01 / CU-01 E1 |
| 11 | `test_rechazo_si_la_reserva_ya_comenzo` | Rechazo si la reserva ya comenzo | Integración (MongoDB) | RES-RF-06 | CU-01 E2 |
| 12 | `test_reintentar_la_misma_modificacion_no_falla_ni_duplica` | Reintentar la misma modificacion no falla ni duplica | Integración (MongoDB) | RES-05 (robustez) | CU-01 pasos 6-7 |
| 13 | `test_endpoint_rechazo_devuelve_causa_y_pregunta_si_mantenerla` | Endpoint rechazo devuelve causa y pregunta si mantenerla | Integración (API + MongoDB) | RES-RF-03, RES-RC-01 | HU-01 / CU-01 E1 |
| 14 | `test_endpoint_otro_estudiante_no_puede_modificar` | Endpoint otro estudiante no puede modificar | Integración (API + MongoDB) | RES-RF-03 (solo el dueño modifica) | CU-01 precondición |

Subtotal `test_modificar_reserva.py`: **14** pruebas.

### `test_agenda.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_reserva_movida_fuera_de_bloque_sigue_visible` | Reserva movida fuera de bloque sigue visible | Unitaria (pura) | RES-08 (agenda del día) | — |
| 2 | `test_reserva_que_cruza_dos_bloques_ocupa_ambos` | Reserva que cruza dos bloques ocupa ambos | Unitaria (pura) | RES-08 (agenda del día) | — |
| 3 | `test_sala_en_mantenimiento_nunca_figura_libre` | Sala en mantenimiento nunca figura libre | Unitaria (pura) | RES-06 (mantenimiento) | — |
| 4 | `test_pantalla_muestra_modificar_en_reserva_propia_no_iniciada` | Pantalla muestra modificar en reserva propia no iniciada | Unitaria (pura) | RES-05, RES-RF-06 | CU-01 paso 1 |
| 5 | `test_pantalla_oculta_modificar_si_la_reserva_ya_comenzo` | Pantalla oculta modificar si la reserva ya comenzo | Unitaria (pura) | RES-RF-06 | CU-01 paso 3 / E2 |

Subtotal `test_agenda.py`: **5** pruebas.

### `test_integracion_completa.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_01_flujo_completo_reserva_exitosa_y_verificacion_datos_mongo` | Flujo completo de reserva exitosa con verificación directa en MongoDB. | Integración (MongoDB) | RES-04 | — |
| 2 | `test_02_rechazo_reserva_estudiante_inactivo_sin_guardar_mongo` | Rechazo de reserva por estudiante inactivo y comprobación de cero registros en Mongo. | Integración (MongoDB) | RES-01 | — |
| 3 | `test_03_rechazo_reserva_estudiante_sin_matricula_pagada` | Rechazo de reserva por matrícula pendiente y comprobación de no persistencia en Mongo. | Integración (MongoDB) | RES-RF-05 | — |
| 4 | `test_04_rechazo_reserva_sala_en_mantenimiento` | Rechazo cuando la sala solicitada está en mantenimiento técnico. | Integración (MongoDB) | RES-06, RES-RC-01 | — |
| 5 | `test_05_rechazo_reserva_sala_inexistente` | Rechazo cuando se solicita una sala que no existe en MongoDB. | Integración (MongoDB) | RES-RC-01 | — |
| 6 | `test_06_rechazo_choque_exacto_de_horario_misma_sala` | Rechazo por cruce directo de horario en la misma sala y fecha. | Integración (MongoDB) | RES-RF-01 | — |
| 7 | `test_07_rechazo_violacion_buffer_15_minutos_desalojo` | Rechazo por violación del margen de 15 minutos de desalojo/limpieza. | Integración (MongoDB) | RES-RF-01 | — |
| 8 | `test_08_aceptacion_limite_exacto_buffer_15_minutos` | Aceptación en el límite exacto del intervalo de 15 minutos de buffer. | Integración (MongoDB) | RES-RF-01 (caso Límite) | — |
| 9 | `test_09_rechazo_estudiante_con_doble_reserva_en_mismo_horario` | Rechazo si el mismo estudiante intenta reservar dos salas diferentes en el mismo bloque. | Integración (MongoDB) | RES-RF-02 | — |
| 10 | `test_10_ciclo_vida_reserva_mongo_consulta_cancelacion_y_liberacion` | Ciclo de vida completo: Reserva -> Consulta disponibilidad -> Cancelación -> Reocupación. | Integración (MongoDB) | RES-04, RES-05 (cancelar), RES-02 | — |

Subtotal `test_integracion_completa.py`: **10** pruebas.

### `test_reglas.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad` | Valida que una reserva válida se confirme exitosamente si la sala está libre y tiene capacidad. | Integración (MongoDB) | RES-04 | — |
| 2 | `test_rechaza_reserva_si_no_respeta_15_minutos_de_desalojo` | Valida que se rechace una reserva si entre la anterior y la nueva hay menos de 15 minutos de margen. | Integración (MongoDB) | RES-RF-01 | — |
| 3 | `test_rechaza_si_estudiante_ya_tiene_reserva_en_otra_sala_mismo_bloque` | Valida que un estudiante no pueda reservar dos salas diferentes en el mismo horario. | Integración (MongoDB) | RES-RF-02 | — |
| 4 | `test_consultar_espacios_disponibles` | Valida la consulta de salas libres excluyendo aquellas ocupadas en el intervalo. | Integración (MongoDB) | RES-02 | — |
| 5 | `test_cancelar_reserva_exitosa` | Valida que la cancelación de una reserva existente elimine el registro y libere el espacio. | Integración (MongoDB) | RES-05 (cancelar) | — |
| 6 | `test_cancelar_reserva_rechazada_si_no_existe` | Valida que intentar cancelar una reserva inexistente retorne un estado de rechazo. | Integración (MongoDB) | RES-05 (cancelar), RES-RC-01 | — |

Subtotal `test_reglas.py`: **6** pruebas.

### `test_unitarios_simples.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_convertir_a_minutos_formato_texto` | Convierte texto '10:30' a 630 minutos. | Unitaria (pura) | RES-RT-01 (base de RF-01) | — |
| 2 | `test_convertir_a_minutos_objeto_time` | Convierte objeto datetime.time(7, 45) a 465 minutos. | Unitaria (pura) | RES-RT-01 (base de RF-01) | — |
| 3 | `test_convertir_a_minutos_formato_invalido_lanza_error` | Valida que un formato inválido lance ValueError. | Unitaria (pura) | RES-RT-01 (base de RF-01) | — |
| 4 | `test_minutos_a_time_conversion_correcta` | Convierte 600 minutos al objeto datetime.time(10, 0). | Unitaria (pura) | RES-RT-01 (base de RF-01) | — |
| 5 | `test_validar_rango_horario_valido` | Valida que hora inicio menor a fin retorne los minutos. | Unitaria (pura) | RES-04 | — |
| 6 | `test_validar_rango_horario_invalido_fin_menor_que_inicio` | Valida que hora fin <= inicio lance ValueError. | Unitaria (pura) | RES-04, RES-RC-01 | — |
| 7 | `test_hay_choque_con_buffer_dentro_del_margen_15_min` | Detecta choque si la distancia entre reservas es de solo 10 minutos. | Unitaria (pura) | RES-RF-01 | — |
| 8 | `test_hay_choque_con_buffer_fuera_del_margen_15_min` | NO detecta choque si se respeta exactamente el buffer de 15 minutos. | Unitaria (pura) | RES-RF-01 (caso Límite) | — |
| 9 | `test_hay_solapamiento_simple_directo` | Detecta cruce de horario directo entre dos intervalos. | Unitaria (pura) | RES-RF-01 | — |
| 10 | `test_parsear_horas_desde_cadena` | Parsea '10:00-12:00' a tupla de objetos datetime.time. | Unitaria (pura) | RES-RT-01 (base de RF-01) | — |
| 11 | `test_validar_estudiante_habilitado_exitoso` | Valida estudiante activo y con matrícula al día en MongoDB. | Integración (MongoDB) | RES-01, RES-RF-05 | — |
| 12 | `test_validar_estudiante_rechazado_si_inactivo` | Rechaza estudiante inactivo consultado en MongoDB. | Integración (MongoDB) | RES-01 | — |
| 13 | `test_validar_estudiante_rechazado_si_sin_matricula` | Rechaza estudiante sin matrícula pagada en MongoDB. | Integración (MongoDB) | RES-RF-05 | — |
| 14 | `test_validar_estudiante_rechazado_si_no_existe` | Rechaza estudiante inexistente en MongoDB. | Integración (MongoDB) | RES-01, RES-RC-01 | — |
| 15 | `test_validar_sala_habilitada_exitosa` | Valida sala existente y sin mantenimiento en MongoDB. | Integración (MongoDB) | RES-04, RES-06 | — |
| 16 | `test_validar_sala_rechazada_en_mantenimiento` | Rechaza sala en estado de mantenimiento en MongoDB. | Integración (MongoDB) | RES-06 | — |
| 17 | `test_validar_sala_rechazada_si_no_existe` | Rechaza sala inexistente en MongoDB. | Integración (MongoDB) | RES-RC-01 | — |
| 18 | `test_revisar_choque_horario_dia_en_sala_libre` | Verifica que un horario libre en una sala retorne True. | Integración (MongoDB) | RES-RF-01 | — |
| 19 | `test_revisar_reserva_estudiante_en_horario_libre` | Verifica que el estudiante no tenga cruces de horario. | Integración (MongoDB) | RES-RF-02 | — |
| 20 | `test_guardar_reserva_mongo_crea_registro` | Valida que guardar_reserva_mongo persista en MongoDB. | Integración (MongoDB) | RES-04 | — |
| 21 | `test_cancelar_reserva_en_mongo_inexistente` | Cancelar una reserva inexistente retorna False. | Integración (MongoDB) | RES-05 (cancelar) | — |
| 22 | `test_consultar_salas_disponibles_dia_retorna_lista` | Consulta salas disponibles para un día y rango horario. | Integración (MongoDB) | RES-02 | — |
| 23 | `test_alias_reservar_si_es_posible_camel_case` | Verifica que el alias reservarSiesPosible funcione idéntico. | Integración (MongoDB) | RES-RT-01 (compatibilidad) | — |
| 24 | `test_tiene_poderes_especiales_usuarios_designados` | Verifica que Sergio, Hugo, Raúl y Alejandro tengan poderes. | Unitaria (pura) | Roles (docente/admin) | — |
| 25 | `test_obtener_info_usuario_formato_correcto` | Valida que obtener_info_usuario devuelva la insignia y rol adecuados. | Unitaria (pura) | Roles (docente/admin) | — |

Subtotal `test_unitarios_simples.py`: **25** pruebas.

### `test_niveles.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1–6 | `test_tabla_de_niveles_y_salas` ×6 | Tabla de niveles y salas | Unitaria (pura) | Decisión: salas por nivel (A y E posgrado) | — |
| 7 | `test_nivel_vacio_se_trata_como_pregrado` | Nivel vacio se trata como pregrado | Unitaria (pura) | Decisión: salas por nivel (A y E posgrado) | — |
| 8 | `test_mensajes_dicen_que_sala_es_de_quien` | Mensajes dicen que sala es de quien | Unitaria (pura) | Decisión: salas por nivel (A y E posgrado) | — |
| 9 | `test_pregrado_reserva_sala_comun` | Pregrado reserva sala comun | Integración (MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |
| 10 | `test_pregrado_no_reserva_sala_exclusiva_de_posgrado` | Pregrado no reserva sala exclusiva de posgrado | Integración (MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |
| 11 | `test_postgrado_reserva_sala_exclusiva_y_no_la_comun` | Postgrado reserva sala exclusiva y no la comun | Integración (MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |
| 12 | `test_endpoint_pregrado_no_reserva_sala_de_posgrado` | Endpoint pregrado no reserva sala de posgrado | Integración (API + MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |
| 13 | `test_endpoint_postgrado_reserva_su_sala` | Endpoint postgrado reserva su sala | Integración (API + MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |
| 14 | `test_cada_estudiante_ve_solo_las_salas_de_su_nivel` | Cada estudiante ve solo las salas de su nivel | Integración (API + MongoDB) | Decisión: salas por nivel (A y E posgrado) | — |

Subtotal `test_niveles.py`: **14** pruebas.

### `test_padron.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_busca_por_codigo_y_correo_sin_distinguir_mayusculas` | Busca por codigo y correo sin distinguir mayusculas | Unitaria (pura) | Decisión: padrón simulado y registro | — |
| 2 | `test_correo_que_no_corresponde_al_codigo_no_entra` | Correo que no corresponde al codigo no entra | Unitaria (pura) | Decisión: padrón simulado y registro | — |
| 3 | `test_datos_vacios_no_entran` | Datos vacios no entran | Unitaria (pura) | Decisión: padrón simulado y registro | — |
| 4 | `test_padron_del_repositorio_es_ficticio_y_consistente` | Padron del repositorio es ficticio y consistente | Unitaria (pura) | Decisión: padrón simulado y registro | — |
| 5 | `test_padron_del_repositorio_tiene_todos_los_roles_y_niveles` | Padron del repositorio tiene todos los roles y niveles | Unitaria (pura) | Decisión: padrón simulado y registro | — |
| 6 | `test_duenio_por_codigo_de_estudiante` | Duenio por codigo de estudiante | Unitaria (pura) | RES-RF-03 (solo el dueño modifica) | CU-01 precondición |
| 7 | `test_registro_crea_la_cuenta_con_los_datos_del_padron` | Registro crea la cuenta con los datos del padron | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 8 | `test_registro_de_postgrado_guarda_su_nivel_y_el_de_carlos_su_matricula` | Registro de postgrado guarda su nivel y el de carlos su matricula | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 9–11 | `test_el_rol_del_padron_decide_los_permisos` ×3 | El rol del padron decide los permisos | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 12–15 | `test_registro_rechaza_a_quien_no_corresponde` ×4 | Registro rechaza a quien no corresponde | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 16 | `test_registro_rechaza_contrasenas_distintas_o_debiles` | Registro rechaza contrasenas distintas o debiles | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 17 | `test_no_se_puede_registrar_dos_veces_ni_cambiar_la_contrasena_de_otro` | No se puede registrar dos veces ni cambiar la contrasena de otro | Integración (MongoDB) | Decisión: padrón simulado y registro | — |
| 18 | `test_hay_un_solo_formulario_de_inicio_de_sesion_y_un_enlace_al_registro` | Hay un solo formulario de inicio de sesion y un enlace al registro | Integración (MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 19–20 | `test_despues_de_registrarse_inicia_sesion_y_va_a_su_pantalla` ×2 | Despues de registrarse inicia sesion y va a su pantalla | Integración (API + MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 21 | `test_el_login_no_consulta_el_padron` | El login no consulta el padron | Integración (MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 22 | `test_estar_en_el_padron_no_basta_para_iniciar_sesion_sin_registrarse` | Estar en el padron no basta para iniciar sesion sin registrarse | Integración (MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 23–25 | `test_login_rechaza_con_mensaje_generico` ×3 | Login rechaza con mensaje generico | Integración (MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 26 | `test_login_rechaza_codigo_que_no_tiene_5_digitos` | Login rechaza codigo que no tiene 5 digitos | Integración (MongoDB) | Decisión: login único (FE → MW → DB del proyecto) | — |
| 27 | `test_estudiante_solo_puede_reservar_a_su_nombre` | Estudiante solo puede reservar a su nombre | Integración (API + MongoDB) | Decisión: reservas solo a nombre propio | — |

Subtotal `test_padron.py`: **27** pruebas.

### `test_ventanas.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_dias_de_clase_no_cuentan_sabado_ni_domingo` | Dias de clase no cuentan sabado ni domingo | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 2–9 | `test_posgrado_reserva_hasta_dos_dias_de_clase_adelante` ×8 | Posgrado reserva hasta dos dias de clase adelante | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 10–15 | `test_pregrado_reserva_el_dia_siguiente_desde_las_18` ×6 | Pregrado reserva el dia siguiente desde las 18 | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 16 | `test_la_hora_se_interpreta_en_la_paz_cuando_viene_con_zona` | La hora se interpreta en la paz cuando viene con zona | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 17 | `test_apertura_de_reservas` | Apertura de reservas | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 18 | `test_ultima_fecha_reservable` | Ultima fecha reservable | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 19 | `test_mensajes_dicen_cuando_se_abre` | Mensajes dicen cuando se abre | Unitaria (pura) | Decisión: anticipación para reservar (07/10) | — |
| 20 | `test_pregrado_no_reserva_mas_alla_de_su_ventana` | Pregrado no reserva mas alla de su ventana | Integración (API + MongoDB) | Decisión: anticipación para reservar (07/10) | — |
| 21 | `test_pregrado_si_reserva_para_hoy` | Pregrado si reserva para hoy | Integración (API + MongoDB) | Decisión: anticipación para reservar (07/10) | — |
| 22 | `test_posgrado_no_reserva_mas_alla_de_sus_dos_dias_de_clase` | Posgrado no reserva mas alla de sus dos dias de clase | Integración (API + MongoDB) | Decisión: anticipación para reservar (07/10) | — |
| 23 | `test_administrador_no_tiene_limite_de_anticipacion` | Administrador no tiene limite de anticipacion | Integración (API + MongoDB) | Decisión: anticipación para reservar (07/10) | — |
| 24 | `test_modificar_a_una_fecha_fuera_de_la_ventana_se_rechaza_y_deja_la_original` | Modificar a una fecha fuera de la ventana se rechaza y deja la original | Integración (API + MongoDB) | Decisión: anticipación + RES-05 | CU-01 E1 (extensión) |
| 25 | `test_la_agenda_dice_hasta_que_dia_puede_reservar` | La agenda dice hasta que dia puede reservar | Integración (API + MongoDB) | Decisión: anticipación para reservar (07/10) | — |

Subtotal `test_ventanas.py`: **25** pruebas.

### `test_urls.py`

| # | Prueba | Qué comprueba | Tipo | Requisito | Historia / caso de uso |
|---|---|---|---|---|---|
| 1 | `test_url_logout_apunta_a_la_vista_propia` | Url logout apunta a la vista propia | Unitaria (pura) | Sesión (botón Salir) | — |
| 2 | `test_url_login_apunta_a_la_vista_propia` | Url login apunta a la vista propia | Unitaria (pura) | Sesión (login único) | — |
| 3 | `test_boton_salir_con_get_redirige_al_login` | Boton salir con get redirige al login | Unitaria (pura) | Sesión (botón Salir) | — |

Subtotal `test_urls.py`: **3** pruebas.
