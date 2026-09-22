from challenge_tools import unique_tags


def test_r07_conserva_orden_y_distingue_mayusculas():
    etiquetas = ["rojo", "azul", "rojo", "Azul", "verde", "rojo"]
    esperado = ["rojo", "azul", "Azul", "verde"]

    assert unique_tags(etiquetas) == esperado