# Campus Challenge — Requisitos

Estos ocho requisitos definen el comportamiento que debe cumplir el programa.

| ID | Requisito |
|---|---|
| R-01 | Utilizar Python 3.10 o superior y únicamente la biblioteca estándar en el código de la aplicación. pytest es la dependencia de desarrollo utilizada para las pruebas. |
| R-02 | Las funciones de utilidad deben devolver resultados nuevos y no modificar las colecciones recibidas como entrada. |
| R-03 | Recortar los espacios en blanco exteriores de las respuestas y normalizarlas para comparaciones sin distinción de mayúsculas y minúsculas compatibles con Unicode. |
| R-04 | La rotación izquierda debe ser circular, admitir una lista vacía e interpretar los pasos negativos como una rotación hacia la derecha. |
| R-05 | Redondear puntuaciones enteras no negativas a la decena más cercana. Cuando el valor esté exactamente a mitad de camino, redondear hacia arriba. |
| R-06 | Clasificar los equipos por puntuación descendente. Resolver los empates en orden alfabético sin distinguir mayúsculas y minúsculas. |
| R-07 | Eliminar etiquetas duplicadas conservando la primera aparición y el orden original. La comparación de etiquetas distingue mayúsculas y minúsculas. |
| R-08 | Calcular la media aritmética de una colección no vacía de puntuaciones. Para una colección vacía, devolver 0.0. |

## Relación con el código

| Función | Requisito específico |
|---|---|
| normalize_answer(answer) | R-03 |
| rotate_left(items, steps) | R-04 |
| round_score_to_ten(score) | R-05 |
| rank_teams(entries) | R-06 |
| unique_tags(tags) | R-07 |
| average_score(scores) | R-08 |

R-01 se aplica a todo el programa.

R-02 se aplica a las funciones que reciben colecciones.

## Entradas de la actividad

Se utilizan:

- Cadenas para respuestas y etiquetas.
- Listas para las colecciones.
- Pasos enteros para la rotación.
- Pares (nombre, puntuación) para los equipos.
- Puntuaciones enteras no negativas para el redondeo.

No se pide incorporar validaciones de tipos ni nuevas reglas para
entradas fuera de lo especificado. Consulta al docente cuando el
comportamiento requerido no esté definido.