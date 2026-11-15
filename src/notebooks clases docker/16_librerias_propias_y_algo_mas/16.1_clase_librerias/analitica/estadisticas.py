"""
estadisticas.py
===============
Submódulo de analitica: estadísticas descriptivas.
"""

import statistics

# Import relativo: el punto significa "desde este mismo paquete"
from ._utils import percentil

__all__ = ['resumen', 'detectar_outliers', 'normalizar']


def resumen(datos):
    """
    Devuelve un diccionario con las principales estadísticas descriptivas.

    Retorna
    -------
    dict con claves: n, media, mediana, desvio, minimo, maximo, p25, p75
    """
    datos = list(datos)
    if not datos:
        raise ValueError("La lista está vacía.")

    datos_ord = sorted(datos)
    n = len(datos)

    return {
        'n':       n,
        'media':   statistics.mean(datos),
        'mediana': statistics.median(datos),
        'desvio':  statistics.stdev(datos) if n > 1 else 0.0,
        'minimo':  datos_ord[0],
        'maximo':  datos_ord[-1],
        'p25':     percentil(datos_ord, 25),
        'p75':     percentil(datos_ord, 75),
    }


def detectar_outliers(datos):
    """
    Detecta valores atípicos con el método IQR.

    Un valor es outlier si está por debajo de Q1 - 1.5*IQR
    o por encima de Q3 + 1.5*IQR.

    Retorna
    -------
    dict con claves: outliers, limite_inf, limite_sup
    """
    datos = list(datos)
    if len(datos) < 4:
        raise ValueError("Se necesitan al menos 4 valores para calcular outliers.")

    datos_ord = sorted(datos)
    q1 = percentil(datos_ord, 25)
    q3 = percentil(datos_ord, 75)
    iqr = q3 - q1

    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr

    return {
        'outliers':   [x for x in datos if x < limite_inf or x > limite_sup],
        'limite_inf': limite_inf,
        'limite_sup': limite_sup,
    }


def normalizar(datos):
    """Escala los valores al rango [0, 1]: (x - min) / (max - min)."""
    datos = list(datos)
    minimo, maximo = min(datos), max(datos)

    if minimo == maximo:
        raise ValueError("Todos los valores son iguales — no se puede normalizar.")

    return [(x - minimo) / (maximo - minimo) for x in datos]
