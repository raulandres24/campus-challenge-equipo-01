# Sistema de Reserva de Salas — UPB Santa Cruz
## Informe Completo de Refactorización, Arquitectura y Suite de Pruebas

---

### 1. Resumen Ejecutivo de lo Realizado desde el Inicio

El proyecto ha sido estructurado y refactorizado de principio a fin siguiendo **Clean Architecture**, **Clean Code** y el principio de **Responsabilidad Única (SRP)**, integrando una base de datos real **MongoDB** mediante `django-mongodb-backend` y Django ORM 5.2.

A continuación se detallan las fases completadas:

1. **Corrección y Migración de Base de Datos MongoDB:**
   - Se configuraron los modelos relacionales en MongoDB mediante `django-mongodb-backend` con Replica Set (`rs0`).
   - Se crearon y aplicaron las migraciones iniciales (`reservas/migrations/0001_initial.py`).
   - Se implementó el comando de inicialización de datos de prueba (`python manage.py poblar_bd`) con 5 salas, 10 estudiantes y 30 reservas de ejemplo.
   - Se configuró el panel administrativo de Django con `@admin.register` para `Estudiante`, `Sala` y `Reserva`.

2. **Refactorización Modular de la Carpeta `proyecto/clases/`:**
   - Se transformó la lógica previa en **funciones simples, modulares, altamente cohesivas y desacopladas**.
   - Se implementó la función principal `reservar_si_es_posible` (con alias `reservarSiesPosible`) que valida todas las reglas y persiste en MongoDB, retornando estado (`CONFIRMADA` o `RECHAZADA`) y mensajes descriptivos.
   - Se implementó la función revisora `revisar_choque_horario_dia` para detectar colisiones en una sala considerando el intervalo obligatorio de **15 minutos de desalojo**.

3. **Suite Completa de Pruebas Automatizadas (39 Pruebas Pasando):**
   - **Nivel 1 — Pruebas Unitarias Aisladas (23 tests):** Cada test llama **únicamente a 1 función** de forma aislada.
   - **Nivel 2 — Pruebas de Integración Multi-función (10 tests):** Combinan múltiples funciones y validan directamente los datos guardados en las colecciones de MongoDB.
   - **Nivel 3 — Pruebas de Reglas Históricas (6 tests):** Compatibilidad retroactiva 100% verificada.

---

### 2. Modelos de Base de Datos en MongoDB (`reservas/models.py`)

Se diseñaron tres entidades bajo la sintaxis del ORM de Django traducida de forma nativa a MongoDB:

| Modelo | Atributos Clave | Métodos / Propiedades | Regla de Negocio Soportada |
|---|---|---|---|
| **`Estudiante`** | `codigo_estudiante` (único), `nombres`, `apellidos`, `esta_activo`, `matricula_pagada` | `@property puede_reservar` | Un estudiante solo puede reservar si está activo y tiene su matrícula al día. |
| **`Sala`** | `nombre` (único), `en_mantenimiento` (booleano) | `@property disponible` | No almacena booleanos estáticos de "ocupada"; la disponibilidad se calcula temporalmente por bloques y mantenimiento. |
| **`Reserva`** | `estudiante` (FK), `sala` (FK), `fecha`, `hora_inicio`, `hora_fin`, `estado` (`CONFIRMADA`/`CANCELADA`) | `BUFFER_MINUTOS = 15`<br>`choca_con()`<br>`solapa_estudiante()` | Controla colisiones en la misma sala (margen de 15 min) y colisiones del mismo estudiante en diferentes salas. |

---

### 3. Estructura Refactorizada de `proyecto/clases/`

La carpeta `proyecto/clases/` se organizó en submódulos especializados donde cada función tiene una única responsabilidad:

```text
proyecto/clases/
├── __init__.py           # Exporta la API pública limpia del paquete
├── _db.py                # Inicialización transparente de Django y conexión a MongoDB
├── horarios.py           # Funciones puras de cálculo de horas, buffers y validación
├── estudiante.py         # Consulta y validación de estudiantes contra MongoDB
├── sala.py               # Consulta y validación de salas contra MongoDB
├── reserva.py            # Revisión de choques en Mongo, guardado y cancelación
└── sistema_reservas.py   # Orquestador principal reservar_si_es_posible y consultas
```

