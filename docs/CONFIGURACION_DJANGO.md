# Qué hace cada archivo de `reservas_upb/`

Guía didáctica de la carpeta de configuración central del proyecto Django, y cómo se conecta todo con MongoDB. Pensada para quien no haya tocado Django antes.

## Antes de empezar: proyecto vs. app

En Django, un proyecto tiene **una carpeta de configuración general** (`reservas_upb/`) y **una o más "apps"** (en este caso, `reservas/`, donde viven los modelos, vistas, templates, etc.). `reservas_upb/` no hace trabajo por sí sola — es el "centro de mando" que le dice a Django cómo arrancar, a qué base de datos conectarse, y qué URLs existen. Todo el trabajo real (leer/guardar datos, validar reglas) pasa en `reservas/`.

## `settings.py` — el archivo más importante, explicado por bloques

```python
from dotenv import load_dotenv
load_dotenv()
```
Esto lee el archivo `.env` (que nunca se sube a GitHub) y mete sus valores como si fueran variables de entorno del sistema operativo. Ahí vive la dirección de MongoDB (`MONGO_URI`) y el nombre de la base (`MONGO_DB_NAME`). Sin esta línea, Django no sabría dónde está el Mongo de cada quien.

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```
Calcula automáticamente la ruta de la carpeta raíz del proyecto (donde está `manage.py`), para que el resto del archivo pueda referirse a subcarpetas sin escribir rutas fijas tipo `C:\Users\...`.

```python
SECRET_KEY = 'django-insecure-...'
```
Una clave que Django usa internamente para firmar cosas (sesiones, tokens de formularios contra ataques CSRF, etc.). En producción esto también debería ir en `.env`, no quedar escrito en el código — pero para un proyecto universitario local no es crítico.

```python
DEBUG = True
```
Modo desarrollo: si algo falla, Django muestra la página de error detallada (como la que vimos cuando faltaba un template). En producción esto se pone en `False`, porque mostrar ese detalle a cualquier visitante sería un riesgo de seguridad.

```python
INSTALLED_APPS = [
    'django_mongodb_backend',
    'reservas.apps.MongoAdminConfig',
    'reservas.apps.MongoAuthConfig',
    'reservas.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tailwind_cli',
    'reservas.apps.ReservasConfig',
]
```
La lista de "piezas activas" del proyecto. Nada de lo que no esté aquí existe para Django:
- **`django_mongodb_backend`**: el traductor que le enseña a Django a hablar con MongoDB en vez de con una base SQL.
- **`MongoAdminConfig`, `MongoAuthConfig`, `MongoContentTypesConfig`**: versiones "adaptadas a Mongo" de tres piezas que Django trae de fábrica (el panel `/admin/`, el sistema de login/permisos, y un sistema interno de "tipos de contenido"). Se adaptaron porque, por defecto, esas piezas asumen que los IDs son números (como en SQL), y en Mongo son `ObjectId`.
- **`django.contrib.sessions`**: maneja las sesiones — permite que, después del login, Django "recuerde" quién eres en cada clic siguiente (guarda una cookie en el navegador con un identificador, y en el servidor guarda a quién pertenece).
- **`django.contrib.messages`**: el sistema de mensajitos tipo "Reserva confirmada" o "esta sala es solo para docentes" que aparece después de un formulario.
- **`django.contrib.staticfiles`**: organiza los archivos estáticos (CSS, imágenes, JS) para servirlos correctamente.
- **`django_tailwind_cli`**: compila Tailwind CSS (integrado por el equipo para el frontend).
- **`reservas.apps.ReservasConfig`**: la app real del proyecto, donde están `Sala`, `Reserva`, `Usuario`, etc.

```python
MIDDLEWARE = [...]
```
Una fila de "filtros" por los que pasa *cada* petición antes de llegar a una vista, y cada respuesta antes de salir de vuelta al navegador — en orden. Por ejemplo, `AuthenticationMiddleware` revisa la cookie de sesión y "adjunta" al usuario como `request.user` en cada vista; `CsrfViewMiddleware` protege los formularios contra ataques donde una página externa intenta enviar formularios en nombre de otro.

```python
ROOT_URLCONF = 'reservas_upb.urls'
```
Le dice a Django: "el mapa de URLs del sitio está en `reservas_upb/urls.py`". Sin esto, Django no sabría qué archivo mirar cuando llega una petición.

```python
TEMPLATES = [...]
```
Configura el motor que convierte los archivos `.html` (con `{% %}` y `{{ }}`) en HTML final. `APP_DIRS: True` significa "busca templates automáticamente dentro de la carpeta `templates/` de cada app" — por eso los archivos en `reservas/templates/reservas/` se encuentran solos, sin registrarlos a mano.

```python
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.environ.get("MONGO_URI"),
        "NAME": os.environ.get("MONGO_DB_NAME"),
    }
}
```
**Aquí está el corazón de la conexión con MongoDB.** `ENGINE` le dice a Django "usa el traductor de Mongo, no el de PostgreSQL/MySQL/SQLite". `HOST` y `NAME` vienen del `.env`. Cada vez que se escribe algo como `Sala.objects.all()` en cualquier vista, Django mira esta configuración para saber a qué base conectarse y cómo "hablarle".

```python
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
```
Le dice a Django "cuando crees el campo `id` automático de un modelo nuevo, usa `ObjectIdAutoField`" (el tipo de identificador que usa Mongo), en vez del `AutoField` numérico de siempre.

```python
AUTH_USER_MODEL = 'reservas.Usuario'
```
Le dice a Django "el modelo de usuario del sistema no es el `User` genérico de fábrica — es el modelo `Usuario` propio (`reservas/models.py`), el que tiene `email`, `codigo` y `rol`". Esta línea hace que todo el sistema de login (incluyendo `/admin/`, los formularios, `request.user`, etc.) use ese modelo en vez del de Django.

```python
AUTHENTICATION_BACKENDS = [
    'reservas.auth_backends.PadronBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```
Cuando alguien envía el formulario de login, Django prueba estos "verificadores" en orden. Primero `PadronBackend` (revisa el padrón institucional simulado). Si dice "no lo conozco", Django prueba `ModelBackend` (el de Django: revisa contraseña normal) — así los 2 superusuarios entran con clave y los estudiantes/docentes entran con código.

## `urls.py` — el mapa de direcciones

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(...), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('reservar/', views.crear_reserva, name='crear_reserva'),
]
```
Una lista de "si la URL es X, llama a la función Y". Django la revisa **de arriba hacia abajo** y usa la primera que coincida — por eso el login personalizado está antes del `include` genérico, para que gane el propio. Cuando alguien entra a `127.0.0.1:8000/reservar/`, Django busca en esta lista, encuentra `path('reservar/', views.crear_reserva, ...)`, y ejecuta la función `crear_reserva` de `reservas/views.py` — que es la que finalmente habla con el modelo `Reserva` y, a través de él, con MongoDB.

## `wsgi.py` y `asgi.py` — el "enchufe" para encender el servidor

```python
application = get_wsgi_application()
```
Cuando se corre `python manage.py runserver`, por dentro Django arranca un mini-servidor que usa este archivo como punto de entrada: "aquí está la aplicación completa, lista para recibir peticiones HTTP". `wsgi.py` es la forma clásica (una petición a la vez, de forma ordenada); `asgi.py` es la versión moderna que además soporta cosas como WebSockets. Hoy se usa WSGI sin notarlo — Django genera ambos por si algún día se necesita el otro. No hace falta tocarlos.

## `__init__.py`

Vacío. Solo le dice a Python "esta carpeta es un paquete". Sin contenido, sin lógica.

## El viaje completo, uniendo todo

1. Se escribe `127.0.0.1:8000/reservar/` en el navegador.
2. El servidor (encendido vía `wsgi.py`) recibe la petición.
3. Pasa por el `MIDDLEWARE` (sesión, autenticación, CSRF...).
4. Django mira `ROOT_URLCONF` → va a `urls.py` → encuentra `reservar/` → llama a `crear_reserva` en `views.py`.
5. Esa vista usa el modelo `Reserva` (`models.py`).
6. El modelo, para guardar o consultar, usa la configuración de `DATABASES` en `settings.py` → ahí está `ENGINE: django_mongodb_backend` → ese paquete traduce la operación a una instrucción real de MongoDB.
7. MongoDB responde, Django arma el resultado, lo mete en un template (`crear_reserva.html`), y el HTML final vuelve al navegador.

`reservas_upb/` no "hace" nada operativo por sí sola — conecta los cables: le dice a Django dónde está el mapa de URLs, con qué base de datos hablar, y qué modelo de usuario usar.
