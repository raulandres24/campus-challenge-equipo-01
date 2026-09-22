# Sesión 03 — Colaboración con Git y GitHub

**Ingeniería de Software · Guía de laboratorio para estudiantes**    
**Punto de partida:** la actividad o primera tarea de la Sesión 01, Campus Challenge.  
**Modalidad:** equipos de proyecto; cada integrante trabaja con su propia cuenta y copia local.

## 1. El desafío

Hasta ahora han trabajado en funciones de Python y en pruebas que verifican sus requisitos. En esta sesión colaborarán sobre una misma versión del programa: cada integrante propondrá una mejora, otra persona la revisará y el equipo integrará las contribuciones.

Al terminar podrán:

- Distinguir un cambio local, un commit y un cambio publicado en GitHub.
- Crear una rama para una contribución concreta.
- Agregar pruebas y corregir funciones cuando los requisitos lo exijan.
- Revisar una contribución mediante un pull request (PR).
- Integrar cambios y comprobar el resultado con pytest.

**Cada estudiante debe ser autor y revisor.** Una persona puede crear el repositorio, pero no realizar todas las contribuciones del equipo.

## 2. Conceptos para la demostración inicial

| Concepto | Qué significa en esta práctica |
|---|---|
| Git | Registra versiones del proyecto en su computadora. |
| GitHub | Aloja el repositorio compartido y permite discutir y revisar contribuciones. |
| Directorio de trabajo | Los archivos que están editando. |
| Área de preparación, staging | Los cambios seleccionados con `git add` para el siguiente commit. |
| Commit | Una versión registrada localmente con un mensaje que explica el cambio. |
| Rama | Una línea de trabajo para desarrollar una contribución. |
| `main` | La rama donde el equipo reúne el trabajo integrado. |
| `origin` | El nombre que utilizaremos para el repositorio remoto en GitHub. |
| Push | Publica commits locales en el repositorio remoto. |
| Pull request | Solicitud para revisar e integrar una rama en otra. |
| Merge | Integra el trabajo de dos ramas. |
| Pull | Obtiene cambios remotos y los incorpora en la rama local. |

**Guardar un archivo no crea un commit. Crear un commit no lo publica en GitHub. Fusionar un PR en GitHub no actualiza automáticamente las computadoras del equipo.**

En la demostración observarán un ciclo completo: crear rama, editar, ejecutar pruebas, revisar diferencias, registrar un commit, publicar la rama, abrir un PR, revisarlo e integrarlo.

## 3. Organización del tiempo

| Minutos | Trabajo |
|---|---|
| 0–30 | Explicación y demostración del flujo completo. |
| 30–45 | Repositorio compartido, copias locales y ejecución inicial. |
| 45–70 | Contribución individual: pruebas nuevas y mejoras justificadas. |
| 70–90 | Pull requests y revisión entre compañeros. |
| 90–105 | Integración secuencial y verificación del conjunto. |
| 105–115 | Demostración guiada de un conflicto de documentación. |
| 115–120 | Entrega y preguntas individuales. |

## 4. Preparación y elección de la versión inicial

Antes de la práctica deben tener Git, Python 3.10 o superior, una cuenta de GitHub y acceso autenticado desde su computadora. Pueden editar en PyCharm y ejecutar los comandos en su terminal.

El equipo elige **una entrega de la Sesión 01 como versión inicial**. Registren en el README de quién proviene y qué pruebas contiene. Si las entregas difieren, no copien varias carpetas completas unas encima de otras: las mejoras de las demás versiones se incorporarán mediante ramas y PR.

Conserven los requisitos y las pruebas existentes. Si la versión inicial tiene fallos, anoten cuáles son antes de cambiar el código. Si ya funciona correctamente, todavía pueden mejorar su cobertura con casos que no se hayan comprobado.

Para esta práctica utilicen un repositorio de Campus Challenge separado del proyecto semestral. El flujo aprendido se aplicará después a ese proyecto.

### Requisitos que siguen vigentes