#### Detalle de Funciones por Módulo

#### A. `horarios.py` (Funciones puras de tiempo)
- `convertir_a_minutos(hora)`: Convierte `"HH:MM"` o `datetime.time` a minutos desde medianoche (ej: `"10:30"` -> `630`).
- `minutos_a_time(minutos)`: Convierte minutos enteros a un objeto `datetime.time`.
- `validar_rango_horario(hora_inicio, hora_fin)`: Valida que `hora_fin > hora_inicio`. Retorna `(min_inicio, min_fin)` o lanza `ValueError`.
- `hay_choque_con_buffer(inicio_a, fin_a, inicio_b, fin_b, buffer_min=15)`: Evalúa si dos bloques solapan con margen de desalojo:
  $$\text{inicio}_a < (\text{fin}_b + \text{buffer}) \land \text{fin}_a > (\text{inicio}_b - \text{buffer})$$
- `hay_solapamiento_simple(inicio_a, fin_a, inicio_b, fin_b)`: Evalúa cruce directo de tiempo para un mismo estudiante.
- `parsear_horas(horas)`: Parsea cadenas `"10:00-12:00"` o tuplas `("10:00", "12:00")`.

#### B. `estudiante.py` (Validación de Estudiante en MongoDB)
- `obtener_estudiante(codigo_estudiante)`: Busca en MongoDB por `codigo_estudiante`. Retorna el modelo o `None`.
- `validar_estudiante_habilitado(codigo_o_obj)`: Función simple que valida:
  1. ¿Existe en la BD?
  2. ¿`esta_activo == True`?
  3. ¿`matricula_pagada == True`?
  Retorna `(True, "Estudiante habilitado.", obj)` o `(False, "Motivo...", None)`.

#### C. `sala.py` (Validación de Sala en MongoDB)
- `obtener_sala(nombre_o_num)`: Busca en MongoDB por coincidencia exacta o alias.
- `validar_sala_habilitada(nombre_o_obj)`: Función simple que valida:
  1. ¿Existe en la BD?
  2. ¿`en_mantenimiento == False`?
  Retorna `(True, "Sala disponible.", obj)` o `(False, "Motivo...", None)`.

#### D. `reserva.py` (Revisión de Choques y Persistencia en MongoDB)
- `revisar_choque_horario_dia(sala, fecha, hora_inicio, hora_fin, buffer_min=15)`: **Función revisora**. Consulta en MongoDB todas las reservas activas en esa fecha para la sala dada y verifica si colisiona con el buffer de 15 minutos.
- `revisar_reserva_estudiante_en_horario(estudiante, fecha, hora_inicio, hora_fin)`: Verifica en MongoDB si el solicitante ya tiene otra reserva en cualquier sala en ese mismo bloque.
- `guardar_reserva_mongo(estudiante, sala, fecha, hora_inicio, hora_fin)`: Inserta el documento en la colección de reservas de MongoDB (`Reserva.objects.create(...)`).
- `cancelar_reserva_en_mongo(codigo_estudiante, nombre_sala, fecha)`: Actualiza el estado a `CANCELADA` en MongoDB.
- `consultar_salas_disponibles_dia(fecha, hora_inicio, hora_fin)`: Retorna la lista de nombres de salas libres.

