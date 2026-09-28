"""Validaciones de datos de entrada (PB-03).
"""

# SUPUESTO PENDIENTE DE CONFIRMAR CON EL CLIENTE (docente):
# cuantos digitos tiene un codigo de estudiante UPB.
LONGITUD_CODIGO_UPB = 5


def validar_codigo_upb(estudiante_codigo):
    """Valida el formato del codigo. Solo lee, no modifica nada.

    Devuelve {"valido": bool, "mensaje": str}.
    Ojo: esto valida el FORMATO, no que el estudiante este registrado.
    """
    # bool es subclase de int en Python, se excluye a proposito.
    if isinstance(estudiante_codigo, bool) or not isinstance(estudiante_codigo, int):
        return {"valido": False, "mensaje": "El codigo de estudiante debe ser numerico."}

    if estudiante_codigo <= 0:
        return {"valido": False, "mensaje": "El codigo de estudiante debe ser un numero positivo."}

    if len(str(estudiante_codigo)) != LONGITUD_CODIGO_UPB:
        return {
            "valido": False,
            "mensaje": f"El codigo de estudiante debe tener {LONGITUD_CODIGO_UPB} digitos.",
        }

    return {"valido": True, "mensaje": "Codigo valido."}