| ID | Comportamiento requerido |
|---|---|
| R-01 | Python 3.10 o superior y biblioteca estándar para las funciones del programa. pytest se utiliza para las pruebas. |
| R-02 | Devolver resultados nuevos sin modificar las colecciones de entrada. |
| R-03 | Quitar espacios exteriores y permitir comparación sin distinción de mayúsculas y minúsculas compatible con Unicode. |
| R-04 | Rotar a la izquierda con desplazamientos que se repiten cíclicamente; aceptar una lista vacía; interpretar pasos negativos como rotación a la derecha. |
| R-05 | Redondear puntuaciones enteras no negativas a la decena más cercana; en la mitad exacta, redondear hacia arriba. |
| R-06 | Ordenar equipos por puntuación descendente; resolver empates alfabéticamente sin distinguir mayúsculas y minúsculas. |
| R-07 | Eliminar etiquetas duplicadas conservando la primera aparición y el orden original. La comparación distingue mayúsculas y minúsculas. |
| R-08 | Calcular la media aritmética de las puntuaciones; para una colección vacía devolver `0.0`. |

No agreguen reglas para entradas fuera de estos requisitos sin consultarlo. Por ejemplo, aceptar cadenas donde se esperan números no es una obligación de esta actividad.

## 5. Crear el repositorio compartido

**Una persona del equipo:**

1. Cree en GitHub un repositorio llamado, por ejemplo, `campus-challenge-equipo-01` e inicialícelo con un README.
2. Invite a los demás integrantes como colaboradores desde la configuración del repositorio. Cada integrante debe aceptar la invitación.
3. Clone el repositorio y copie dentro los archivos elegidos de la Sesión 01. Conserve el README generado o integre su contenido. No copie una carpeta `.git`, un entorno virtual ni archivos de caché de la entrega anterior.

```bash
git clone https://github.com/USUARIO/campus-challenge-equipo-01.git
cd campus-challenge-equipo-01
```

Sustituyan `USUARIO` y el nombre del repositorio por los reales. La URL se puede copiar del botón **Code** en GitHub. Los comandos siguientes se ejecutan desde la carpeta raíz del proyecto.

Configuren su identidad local para este repositorio:

```bash
git config user.name "Nombre Apellido"
git config user.email "CORREO_ASOCIADO_A_GITHUB"
```

Pueden usar el correo privado `noreply` que muestra su cuenta de GitHub. Esta configuración identifica sus commits; no inicia sesión.

### Archivos y carpetas

| Ruta | Uso |
|---|---|
| `challenge_tools/__init__.py` | Exportaciones existentes del paquete. |
| `challenge_tools/candidates.py` | Funciones que se mejorarán cuando sea necesario. |
| `tests/test_baseline.py` | Pruebas originales; se conservan. |
| `tests/` | También conserva cualquier otra prueba válida de la Sesión 01. |
| `tests/sesion03/` | Carpeta nueva para las contribuciones de esta sesión. |
| `requirements.txt` | Dependencia de pruebas: `pytest>=8,<10`. |
| `pytest.ini` | Configuración de descubrimiento e importación de las pruebas. |
| `README.md` | Descripción, integrantes y pasos de ejecución. |
| `.gitignore` | Archivos locales que no se incorporan al repositorio. |

Git registra archivos, no carpetas vacías: `tests/sesion03/` aparecerá en GitHub cuando contenga un archivo registrado.

Creen `.gitignore` con este contenido antes de registrar los archivos:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.idea/
.DS_Store
```

Si no existe una configuración equivalente, utilicen en `pytest.ini`:

```ini
[pytest]
testpaths = tests
pythonpath = .
```

La persona que prepara la base verifica los archivos y registra la versión inicial:

```bash
git status
git add .
git diff --cached --stat
git commit -m "Incorpora la entrega inicial de Campus Challenge"
git push origin main
```

Antes del commit, comprueben que no se incluyeron entornos virtuales ni archivos ajenos a la práctica. Este commit inicial es la excepción: las contribuciones posteriores se integran mediante PR.

**Después, los demás integrantes clonan el repositorio** con los mismos comandos de `git clone` y `cd`, y configuran su propia identidad. Quien ya lo clonó no necesita clonarlo otra vez.

## 6. Preparar el entorno y medir el punto de partida

Cada integrante crea su propio entorno virtual. En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows, desde PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, pueden invocar directamente `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos siguientes.

