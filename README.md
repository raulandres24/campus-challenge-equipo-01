# Sesión 01 — Campus Challenge: requisitos, código y pruebas

## El problema

Campus Challenge utiliza seis funciones para preparar respuestas,
rotar listas, redondear puntuaciones, ordenar equipos, eliminar
etiquetas repetidas y calcular promedios.

Recibes una implementación inicial y algunas pruebas. Tu tarea es:

1. Revisar si el programa cumple los ocho requisitos.
2. Añadir pruebas para comportamientos que todavía no se comprueban.
3. Corregir las funciones cuando sea necesario.
4. Validar el programa ejecutando las pruebas iniciales y las nuevas.

El resultado será el código mejorado y la suite de pruebas ampliada.

## 1. Preparar el entorno

Abre la carpeta del proyecto en PyCharm y utiliza Python 3.10 o superior.

Si PyCharm ya ha configurado un entorno virtual, utiliza su terminal.
De lo contrario, puedes crear uno desde la configuración del intérprete.

En macOS/Linux también puedes crearlo desde la terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Desde la carpeta que contiene este README, instala la dependencia:

```bash
python -m pip install -r requirements.txt
```

Ejecuta las pruebas:

```bash
python -m pytest -q
```

## 2. Leer antes de cambiar

1. Lee REQUISITOS.md.
2. Examina las funciones de challenge_tools/candidates.py.
3. Lee tests/test_baseline.py.
4. Identifica las entradas y los resultados que comprueba cada prueba.
5. Ejecuta las pruebas iniciales.

Que las pruebas existentes pasen no significa que todos los requisitos
estén cubiertos.

## 3. Encontrar casos que faltan

Compara cada requisito con las pruebas existentes.

Pregúntate:

- ¿Qué condiciones del requisito todavía no aparecen en las pruebas?
- ¿Qué sucede en los límites?
- ¿Qué sucede con colecciones vacías o con un solo elemento,
  cuando corresponda?
- ¿Se comprueban los empates, las repeticiones y las diferencias
  entre mayúsculas y minúsculas?
- ¿Las colecciones de entrada conservan su contenido después
  de ejecutar la función?
- ¿Qué ejemplos Unicode adicionales permiten comprobar
  la comparación de respuestas?

No basta con elegir caracteres al azar: cada prueba debe tener un
resultado esperado justificable a partir del requisito.

## 4. Añadir pruebas y mejorar el código

Repite este ciclo:

1. Elige un requisito y una entrada que no esté cubierta.
2. Determina el resultado esperado a partir del requisito.
3. Añade una prueba en tests/test_nuevos_casos.py.
4. Ejecuta la prueba antes de modificar la función.
5. Si falla, compara lo esperado con lo obtenido e investiga la causa.
6. Corrige la implementación cuando no cumpla el requisito.
7. Ejecuta toda la suite para comprobar que los cambios no afectan
   a los comportamientos ya verificados.

Cada prueba nueva debe:

- Tener un nombre que comience con test_.
- Utilizar assert para comprobar el comportamiento.
- Indicar el requisito correspondiente en un comentario o docstring.

Puedes utilizar puntos de interrupción y el depurador de PyCharm
para observar valores y seguir la ejecución.

Si una prueba nueva pasa desde el inicio, consérvala cuando compruebe
un comportamiento que faltaba. Una función que ya cumple los requisitos
no necesita cambios innecesarios.

### Ejecutar solo los casos nuevos

```bash
python -m pytest tests/test_nuevos_casos.py -v
```

### Ejecutar toda la suite

```bash
python -m pytest -v
```

Conserva las pruebas iniciales. No las elimines ni cambies sus resultados
esperados para ocultar un fallo.

Mantén los nombres de las funciones y sus parámetros para que las
pruebas puedan seguir utilizándolas.

## 5. Comprobar y entregar

Antes de entregar:

- Revisa los ocho requisitos y verifica que el código los cumple.
- Comprueba que las pruebas nuevas cubren comportamientos adicionales.
- Revisa los casos límite y la conservación de las entradas.
- Ejecuta toda la suite: todas las pruebas deben pasar.

Entrega el proyecto con:

- challenge_tools/candidates.py actualizado.
- Tus pruebas en tests/test_nuevos_casos.py.
- Las pruebas iniciales y los archivos necesarios para ejecutarlo.

Excluye del ZIP las carpetas .venv, __pycache__ y .pytest_cache.

No se solicita un informe adicional. Los comentarios de las pruebas
deben permitir relacionarlas con los requisitos.

El número de pruebas por sí solo no demuestra calidad: importa
qué comportamiento comprueba cada una.