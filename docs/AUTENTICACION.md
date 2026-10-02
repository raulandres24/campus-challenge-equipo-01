# Login institucional y roles de usuario

Este documento explica el sistema de login que reemplaza al login simple de Django (usuario/contraseña genéricos) y responde, de forma simulada por ahora, la pregunta pendiente de `docs/sesion-06-requisitos.md` (RES-RF-05): *"¿Cómo sabe el sistema si la matrícula está al día?"*

## La idea

En vez de guardar una contraseña para cada estudiante, el sistema verifica **en el momento del login** que el correo institucional y el código existan en el padrón de la universidad y que la persona esté activa (matrícula al día). Si todo coincide, el sistema le crea su cuenta local automáticamente — nadie necesita estar precargado de antemano.

Los 2 superusuarios (jefe de carrera, encargado de salas de estudio) son la excepción: ellos sí tienen una contraseña normal, porque no son parte del padrón de estudiantes/docentes.

## Por qué está "simulado" por ahora

Todavía no tenemos acceso a un endpoint real de la UPB para consultar esto. Para no bloquear el resto del proyecto, construimos una copia local del padrón (`PadronPersona`, administrable desde `/admin/`) que cumple el mismo papel mientras tanto. El día que la universidad entregue un endpoint real, **el único archivo que hay que cambiar es `reservas/padron.py`** — el resto (login, roles, creación de cuentas) sigue funcionando igual, porque todo depende únicamente de lo que esa función devuelve.

## Las piezas, archivo por archivo

### `reservas/models.py` — `Usuario`

Reemplaza al `User` por defecto de Django. En vez de `username`, usa `email` para iniciar sesión (`USERNAME_FIELD = "email"`), y agrega:
- `codigo`: el código institucional.
- `rol`: uno de `ESTUDIANTE`, `DOCENTE`, `JEFE_CARRERA`, `ENCARGADO_SALAS`.

### `reservas/models.py` — `PadronPersona`

La copia simulada del padrón de la universidad: correo, código, nombre, rol y `matricula_vigente` (si está activo o no). Se llena desde `/admin/` o con el comando `crear_cuentas_demo`.

### `reservas/padron.py` — `verificar_en_padron(email, codigo)`

La función que "pregunta a la universidad". Hoy consulta `PadronPersona`; el día de mañana haría una petición HTTP real. Devuelve los datos de la persona si existe y está activa, o `None` si no.

### `reservas/auth_backends.py` — `PadronBackend`

Esto es lo que Django ejecuta cuando alguien envía el formulario de login. Dos backends están configurados en `settings.py`, en orden:

1. **`PadronBackend`**: llama a `verificar_en_padron`. Si la persona existe y está activa, busca (o crea, si es la primera vez) su cuenta local `Usuario` y la devuelve — login exitoso. Si no, devuelve `None`.
2. **`ModelBackend`** (el de Django): Django lo intenta automáticamente cuando el primero devuelve `None`. Es el que valida la contraseña normal de los 2 superusuarios.

Así, un mismo formulario de login sirve para los tres casos (estudiante, docente, administrador) sin que el usuario note la diferencia.

### `reservas/forms.py` — `LoginPadronForm`

Solo cambia las etiquetas del formulario de Django ("Correo institucional" y "Código / Contraseña") para que digan lo que realmente se pide. Por dentro sigue siendo el mismo mecanismo de siempre.

### `reservas/management/commands/crear_cuentas_demo.py`

Comando (`python manage.py crear_cuentas_demo`) que crea los 2 superusuarios y algunos registros de prueba en el padrón simulado — incluyendo uno inactivo, para comprobar que el sistema lo rechaza.

## Flujo completo de un login de estudiante

1. El estudiante escribe su correo y su código en `/accounts/login/`.
2. Django llama a `PadronBackend.authenticate(email, codigo)`.
3. `PadronBackend` llama a `verificar_en_padron(email, codigo)`.
4. Si el padrón dice que existe y está activo: se busca su `Usuario` local; si no existe todavía, se crea en ese momento con los datos del padrón (nombre, código, rol).
5. Django inicia la sesión con ese `Usuario` y lo redirige a `/` (horarios).
6. Si el padrón no lo reconoce o aparece inactivo, el login se rechaza con el mensaje de error estándar de Django.

## Qué falta (fuera de alcance de este incremento)

- Conectar `verificar_en_padron` a un endpoint real de la UPB cuando exista.
- Frontend con diseño UPB (pendiente, según lo acordado).
- Reglas de reserva específicas por rol (ej. si un docente puede reservar distinto que un estudiante) — hoy todos los roles pueden ver y crear reservas igual.