Con el entorno activado:

```bash
python --version
python -m pip install -r requirements.txt
python -m pytest -q
```

Revisen qué pruebas pasan y cuáles fallan. No supongan un número fijo de pruebas: depende de la entrega elegida. Distingan un fallo de una función de un problema de instalación o importación.

**Punto de control:** todas las personas ejecutan la misma versión inicial y conocen su resultado.

## 7. Elegir una contribución y crear una rama

Cada integrante elige un requisito. Coordinen las funciones que van a modificar para evitar cambios simultáneos innecesarios sobre las mismas líneas.

| Función o requisito | Casos para investigar; comprueben primero si ya existen |
|---|---|
| `normalize_answer` | Espacios exteriores y equivalencias de mayúsculas/minúsculas en Unicode. |
| `rotate_left` | Lista vacía, cero pasos, pasos negativos y pasos mayores que la longitud. |
| `round_score_to_ten` | Cero, valores a ambos lados de una mitad y mitades exactas. |
| `rank_teams` | Empates y nombres con distintas combinaciones de mayúsculas/minúsculas. |
| `unique_tags` | Repeticiones intercaladas, orden y distinción entre `a` y `A`. |
| `average_score` | Colección vacía, un elemento y media no entera. |
| R-02 | Comparar la colección de entrada antes y después de llamar a una función. |

No se exige modificar una función que ya cumple el requisito. En ese caso, aporten una prueba relevante que amplíe la evidencia.

Antes de empezar, comprueben que no tienen cambios pendientes:

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c pruebas/tigre-ser
```

`pruebas/tigre-ana` es un ejemplo. Utilicen su requisito y nombre, sin espacios ni tildes. Mantengan ese nombre durante todo el procedimiento.

## 8. Agregar pruebas y mejorar las funciones

Creen la carpeta `tests/sesion03/` desde PyCharm. Cada integrante crea allí un archivo con nombre propio y descriptivo, por ejemplo:

- `test_r07_bruna.py`
- `test_r04_daisy.py`
- `test_r08_peach.py`

Los archivos y las funciones de prueba deben comenzar con `test_`. Eviten repetir nombres de archivo de otras carpetas. No es necesario agregar `__init__.py` a esta carpeta para la estructura propuesta.

Para cada caso:

1. Lean el requisito y determinen el resultado esperado antes de ejecutar el programa.
2. Escriban una prueba que llame a la función real del paquete.
3. Ejecuten la prueba sobre la implementación actual.
4. Si falla, identifiquen si el error está en la función o en la interpretación del requisito. Corrijan la función cuando corresponda.
5. Ejecuten de nuevo la prueba y después toda la suite.

Este ejemplo muestra el formato de una prueba, sin proporcionar la implementación de la función:

```python
from challenge_tools import unique_tags


def test_r07_distingue_mayusculas_y_conserva_orden():
    etiquetas = ["a", "b", "A", "a", "B"]
    esperado = ["a", "b", "A", "B"]

    assert unique_tags(etiquetas) == esperado
```

Si ya tienen ese caso, elijan otro. Un nombre diferente para la misma comprobación no amplía necesariamente la cobertura.

Para ejecutar un archivo y luego el conjunto completo:

```bash
python -m pytest tests/sesion03/test_r07_bruna.py -q
python -m pytest -q
```

**Una prueba nueva puede pasar desde el primer intento.** No introduzcan errores deliberados. Tampoco eliminen pruebas, reduzcan sus comprobaciones ni cambien resultados esperados para ocultar un incumplimiento.

Si quedan fallos iniciales en otras funciones, asignen su corrección dentro del equipo. Pueden abrir un PR como borrador para discutir trabajo incompleto; antes de integrar, el conjunto debe pasar después de incorporar las correcciones necesarias.

## 9. Revisar y registrar la contribución

Inspeccionen sus cambios:

```bash
git status
git diff
```

`git diff` muestra cambios en archivos ya registrados. Los archivos nuevos aparecen en `git status`; después de agregarlos podrán inspeccionarlos con `git diff --cached`.

Preparen únicamente los archivos de su contribución:

```bash
git add tests/sesion03/test_r07_bruna.py
```

Si modificaron la implementación, agreguen también:

```bash
git add challenge_tools/candidates.py
```

Revisen y registren:

```bash
git diff --cached
git commit -m "R-07: agrega cobertura de etiquetas sensibles a mayusculas"
git push -u origin pruebas/r07-bruna
```

Adapten las rutas, el mensaje y la rama a lo que realmente hicieron. Un buen mensaje explica el propósito. Eviten mensajes como `cosas`, `final` o `ahora si`.

## 10. Abrir el pull request

En GitHub, abran un PR desde su rama hacia `main`. Comprueben los campos de rama base y rama de origen.

Utilicen esta descripción breve y completen los espacios:

```text
Requisito: R-__