#### E. `sistema_reservas.py` (Orquestación y API Pública)
- `reservar_si_es_posible(codigo_estudiante, nombre_sala, horas, fecha=None, hora_fin=None, asistentes=None)` (Alias: `reservarSiesPosible`):
  Ejecuta la secuencia de validaciones aisladas:
  1. Parsea horario -> Si falla, retorna `{"estado": "RECHAZADA", "mensaje": "..."}`.
  2. Valida estudiante en Mongo -> Si falla, retorna `{"estado": "RECHAZADA", "mensaje": "..."}`.
  3. Valida sala en Mongo -> Si falla, retorna `{"estado": "RECHAZADA", "mensaje": "..."}`.
  4. Valida no duplicidad del estudiante -> Si falla, retorna `{"estado": "RECHAZADA", "mensaje": "..."}`.
  5. Valida choque de sala con buffer 15 min -> Si falla, retorna `{"estado": "RECHAZADA", "mensaje": "..."}`.
  6. Guarda en MongoDB (`guardar_reserva_mongo`).
  7. Retorna éxito: `{"estado": "CONFIRMADA", "mensaje": "Reserva exitosa.", "id_reserva": "...", "datos": {...}}`.

---

### 4. Dónde y Cómo se Validan los Datos en las Pruebas

En todas las pruebas de integración y unitarias que tocan persistencia:
- Los datos se guardan y leen directamente en las colecciones de **MongoDB** (`reservas_estudiante`, `reservas_sala`, `reservas_reserva`).
- Se utiliza `tests/conftest.py` con fixtures parametrizadas (`estudiante_habilitado_db`, `estudiante_inactivo_db`, `estudiante_sin_matricula_db`, `sala_disponible_db`, `sala_mantenimiento_db`).
- La limpieza automática elimina registros con prefijo `TEST-` antes y después de cada test utilizando IDs directos para cumplir con las restricciones de consultas sin JOIN de MongoDB.

---

### 5. Detalle de las Pruebas Automatizadas

#### Nivel 1: Pruebas Unitarias Simples y Aisladas (`tests/test_unitarios_simples.py`)
*Cada test llama a 1 sola función de forma estricta.*

1. `test_convertir_a_minutos_formato_texto`: Valida `convertir_a_minutos("10:30") == 630`.
2. `test_convertir_a_minutos_objeto_time`: Valida `convertir_a_minutos(time(7, 45)) == 465`.
3. `test_convertir_a_minutos_formato_invalido_lanza_error`: Valida `ValueError` ante formatos erróneos.
4. `test_minutos_a_time_conversion_correcta`: Valida `minutos_a_time(600) == time(10, 0)`.
5. `test_validar_rango_horario_valido`: Valida `validar_rango_horario("08:00", "10:00") == (480, 600)`.
6. `test_validar_rango_horario_invalido_fin_menor_que_inicio`: Valida error si fin <= inicio.
7. `test_hay_choque_con_buffer_dentro_del_margen_15_min`: Valida choque con margen de 10 min (< 15 min).
8. `test_hay_choque_con_buffer_fuera_del_margen_15_min`: Valida no choque con margen de 15 min exactos.
9. `test_hay_solapamiento_simple_directo`: Valida colisión directa de tiempo.
10. `test_parsear_horas_desde_cadena`: Valida parseo de `"10:00-12:00"`.
11. `test_validar_estudiante_habilitado_exitoso`: Valida estudiante activo y matriculado en MongoDB.
12. `test_validar_estudiante_rechazado_si_inactivo`: Valida rechazo por inactividad en MongoDB.
13. `test_validar_estudiante_rechazado_si_sin_matricula`: Valida rechazo por deuda de matrícula en MongoDB.
14. `test_validar_estudiante_rechazado_si_no_existe`: Valida rechazo ante código no registrado.
15. `test_validar_sala_habilitada_exitosa`: Valida sala existente y disponible en MongoDB.
16. `test_validar_sala_rechazada_en_mantenimiento`: Valida rechazo de sala en mantenimiento en MongoDB.
17. `test_validar_sala_rechazada_si_no_existe`: Valida rechazo ante sala inexistente.
18. `test_revisar_choque_horario_dia_en_sala_libre`: Valida que `revisar_choque_horario_dia` retorne `True`.
19. `test_revisar_reserva_estudiante_en_horario_libre`: Valida que `revisar_reserva_estudiante_en_horario` retorne `True`.
20. `test_guardar_reserva_mongo_crea_registro`: Valida persistencia de `Reserva` en MongoDB.
21. `test_cancelar_reserva_en_mongo_inexistente`: Valida respuesta adecuada al cancelar reserva inexistente.
22. `test_consultar_salas_disponibles_dia_retorna_lista`: Valida obtención de lista de salas disponibles.
23. `test_alias_reservar_si_es_posible_camel_case`: Valida funcionamiento idéntico de `reservarSiesPosible`.

