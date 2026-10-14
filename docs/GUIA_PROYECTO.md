# 📚 Guía Completa del Proyecto — Reservas UPB

---

## 🗄️ ¿Dónde está la "base de datos artificial" que le pasaste a Mongo?

Los datos de prueba que ves en MongoDB vienen de **DOS lugares distintos**:

### 1. `datos/padron_upb.json` — El padrón simulado de la universidad (SOLO LECTURA)

Este es el archivo que **TÚ subiste** al proyecto. Es una simulación del padrón real de la UPB con 19 personas ficticias:

```
datos/
└── padron_upb.json   ← AQUÍ están las personas con nombre, código, correo, rol y nivel
```

**Qué contiene:**
| Código | Nombre | Rol | Nivel | Matrícula |
|---|---|---|---|---|
| 20011 | Sergio Barrientos | docente | — | vigente |
| 20012 | Hugo Zúñiga | admin | — | vigente |
| 20013 | Raúl Vaca | admin | — | vigente |
| 20014 | Alejandro Párraga | admin | — | vigente |
| 94210 | Lucía Méndez | estudiante | pregrado | vigente |
| 94377 | Carlos Torrico | estudiante | pregrado | NO vigente |
| 93815 | Valeria Flores | estudiante | pregrado | vigente |
| 92604 | Sebastián Gutiérrez | estudiante | pregrado | vigente (inactivo) |
| 95048 | Daniela Castro | estudiante | pregrado | vigente |
| 93192 | Andrés Romero | estudiante | pregrado | vigente |
| 94731 | Fernanda Salinas | estudiante | pregrado | vigente |
| 92956 | Diego Suárez | estudiante | pregrado | vigente (SIN CUENTA demo) |
| 95513 | Camila Rojas | estudiante | pregrado | vigente |
| 93340 | Mateo Vargas | estudiante | pregrado | vigente |
| 81247 | Patricia Aguilera | estudiante | postgrado | vigente |
| 81692 | Marcelo Ibáñez | estudiante | postgrado | vigente |
| 80435 | Rosario Calle | estudiante | postgrado | NO vigente |
| 72118 | Elena Montaño | estudiante | doctorado | vigente |
| 72593 | Gonzalo Peredo | estudiante | doctorado | vigente (SIN CUENTA demo) |

> 💡 **Este archivo se consulta SOLO al registrarse.** Una vez que la persona tiene cuenta en el sistema, el padrón ya no interviene.

### 2. `reservas/management/commands/poblar_bd.py` — El script que llena MongoDB

Este script es el que **ejecutas con `python manage.py poblar_bd`** y es quien:
- Lee el padrón y crea las cuentas de demo en Django
- Crea las **salas** en MongoDB
- Genera **reservas de ejemplo** aleatorias para el calendario

**Las salas que crea:**
| Sala | Exclusiva de | Estado |
|---|---|---|
| Sala A | Postgrado y Doctorado | Habilitada |
| Sala B | Pregrado | Habilitada |
| Sala C | Pregrado | Habilitada |
| Sala D | Pregrado | Habilitada |
| Sala E | Postgrado y Doctorado | Habilitada |
| Sala F | Pregrado | Habilitada |
| Sala H | Pregrado | **EN MANTENIMIENTO** |
| Sala J | Pregrado | Habilitada |

---

## 🔄 ¿Por qué hay dos migraciones (0001 y 0002)?

> **Respuesta corta:** Sí, debería estar todo en una sola, y en MongoDB **las migraciones son casi decorativas**. Pero tienen una historia.

### `0001_initial.py` — La migración original
Creada automáticamente por Django (`makemigrations`) el **01/10/2026**. Contiene los 3 modelos base:
- `Estudiante` (código, nombres, apellidos, esta_activo, matricula_pagada)
- `Sala` (nombre, en_mantenimiento)
- `Reserva` (FK a estudiante y sala, fecha, horas, estado)

### `0002_nivel_estudiante_y_sala_exclusiva.py` — La migración que agregó campos nuevos
Esta fue escrita **a mano** después, cuando el equipo (Raúl) añadió dos campos nuevos para las reglas de niveles académicos:
- `Estudiante.nivel` — para saber si es pregrado, postgrado o doctorado
- `Sala.exclusiva_posgrado` — para marcar las salas A y E

### ¿Hay que unificarlas?