Cambio:
[Qué prueba agregué y qué función modifiqué, si corresponde.]

Caso y resultado esperado:
[Entrada, salida esperada y razón basada en el requisito.]

Verificación:
[Comando ejecutado y resultado real de las pruebas.]
```

Soliciten la revisión de un compañero.

**Un PR es una propuesta de integración. Todavía no cambia `main`.**

## 11. Revisar el trabajo de otra persona

El revisor abre **Files changed** y comprueba:

- ¿El resultado esperado se deriva del requisito?
- ¿La prueba llama a la función real y contiene una comprobación útil?
- ¿El nuevo caso agrega información respecto de los existentes?
- ¿La modificación conserva los demás requisitos, incluido R-02?
- ¿El PR incluye solamente cambios relacionados con su propósito?

Dejen un comentario concreto. Por ejemplo: «La prueba distingue las etiquetas por mayúsculas, pero todavía no comprueba el orden cuando una etiqueta reaparece después de otra». No basta escribir «bien» sin explicar qué revisaron.

Para ejecutar la rama del compañero, primero terminen y registren su propio trabajo. Con `git status` limpio:

```bash
git fetch origin
git switch --track origin/pruebas/r04-luis
python -m pytest -q
```

Si esa rama ya existe localmente, usen `git switch pruebas/r04-peach` y luego `git pull --ff-only`. Sustituyan el nombre por la rama real. No hagan cambios en la rama del compañero: dejen observaciones en su PR.

El autor vuelve a su propia rama, atiende los comentarios y publica los ajustes mediante otro commit y `git push`. El PR se actualiza con esos commits. El revisor vuelve a verificar y aprueba cuando corresponda. No es necesario inventar una objeción si todo está correcto: expliquen la comprobación realizada.

## 12. Integrar y verificar el resultado conjunto

Integren los PR **uno por uno**. Antes de cada integración, el autor incorpora el estado reciente de `main` en su rama para comprobar la combinación real:

```bash
git switch pruebas/r07-bruna
git status
git fetch origin
git merge --no-edit origin/main
python -m pytest -q
git push
```

Ejecuten el merge con el directorio de trabajo limpio. Si aparece un conflicto, resuélvanlo con ayuda del docente antes de continuar. Si la integración cambió el contenido del PR, el revisor comprueba la versión actualizada.

Con revisión terminada y pruebas aprobadas, fusionen el PR en GitHub. **Que GitHub permita fusionar sin conflictos no significa que haya ejecutado pytest:** en esta sesión las pruebas se ejecutan localmente.

Tras la fusión, cada integrante actualiza su copia:

```bash
git switch main
git pull --ff-only origin main
python -m pytest -q
git log --oneline -6
```

La siguiente contribución se verifica contra este nuevo estado. No continúen trabajando en una rama ya integrada: creen otra desde `main` actualizado para la siguiente tarea.

## 13. Conflicto: dos cambios sobre una misma línea

**No se introduce un defecto en Python.**

En un archivo de documentación se escribe inicialmente `Responsable de revisión: por asignar`. Dos ramas parten de ese mismo commit. Una cambia esa línea para asignar a Bruna; la otra, para asignar a Peach. Tras integrar la primera, la segunda debe incorporar `main` y resolver la diferencia.

En la segunda rama, con trabajo registrado:

```bash
git fetch origin
git merge --no-edit origin/main
git status
```

Git señalará el archivo en conflicto. El equipo acuerda el texto correcto, edita el archivo y elimina los marcadores `<<<<<<<`, `=======` y `>>>>>>>`. No se elige automáticamente una versión: se conserva el resultado acordado.

Después, usando la ruta real del archivo:

```bash
git add README.md
git commit -m "Resuelve acuerdo de responsables de revision"
python -m pytest -q
git push
```

El PR vuelve a revisarse antes de integrarlo. Si lo ven necesario, pueden cancelar el intento mientras el merge sigue en conflicto, `git merge --abort` permite abandonar esa integración; por eso comenzamos con el trabajo previo registrado.

## 14. Entrega y criterios de cumplimiento

Entreguen **el enlace del repositorio**, accesible al docente, y los enlaces de los PR. No se requiere un informe separado ni un registro de decisiones de liberación.

| Evidencia | Criterio |
|---|---|
| Base compartida | El README identifica la entrega de la Sesión 01 utilizada. |
| Contribución individual | Cada integrante es autor de al menos un PR integrado con una prueba nueva relevante y cambios de código cuando son necesarios. |
| Revisión individual | Cada integrante revisa al menos un PR ajeno con una observación o validación concreta. |
| Requisitos | Las pruebas y las modificaciones respetan R-01 a R-08. |
| Integración | La suite completa pasa en la versión final de `main`. |
| Reproducibilidad | El README explica cómo instalar las dependencias y ejecutar las pruebas. |
| Historial | Los mensajes permiten entender qué se hizo y por qué. |

Agregar al README una tabla breve facilita localizar las contribuciones:

| Integrante | Requisito trabajado | PR propio | PR revisado |
|---|---|---|---|
| Nombre | R-__ | Enlace | Enlace |

La cantidad de commits por sí sola no demuestra calidad. Se evalúa la contribución y la capacidad de explicarla.

### Preguntas individuales de salida

1. ¿Qué diferencia existe entre guardar, hacer commit y hacer push?
2. ¿Qué cambia cuando un compañero fusiona su PR? ¿Qué debes hacer en tu computadora?
3. ¿Qué requisito verifica tu prueba y qué comportamiento incorrecto detectaría?
4. ¿Por qué una prueba nueva que pasa inmediatamente puede ser útil?

## 15. Problemas frecuentes

| Situación | Qué comprobar |
|---|---|
| `git` no se reconoce | Git debe estar instalado y disponible en la terminal. |
| No pueden clonar o publicar | URL, cuenta autenticada, invitación aceptada y permisos del repositorio. |
| `Author identity unknown` | Configuren `user.name` y `user.email` dentro del repositorio. |
| `No module named pytest` | Usen el intérprete del entorno e instalen con `python -m pip install -r requirements.txt`. |
| `No module named challenge_tools` | Ejecuten desde la raíz, con el paquete y `pytest.ini` en sus ubicaciones previstas. |
| pytest no encuentra una prueba | Archivo `test_*.py`, función `test_*`, ubicación bajo `tests/` y contenido guardado. |
| No aparece una carpeta en GitHub | Debe contener un archivo agregado, registrado y publicado. |
| Git impide cambiar de rama | Revisen `git status` y terminen de registrar su trabajo antes de cambiar. |
| El push o `pull --ff-only` se rechaza | Revisen la rama y el historial con el docente; no utilicen `--force` para saltarse el problema. |
| Otro PR modifica la misma función | Coordinen el orden, integren `origin/main` en la rama y vuelvan a ejecutar las pruebas. |
| Una prueba existente falla tras el cambio | Revisen la regresión; no eliminen la prueba para obtener una ejecución verde. |

## 16. Documentación de consulta

Esta práctica es una adaptación docente de Campus Challenge. Las referencias siguientes documentan las herramientas; no proporcionan las soluciones de las funciones.

- [GitHub Docs — GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow): ramas, publicación, revisión e integración.
- [Git — Manual de git-merge](https://git-scm.com/docs/git-merge): integración y resolución de conflictos.
- [pytest — Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html): organización y descubrimiento de pruebas.
