from proyecto.validaciones import validar_codigo_upb


def test_codigo_valido_se_acepta():
    assert validar_codigo_upb(92345)["valido"] is True


def test_rechaza_codigo_no_numerico():
    resultado = validar_codigo_upb("ABCDE")
    assert resultado["valido"] is False
    assert "numerico" in resultado["mensaje"]


def test_rechaza_codigo_negativo():
    resultado = validar_codigo_upb(-92345)
    assert resultado["valido"] is False
    assert "positivo" in resultado["mensaje"]


def test_rechaza_codigo_con_cantidad_de_digitos_incorrecta():
    assert validar_codigo_upb(1234)["valido"] is False  # muy corto
    assert validar_codigo_upb(123456)["valido"] is False  # muy largo


def test_rechaza_booleano_aunque_python_lo_trate_como_entero():
    assert validar_codigo_upb(True)["valido"] is False