**Con MongoDB NO es necesario.** A diferencia de SQL (donde las migraciones crean tablas físicas), MongoDB crea las colecciones de forma dinámica. Las migraciones en `django-mongodb-backend` son un registro para que Django sepa el estado del esquema, pero **no crean ni modifican colecciones reales** en Mongo.

Si quisieras limpiarlas y dejar solo una, el proceso sería:
```powershell
# 1. Borrar las migraciones viejas
Remove-Item reservas/migrations/0001_initial.py
Remove-Item reservas/migrations/0002_nivel_estudiante_y_sala_exclusiva.py

# 2. Generar una nueva migración limpia (con todos los campos actuales)
python manage.py makemigrations

# 3. Aplicarla
python manage.py migrate
```
Pero **solo tiene sentido hacerlo si reseteas la BD también**, porque Mongo no necesita esa migración para funcionar.

---

## 📝 ¿Qué hace cada archivo `.md` del proyecto?

### En la raíz del proyecto:
| Archivo | Qué es |
|---|---|
| `README.md` | **El más importante.** Describe el proyecto completo, arquitectura, qué hace hoy, cómo instalar, tabla de credenciales de demo, reglas de negocio aprobadas por el docente y bitácora de decisiones |
| `REFACTORIZACION_Y_PRUEBAS.md` | Documento técnico de la refactorización de `proyecto/clases/`. Explica función por función lo que hace cada módulo, las 41+ pruebas y la arquitectura limpia |
| `restricciones.md` | Restricciones del proyecto (reglas que el equipo se impuso para mantener el código ordenado) |

### En `docs/`:
| Archivo | Qué es |
|---|---|
| `SETUP.md` | Guía detallada de instalación: MongoDB Atlas, Docker y local; con 3 formas de tener Mongo funcionando |
| `sesion04.md` | Documento de la **sesión 4 de clase**: backlog, objetivo del sprint, reglas acordadas con el docente (buffer 15 min, una sala por bloque, etc.) |
| `sesion-06-requisitos.md` | Documento de la **sesión 6**: requisitos aprobados por el docente (RES-01 a RES-08), funcionales y no funcionales |
| `sesion-07-modelos.md` | Documento de la **sesión 7**: modelos de flujo para "modificar una reserva" |
| `sesion-08-09-plan.md` | Plan del **incremento de las sesiones 8 y 9**: modificar reserva, pantalla, backend, pruebas |
| `TRAZABILIDAD_PRUEBAS.md` | Tabla que cruza cada prueba con su requisito (RES-HU-01) y caso de uso |
| `AUTENTICACION.md` | Describe el sistema de autenticación (padrón → registro → login) |
| `CONFIGURACION_DJANGO.md` | Configuración de Django con MongoDB |
| `BRECHA_REQUISITOS.md` | Qué está implementado vs. qué falta de los requisitos oficiales |
| `REPARTO_TAREAS.md` | Quién hizo qué en el equipo |

---

## ✏️ ¿Cómo edito / reemplazo los datos de la base de datos?

### Opción A — Editar el padrón y resetear (LA QUE TE RECOMIENDO)

Esto es exactamente lo que quieres hacer: cambiar nombres, IDs, etc.

**Paso 1: Editar `datos/padron_upb.json`**

Abre el archivo y modifica las personas. La estructura de cada persona es:
```json
{
  "codigo": "94210",          ← código de 5 dígitos (es el username de login)
  "nombres": "Lucía",
  "apellidos": "Méndez",
  "email": "lucia.mendez@est.upb.example",   ← se usa para el login
  "rol": "estudiante",        ← "estudiante", "docente" o "admin"
  "nivel": "pregrado",        ← "pregrado", "postgrado", "doctorado" o null
  "carrera": "ISC",           ← "ISC", "LIC", "MSC", "PHD" o null
  "activo": true,             ← si puede registrarse
  "matricula_vigente": true   ← si puede reservar
}
```

**Paso 2: Resetear y re-poblar MongoDB**
```powershell
# Activa el entorno virtual primero
.venv\Scripts\Activate.ps1

# Limpia TODO (reservas, estudiantes, salas y cuentas) y vuelve a crear
python manage.py poblar_bd --limpiar
```

¡Listo! La BD queda completamente nueva con tus datos actualizados.

---

### Opción B — Editar directamente en la BD (sin resetear)

Si solo quieres cambiar un dato puntual sin borrar todo:

