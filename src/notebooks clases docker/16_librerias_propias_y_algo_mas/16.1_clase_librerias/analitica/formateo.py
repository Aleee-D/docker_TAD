"""
formateo.py
===========
Submódulo de analitica: formateo de números al estilo argentino
(punto para miles, coma para decimales).
"""

from ._utils import separar_miles

__all__ = ['formato_moneda', 'formato_porcentaje', 'formato_miles']


def formato_moneda(valor, simbolo='$', decimales=2):
    """
    Formatea un número como moneda.

    >>> formato_moneda(1234567.89)
    '$ 1.234.567,89'
    >>> formato_moneda(1500, simbolo='USD', decimales=0)
    'USD 1.500'
    """
    # Redondeamos primero el valor completo y después separamos
    # parte entera y decimal (evita que 0.999 se muestre como 0,00 + 1)
    texto = f"{abs(valor):.{decimales}f}"
    if decimales > 0:
        entero, decimal = texto.split('.')
        parte_decimal = ',' + decimal
    else:
        entero, parte_decimal = texto, ''

    signo = '-' if valor < 0 else ''
    return f"{signo}{simbolo} {separar_miles(int(entero))}{parte_decimal}"


def formato_porcentaje(valor, decimales=1):
    """
    Formatea un número como porcentaje (con signo).
    Si |valor| <= 1 lo interpreta como proporción.

    >>> formato_porcentaje(0.1534)
    '+15,3%'
    >>> formato_porcentaje(-0.05)
    '-5,0%'
    """
    pct = valor * 100 if abs(valor) <= 1 else valor
    return f"{pct:+.{decimales}f}%".replace('.', ',')


def formato_miles(valor):
    """
    Formatea un entero con separador de miles.

    >>> formato_miles(1234567)
    '1.234.567'
    """
    signo = '-' if valor < 0 else ''
    return signo + separar_miles(int(valor))