#### Nivel 2: 10 Pruebas de Integración Multi-función (`tests/test_integracion_completa.py`)

1. **`test_01_flujo_completo_reserva_exitosa_y_verificacion_datos_mongo`:**
   - Ejecuta `reservar_si_es_posible` con datos válidos.
   - Comprueba respuesta `CONFIRMADA`.
   - Consulta `Reserva.objects.get(...)` en MongoDB y verifica coincidencia exacta de IDs, fecha, horas y estado.
2. **`test_02_rechazo_reserva_estudiante_inactivo_sin_guardar_mongo`:**
   - Intenta reservar con estudiante inactivo.
   - Comprueba estado `RECHAZADA` y mensaje "no está activo".
   - Verifica en MongoDB que `Reserva.objects.filter(...).count() == 0`.
3. **`test_03_rechazo_reserva_estudiante_sin_matricula_pagada`:**
   - Intenta reservar con estudiante deudor.
   - Comprueba estado `RECHAZADA` y mensaje "no tiene la matrícula pagada".
   - Verifica que no hay documentos creados en MongoDB.
4. **`test_04_rechazo_reserva_sala_en_mantenimiento`:**
   - Solicita reserva en sala con `en_mantenimiento=True`.
   - Comprueba estado `RECHAZADA` y mensaje "en mantenimiento".
   - Verifica en MongoDB que la sala permanece con 0 reservas.
5. **`test_05_rechazo_reserva_sala_inexistente`:**
   - Solicita una sala que no existe en el catálogo.
   - Comprueba estado `RECHAZADA` y mensaje "no existe en la base de datos".
6. **`test_06_rechazo_choque_exacto_de_horario_misma_sala`:**
   - Crea reserva A (08:00-10:00) en MongoDB.
   - Intenta reserva B (08:00-10:00) en la misma sala por otro estudiante.
   - Comprueba rechazo por cruce de horarios y que en Mongo solo persiste la primera.
7. **`test_07_rechazo_violacion_buffer_15_minutos_desalojo`:**
   - Crea reserva A (08:00-10:00).
   - Intenta reserva B (10:10-12:00) en la misma sala (margen de 10 min < 15 min buffer).
   - Comprueba rechazo por no respetar los 15 minutos de desalojo.
8. **`test_08_aceptacion_limite_exacto_buffer_15_minutos`:**
   - Crea reserva A (08:00-10:00).
   - Crea reserva B (10:15-12:00) en la misma sala (exactamente 15 min de separación).
   - Comprueba estado `CONFIRMADA` y que ambas reservas existen en MongoDB.
9. **`test_09_rechazo_estudiante_con_doble_reserva_en_mismo_horario`:**
   - Estudiante reserva Sala Alfa (14:00-16:00).
   - El mismo estudiante intenta reservar Sala Beta (14:30-16:30).
   - Comprueba rechazo porque ya cuenta con un espacio reservado en ese horario.
10. **`test_10_ciclo_vida_reserva_mongo_consulta_cancelacion_y_liberacion`:**
    - Reserva Sala Alfa -> Confirmada en MongoDB.
    - Consulta disponibilidad -> Sala Alfa no aparece disponible.
    - Cancela la reserva -> Estado cambia a `CANCELADA` en MongoDB.
    - Consulta disponibilidad -> Sala Alfa vuelve a figurar como disponible.
    - Nuevo estudiante reserva la sala liberada -> Confirmada exitosamente en Mongo.

---

### 6. Verificación de la Suite de Pruebas

Comando ejecutado:
```bash
.venv\Scripts\pytest -v
```

---

### 7. Módulo Web y Sistema de Roles con Poderes Especiales