**Desde el panel `/admin/` de Django:**
1. Levanta el servidor: `python manage.py runserver`
2. Abre `http://127.0.0.1:8000/admin/`
3. Login: usuario `admin`, contraseña `password`
4. Edita Estudiantes, Salas o Reservas directamente

**Desde MongoDB Compass (interfaz visual):**
- Conecta a tu URI de Mongo (la que está en `.env`)
- Base de datos: `reservas_upb`
- Colecciones: `reservas_estudiante`, `reservas_sala`, `reservas_reserva`

**Desde la consola de Django (para cambios masivos):**
```powershell
python manage.py shell
```
```python
from reservas.models import Estudiante, Sala, Reserva

# Cambiar nombre de un estudiante
e = Estudiante.objects.get(codigo_estudiante="94210")
e.nombres = "María Lucia"
e.save()

# Ver todas las salas
for s in Sala.objects.all():
    print(s.nombre, "— Mantenimiento:", s.en_mantenimiento)

# Borrar todas las reservas de un día
import datetime
Reserva.objects.filter(fecha=datetime.date(2026, 10, 7)).delete()
```

---

## 📅 Cronología de lo que se hizo y cuándo

| Fecha | Qué se hizo |
|---|---|
| **01/10/2026** | Sesión de inicio: configuración de Django + MongoDB, modelos base (Estudiante, Sala, Reserva), migración `0001_initial`, comando `poblar_bd` con datos de prueba iniciales |
| **01/10/2026** | Sesión 6 con el docente: aprobación de reglas de negocio (buffer 15 min, una sala por bloque, etc.) |
| **02/10/2026** | Refactorización de `proyecto/clases/` en módulos aislados, sistema de pruebas con pytest (39 tests), función `reservar_si_es_posible` |
| **02/10/2026** | Implementación de vistas web: login con redirección por rol, vista de estudiante con calendario, panel de administrador |
| **02/10/2026** | Templates `web/login.html`, `web/inicio.html`, `web/admin_dashboard.html` con diseño glassmorphism y logo UPB |
| **02/10/2026** | Sistema de permisos especiales (`reservas/permisos.py`): Sergio Barrientos, Hugo Zúñiga, Raúl Vaca, Alejandro Párraga |
| **02/10/2026 (hoy)** | **Limpieza y refactorización de código:** traducción de todos los comentarios al español, eliminación de archivos innecesarios (`reservas/tests.py` vacío, carpeta `templates/reservas` vacía), mejoras en docstrings y prolijo en todos los archivos Python |
| **07/10/2026** | Incremento sesiones 8-9: sistema de registro por padrón (`/registro/`), niveles académicos (`reservas/niveles.py`), ventanas de anticipación para reservar (`reservas/ventanas.py`), migración `0002`, Tailwind CSS mobile-first, nueva estructura de salas (A-J), más pruebas |

---

## 🚀 Referencia rápida: comandos más usados

```powershell
# Levantar el servidor
python manage.py runserver

# Resetear BD y re-poblar con los datos del padrón
python manage.py poblar_bd --limpiar

# Solo poblar (no borra lo que hay)
python manage.py poblar_bd

# Correr todas las pruebas
python -m pytest -q

# Abrir la consola de Django (para editar datos manualmente)
python manage.py shell

# Crear una nueva migración (si cambias models.py)
python manage.py makemigrations
python manage.py migrate
```

---

## 🔑 Credenciales de demo (contraseña siempre: `password`)

| Persona | Código | Correo | Qué ve |
|---|---|---|---|
| Sergio Barrientos (docente) | 20011 | sergio.barrientos@upb.example | Panel de Admin |
| Hugo Zúñiga (tú) | 20012 | hugo.zuniga@upb.example | Panel de Admin |
| Raúl Vaca | 20013 | raul.vaca@upb.example | Panel de Admin |
| Alejandro Párraga | 20014 | alejandro.parraga@upb.example | Panel de Admin |
| Lucía Méndez (pregrado) | 94210 | lucia.mendez@est.upb.example | Portal Estudiante |
| Patricia Aguilera (postgrado) | 81247 | patricia.aguilera@est.upb.example | Portal Estudiante (solo salas A y E) |
| Elena Montaño (doctorado) | 72118 | elena.montano@est.upb.example | Portal Estudiante (solo salas A y E) |
| Superadmin Django | — | — | Solo `/admin/` (usuario: `admin`) |
