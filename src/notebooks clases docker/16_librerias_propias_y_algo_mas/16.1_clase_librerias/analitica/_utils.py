"""
_utils.py
=========
Funciones auxiliares internas del paquete analitica.

El guion bajo en el nombre del archivo indica que es un submódulo
privado: lo usan los otros submódulos, no el usuario final.
"""


def percentil(datos_ordenados, p):
    """Calcula el percentil p de una lista ya ordenada (interpolación lineal)."""
    n = len(datos_ordenados)
    idx = (p / 100) * (n - 1)
    inferior = int(idx)
    fraccion = idx - inferior

    if inferior + 1 < n:
        return datos_ordenados[inferior] + fraccion * (
            datos_ordenados[inferior + 1] - datos_ordenados[inferior]
        )
    return datos_ordenados[inferior]


def separar_miles(entero, sep='.'):
    """Agrega separador de miles a un entero."""
    s = str(abs(entero))
    grupos = []
    while len(s) > 3:
        grupos.append(s[-3:])
        s = s[:-3]
    grupos.append(s)
    return sep.join(reversed(grupos))
