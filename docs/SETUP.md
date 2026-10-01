# Guía de instalación — Reserva de Salas UPB (Django + MongoDB)

Esta guía es para que cualquier integrante del equipo (Hugo, Raúl, Alejandro) deje el proyecto corriendo en su propia máquina, con MongoDB local.

## 1. Requisitos previos

- Python 3.10 o superior instalado
- Git
- PyCharm (o el editor que prefieras)

## 2. Clonar el repositorio

```powershell
git clone https://github.com/raulandres24/campus-challenge-equipo-01
cd campus-challenge-equipo-01
```

## 3. Crear entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Si `requirements.txt` no incluye todavía `django-mongodb-backend` y `python-dotenv`, instálalos a mano:

```powershell
pip install "django>=5.2,<6.0" "django-mongodb-backend==5.2.4" python-dotenv
```

> **Importante:** usamos específicamente `django-mongodb-backend==5.2.4` con `Django 5.2.x`. Versiones más nuevas (como la 6.1.0) tienen un bug conocido que rompe las migraciones. No instales versiones distintas a estas sin avisar al equipo.

## 4. Instalar MongoDB Community Server

1. Ve a **https://www.mongodb.com/try/download/community**
2. Clic en **"Select Package"**, elige **Windows** / **msi**, descarga
3. Instala con la opción **"Install MongoDB as a Service"** marcada

## 5. Instalar mongosh (consola de MongoDB)

Si al escribir `mongosh` en la terminal te dice que no existe:

1. Ve a **https://www.mongodb.com/try/download/shell**
2. Windows / msi, descarga e instala
3. Cierra y vuelve a abrir tu terminal

## 6. Configurar MongoDB para aceptar conexiones de red y transacciones

Edita el archivo de configuración (ruta típica, ajusta la versión):
```
C:\Program Files\MongoDB\Server\<version>\bin\mongod.cfg
```

Necesita permisos de administrador para editarlo (abre tu editor de texto "como administrador").

Busca la sección `net:` y la sección `replication:` (o agrégala si no existe) para que quede así:

```yaml
net:
  port: 27017
  bindIp: 0.0.0.0

replication:
  replSetName: "rs0"
```

Guarda y reinicia el servicio **en una PowerShell abierta como administrador**:

```powershell
Restart-Service MongoDB
```

Abre el firewall de Windows para el puerto (también en PowerShell como administrador):

```powershell
New-NetFirewallRule -DisplayName "MongoDB" -Direction Inbound -Protocol TCP -LocalPort 27017 -Action Allow
```

## 7. Inicializar el replica set (obligatorio, una sola vez)

MongoDB necesita correr como *replica set* (aunque sea de un solo nodo) para que `django-mongodb-backend` funcione — sin esto, las migraciones fallan.

```powershell
mongosh
```

Dentro de la consola:

```javascript
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "localhost:27017" }]
})
```

Verifica que diga `PRIMARY`:
```javascript
rs.status()
```

Sal con `exit`.

## 8. Crear tu archivo `.env`

En la raíz del proyecto (junto a `manage.py`), crea un archivo llamado exactamente `.env` (cuidado con editores que le agregan `.txt` al final) con este contenido:

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=reservas_upb
```

> Usa `localhost` si vas a trabajar solo. Si te vas a conectar a la base de **otro compañero** (por ejemplo, la de Raúl cuando están juntos en la misma red), reemplaza `localhost` por su IP de red local (se las compartirá él mismo, cambia según la red en la que esté).

## 9. Aplicar las migraciones

```powershell
python manage.py migrate
```

Vas a ver un aviso sobre `admin`, `auth`, `contenttypes` con "cambios no reflejados" — es normal, **ignóralo**, no corras `makemigrations` sobre esos tres apps.

## 10. Crear tu usuario

```powershell
python manage.py createsuperuser
```

## 11. Correr el servidor

```powershell
python manage.py runserver
```

Abre **http://127.0.0.1:8000/** — deberías ver la pantalla de login, y después de entrar, la lista de salas y reservas.

---

## Problemas comunes

**`mongosh` o `mongod` no se reconoce como comando** → cierra y vuelve a abrir la terminal después de instalar, para que cargue el PATH actualizado.

**Error `TypeError: Model instances without primary key value are unhashable`** → significa que no se inicializó el replica set (paso 7), o que estás usando una versión de `django-mongodb-backend`/`Django` distinta a la indicada en el paso 3.

**`ServerSelectionTimeoutError`** → MongoDB no está corriendo, o el replica set no está inicializado, o el firewall está bloqueando el puerto.

**No puedo conectarme a la base de otro compañero estando en la misma red de la universidad** → el WiFi de la UPB puede tener aislamiento de clientes (bloquea conexiones directas entre dispositivos). Alternativa: usar Radmin VPN para crear una red virtual entre ustedes.
