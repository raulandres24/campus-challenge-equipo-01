from challenge_tools import unique_tags


def test_r07_conserva_orden_y_distingue_mayusculas():
    """R-07: Conserva el orden original y distingue mayúsculas de minúsculas."""
    etiquetas = ["rojo", "azul", "rojo", "Azul", "verde", "rojo"]
    esperado = ["rojo", "azul", "Azul", "verde"]
    assert unique_tags(etiquetas) == esperado


def test_r07_lista_vacia():
    """R-07: Una lista vacía debe devolver una lista vacía, sin errores."""
    assert unique_tags([]) == []


def test_r07_un_solo_elemento():
    """R-07: Una lista con un solo elemento se devuelve igual."""
    assert unique_tags(["java"]) == ["java"]


def test_r07_todos_repetidos():
    """R-07: Si todas las etiquetas son iguales, solo debe quedar la primera."""
    assert unique_tags(["python", "python", "python"]) == ["python"]


def test_r07_espacios_hacen_etiquetas_distintas():
    """R-07: El requisito no pide recortar espacios; " java" y "java" son etiquetas distintas."""
    etiquetas = ["java", " java", "java"]
    esperado = ["java", " java"]
    assert unique_tags(etiquetas) == esperado


def test_r07_no_modifica_entrada():
    """R-02 / R-07: La lista original no debe ser modificada tras la ejecución."""
    original = ["a", "a", "b"]
    copia = list(original)
    unique_tags(original)
    assert original == copia