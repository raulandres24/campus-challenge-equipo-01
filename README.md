# Reserva de Salas de Estudio — UPB Santa Cruz

Proyecto de Ingeniería de Software (P02 — Reservas de espacios),
adaptado a un sistema de reserva de salas de estudio universitarias.

## Integrantes

- Hugo Zúñiga
- Raúl Vaca
- Alejandro Párraga

## Estado actual

Fase: definición de requisitos y primera capacidad (Sesión 04).
Reglas de negocio en `proyecto/reglas.py`, operando con colecciones
en memoria (diccionarios) mediante validaciones TDD.

## Preparar el entorno

```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
```

## Ejecutar las pruebas

```bash
# Ejecutar suite completa de forma resumida
python -m pytest -q

# Ejecutar con detalles
python -m pytest -v
```

## Estructura

```text
proyecto/       Reglas de negocio (funciones puras, validación de reservas)
tests/          Pruebas automatizadas de las reglas (TDD)
docs/           Registro de acuerdos, backlog, ejemplos y retrospectivas
```

## Limitaciones actuales

Sin persistencia en base de datos real (MySQL/MariaDB) ni interfaz de usuario;
ambas características se incorporarán en fases posteriores del curso.