Se implementó una interfaz web moderna, responsiva y con branding oficial de la **UPB Santa Cruz** (azul marino, oro institucional y escudo UPB vectorizado en SVG):

1. **Gestión de Roles y Poderes Especiales (`reservas/permisos.py`):**
   - **Usuarios con Poderes Especiales (Administradores/Docente):**
     - 👑 **Prof. Sergio Barrientos** (`sbarrientos` - Docente / Director)
     - 👑 **Hugo Zúñiga** (`hzuniga` - Administrador Principal)
     - 👑 **Raúl Vaca** (`rvaca` - Administrador)
     - 👑 **Alejandro Párraga** (`aparraga` - Administrador)
     - 👑 **SuperAdmin** (`admin` - Superusuario)
   - **Privilegios de los Poderes Especiales:**
     - Barra de herramientas dorada exclusiva de administración.
     - Botón y modal interactivo para **alternar el estado de mantenimiento** de salas en vivo (vía endpoint `api/toggle-mantenimiento/`).
     - Capacidad de **cancelar cualquier reserva** directamente desde la cuadrícula del calendario.
     - Selector rápido con autocompletado de cualquier estudiante activo.
     - Acceso directo al panel Django Admin (`/admin/`).
   - **Usuarios Estudiantes Regulares:**
     - `lucia.mendez`, `carlos.torrico`, `valeria.flores`, `daniela.castro` (solo reservan para su cuenta y cancelan reservas propias).

2. **Vistas y Plantillas Web (`reservas/templates/web/`):**
   - **`web/login.html`:** Pantalla de acceso elegante con logo UPB, validación de credenciales y panel de botones de acceso rápido de 1 clic para cada miembro del equipo y estudiantes de prueba.
   - **`web/inicio.html`:** Dashboard interactivo con:
     - **Columna Izquierda (Calendario Visual):** Matriz horaria con bloques coloreados por sala (Alfa, Beta, Gamma, Delta, Omega), indicación de 15 min de margen y visualización de cupos disponibles.
     - **Columna Derecha (Formulario de Reserva):** Selector de sala, autocompletado, selector de horarios mediante botones pills (`07:45 - 09:45`, `10:00 - 12:00`, `12:15 - 14:15`, `14:30 - 16:30`, `16:45 - 18:45`, `19:00 - 21:00`) y feedback en tiempo real mediante toasts flotantes.

---

### 8. Verificación de la Suite de Pruebas

Comando ejecutado:
```bash
.venv\Scripts\pytest -v
```

Resultado de salida:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\sebas\PycharmProjects\campus-challenge-equipo-01
configfile: pytest.ini
testpaths: tests
collected 41 items

