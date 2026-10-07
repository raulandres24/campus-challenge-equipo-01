# Guía de instalación — Reserva de Salas UPB (Django + MongoDB)

Guía corta para dejar el proyecto corriendo en una máquina nueva (Windows y PowerShell).
Tiempo aproximado: 15 minutos con Atlas o Docker.

## 1. Requisitos

- Python 3.10 o superior y Git.
- **Una base MongoDB que funcione como replica set.** `django-mongodb-backend` lo exige. Hay tres formas de tenerla; elige una en el paso 3.

## 2. Código y dependencias

```powershell
git clone https://github.com/raulandres24/campus-challenge-equipo-01
cd campus-challenge-equipo-01
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Versiones fijas: `Django==5.2.17` y `django-mongodb-backend==5.2.4`. No las cambies sin avisar al equipo: otras versiones rompen las migraciones.

Si PowerShell no deja activar el entorno (error de "execution policy"), ejecuta una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

## 3. MongoDB: elige una opción

| Opción | Qué instalas | Ventaja | Desventaja |
|---|---|---|---|
| **A. MongoDB Atlas (recomendada para quien no conoce el proyecto)** | Nada | Ya es replica set; solo se pega una cadena de conexión | Necesita internet y una cuenta en Atlas |
| B. Docker | Docker Desktop | Un comando (`docker compose up -d`) | Docker Desktop es pesado si no lo tienes |
| C. Instalación local | MongoDB Community + mongosh | Funciona sin internet | Hay que editar `mongod.cfg` como administrador e iniciar el replica set a mano |

### Opción A — MongoDB Atlas (gratis)

1. Crea una cuenta en <https://www.mongodb.com/cloud/atlas> y un clúster **Free (M0)**.
2. En **Database Access**, crea un usuario de base de datos con contraseña.
3. En **Network Access**, agrega tu IP (botón "Add current IP address").
4. En el clúster, **Connect → Drivers**, copia la cadena `mongodb+srv://...` y reemplaza `<password>`.

> Si el equipo te comparte su clúster, te pasará la cadena por un medio privado. **Nunca** se sube a GitHub.
> Usa un `MONGO_DB_NAME` propio (por ejemplo `reservas_upb_docente`) para no mezclar datos con el equipo.

### Opción B — Docker

Con Docker Desktop abierto, en la carpeta del proyecto:

```powershell
docker compose up -d
docker compose ps
```

Espera a que `docker compose ps` muestre `healthy` (unos 20 segundos). El replica set `rs0` se crea solo.

### Opción C — MongoDB instalado en Windows

1. Instala MongoDB Community Server (<https://www.mongodb.com/try/download/community>) como servicio, y mongosh (<https://www.mongodb.com/try/download/shell>).
2. Abre `C:\Program Files\MongoDB\Server\<versión>\bin\mongod.cfg` como administrador y agrega:

   ```yaml
   replication:
     replSetName: "rs0"
   ```

3. En PowerShell como administrador: `Restart-Service MongoDB`.
4. Abre `mongosh` y ejecuta una sola vez:

   ```javascript
   rs.initiate({ _id: "rs0", members: [{ _id: 0, host: "localhost:27017" }] })
   ```

   `rs.status()` debe mostrar `PRIMARY`. Sal con `exit`.

## 4. Archivo `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

Deja **una sola** línea `MONGO_URI` sin `#`:

- Atlas: la cadena `mongodb+srv://...` del paso 3A.
- Docker o local: `MONGO_URI=mongodb://localhost:27017/?replicaSet=rs0&directConnection=true`

## 5. Crear las colecciones y los datos de demostración

```powershell
python manage.py migrate
python manage.py poblar_bd
```

- `migrate` puede avisar de "cambios no reflejados" en `admin`, `auth` y `contenttypes`. Es normal: **no** corras `makemigrations` para esas apps. Si cambias `reservas/models.py`, usa `python manage.py makemigrations reservas`.
- `poblar_bd` crea 5 salas, 10 estudiantes ficticios, reservas de ejemplo y los usuarios de prueba. `python manage.py poblar_bd --limpiar` borra los datos de negocio y los vuelve a crear.

## 6. Ejecutar

```powershell
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> (también funciona en el celular: la interfaz es mobile-first). No necesitas Node: el CSS de Tailwind ya va compilado; ver "Interfaz" en el README si cambias clases.

Hay **un solo inicio de sesión** para todos: código (5 dígitos), correo institucional y contraseña, verificados contra el padrón simulado `datos/padron_upb.json` (personas ficticias). Con `DEBUG` activo, la pantalla trae botones de demostración. La contraseña de todas las personas de demostración es `password` (**solo para desarrollo**).

| Persona | Código | Correo | Rol |
|---|---|---|---|
| Lucía | `94210` | `lucia.mendez@est.upb.example` | Estudiante de pregrado (salas B, C, D, F, H, J) |
| Patricia | `81247` | `patricia.aguilera@est.upb.example` | Estudiante de postgrado (salas A y E) |
| Elena | `72118` | `elena.montano@est.upb.example` | Estudiante de doctorado (salas A y E) |
| Sergio Barrientos | `20011` | `sergio.barrientos@upb.example` | Docente (administra) |
| Raúl, Hugo, Alejandro | `20013`, `20012`, `20014` | `raul.vaca@`, `hugo.zuniga@`, `alejandro.parraga@` + `upb.example` | Administradores |

`poblar_bd` también crea el superusuario `admin` (contraseña `password`) solo para el sitio `/admin/` de Django.

> **Si ya habías corrido `poblar_bd` antes de esta versión** (salas "Alfa", "Beta"…), corre una vez `python manage.py migrate` y luego `python manage.py poblar_bd --limpiar`. Borra las reservas, estudiantes y salas de demostración y las crea de nuevo con las salas A a J.

## 7. Pruebas (sin tocar la base real)

```powershell
python -m pytest -q
```

- Las pruebas que usan MongoDB crean una base aparte, `test_<MONGO_DB_NAME>` (por ejemplo `test_reservas_upb`), y la borran al terminar. **La base real no se lee ni se modifica.** Si por error apuntaran a la base real, se detienen.
- Las pruebas puras no necesitan MongoDB encendido:

  ```powershell
  python -m pytest -q tests/test_urls.py
  ```

## 8. Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `ServerSelectionTimeoutError` | MongoDB apagado, IP no permitida en Atlas o firewall | Revisa el paso 3 y la línea `MONGO_URI` del `.env` |
| `TypeError: Model instances without primary key value are unhashable` o errores de transacción | MongoDB sin replica set, o versiones distintas de Django y del backend | Opción C pasos 2 a 4; reinstala `requirements.txt` |
| `mongosh` o `mongod` "no se reconoce" | La terminal no cargó el PATH nuevo | Cierra y vuelve a abrir la terminal |
| No conecta a la base de un compañero en el WiFi de la UPB | El WiFi puede aislar a los dispositivos entre sí | Usen Atlas (opción A) |