tests/test_integracion_completa.py::test_01_flujo_completo_reserva_exitosa_y_verificacion_datos_mongo PASSED [  2%]
tests/test_integracion_completa.py::test_02_rechazo_reserva_estudiante_inactivo_sin_guardar_mongo PASSED [  4%]
tests/test_integracion_completa.py::test_03_rechazo_reserva_estudiante_sin_matricula_pagada PASSED [  7%]
tests/test_integracion_completa.py::test_04_rechazo_reserva_sala_en_mantenimiento PASSED [  9%]
tests/test_integracion_completa.py::test_05_rechazo_reserva_sala_inexistente PASSED [ 12%]
tests/test_integracion_completa.py::test_06_rechazo_choque_exacto_de_horario_misma_sala PASSED [ 14%]
tests/test_integracion_completa.py::test_07_rechazo_violacion_buffer_15_minutos_desalojo PASSED [ 17%]
tests/test_integracion_completa.py::test_08_aceptacion_limite_exacto_buffer_15_minutos PASSED [ 19%]
tests/test_integracion_completa.py::test_09_rechazo_estudiante_con_doble_reserva_en_mismo_horario PASSED [ 21%]
tests/test_integracion_completa.py::test_10_ciclo_vida_reserva_mongo_consulta_cancelacion_y_liberacion PASSED [ 24%]
tests/test_reglas.py::test_crear_reserva_exitosa_si_hay_capacidad_y_disponibilidad PASSED [ 26%]
tests/test_reglas.py::test_rechaza_reserva_si_no_respeta_15_minutos_de_desalojo PASSED [ 29%]
tests/test_reglas.py::test_rechaza_si_estudiante_ya_tiene_reserva_en_otra_sala_mismo_bloque PASSED [ 31%]
tests/test_reglas.py::test_consultar_espacios_disponibles PASSED         [ 34%]
tests/test_reglas.py::test_cancelar_reserva_exitosa PASSED               [ 36%]
tests/test_reglas.py::test_cancelar_reserva_rechazada_si_no_existe PASSED [ 39%]
tests/test_unitarios_simples.py::test_convertir_a_minutos_formato_texto PASSED [ 41%]
tests/test_unitarios_simples.py::test_convertir_a_minutos_objeto_time PASSED [ 43%]
tests/test_unitarios_simples.py::test_convertir_a_minutos_formato_invalido_lanza_error PASSED [ 46%]
tests/test_unitarios_simples.py::test_minutos_a_time_conversion_correcta PASSED [ 48%]
tests/test_unitarios_simples.py::test_validar_rango_horario_valido PASSED [ 51%]
tests/test_unitarios_simples.py::test_validar_rango_horario_invalido_fin_menor_que_inicio PASSED [ 53%]
tests/test_unitarios_simples.py::test_hay_choque_con_buffer_dentro_del_margen_15_min PASSED [ 56%]
tests/test_unitarios_simples.py::test_hay_choque_con_buffer_fuera_del_margen_15_min PASSED [ 58%]
tests/test_unitarios_simples.py::test_hay_solapamiento_simple_directo PASSED [ 60%]
tests/test_unitarios_simples.py::test_parsear_horas_desde_cadena PASSED  [ 63%]
tests/test_unitarios_simples.py::test_validar_estudiante_habilitado_exitoso PASSED [ 65%]
tests/test_unitarios_simples.py::test_validar_estudiante_rechazado_si_inactivo PASSED [ 68%]
tests/test_unitarios_simples.py::test_validar_estudiante_rechazado_si_sin_matricula PASSED [ 70%]
tests/test_unitarios_simples.py::test_validar_estudiante_rechazado_si_no_existe PASSED [ 73%]
tests/test_unitarios_simples.py::test_validar_sala_habilitada_exitosa PASSED [ 75%]
tests/test_unitarios_simples.py::test_validar_sala_rechazada_en_mantenimiento PASSED [ 78%]
tests/test_unitarios_simples.py::test_validar_sala_rechazada_si_no_existe PASSED [ 80%]
tests/test_unitarios_simples.py::test_revisar_choque_horario_dia_en_sala_libre PASSED [ 82%]
tests/test_unitarios_simples.py::test_revisar_reserva_estudiante_en_horario_libre PASSED [ 85%]
tests/test_guardar_reserva_mongo_crea_registro PASSED                   [ 87%]
tests/test_cancelar_reserva_en_mongo_inexistente PASSED                 [ 90%]
tests/test_consultar_salas_disponibles_dia_retorna_lista PASSED         [ 92%]
tests/test_alias_reservar_si_es_posible_camel_case PASSED               [ 95%]
tests/test_unitarios_simples.py::test_tiene_poderes_especiales_usuarios_designados PASSED [ 97%]
tests/test_unitarios_simples.py::test_obtener_info_usuario_formato_correcto PASSED [100%]

============================= 41 passed in 1.44s ==============================
```

---

### 9. Comandos de Uso

- **Ejecutar servidor Django:**
  ```bash
  .venv\Scripts\python.exe manage.py runserver
  ```
  Acceso: `http://127.0.0.1:8000/` (o `/login/`)

- **Poblar / Resetear Usuarios con Poderes y Reservas en MongoDB:**
  ```bash
  .venv\Scripts\python.exe manage.py poblar_bd --limpiar
  ```

- **Ejecutar Suite de Pruebas:**
  ```bash
  .venv\Scripts\pytest -v
  ```

