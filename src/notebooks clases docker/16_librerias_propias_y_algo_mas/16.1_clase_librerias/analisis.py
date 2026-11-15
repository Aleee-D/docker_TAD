"""
analisis.py
===========
Módulo de utilidades para análisis y formateo de datos numéricos.

Secciones
---------
- Estadísticas : resumen, outliers, normalización
- Formateo     : moneda, porcentaje, miles
"""

__all__ = [
    'resumen',
    'detectar_outliers',
    'normalizar',
    'formato_moneda',
    'formato_porcentaje',
    'formato_miles',
]

# ── Dependencias ──────────────────────────────────────────────────
import statistics


# ════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Estadísticas
# ════════════════════════════════════════════════════════════════

def resumen(datos):
    """
    Devuelve un diccionario con las principales estadísticas descriptivas.

    Parámetros
    ----------
    datos : list o cualquier iterable de números

    Retorna
    -------
    dict con claves: n, media, mediana, desvio, minimo, maximo, p25, p75

    Ejemplo
    -------
    >>> resumen([2, 4, 4, 4, 5, 5, 7, 9])
    {'n': 8, 'media': 5.0, 'mediana': 4.5, ...}
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
        'p25':     _percentil(datos_ord, 25),
        'p75':     _percentil(datos_ord, 75),
    }


def detectar_outliers(datos):
    """
    Detecta valores atípicos usando el método IQR (rango intercuartílico).

    Un valor es outlier si está por debajo de  Q1 - 1.5 * IQR
    o por encima de  Q3 + 1.5 * IQR.

    Parámetros
    ----------
    datos : list o cualquier iterable de números

    Retorna
    -------
    dict con claves:
        outliers      — lista de valores atípicos
        limite_inf    — umbral inferior
        limite_sup    — umbral superior

    Ejemplo
    -------
    >>> detectar_outliers([10, 12, 11, 13, 9, 100, 11])
    {'outliers': [100], 'limite_inf': 3.5, 'limite_sup': 20.5}
    """
    datos = list(datos)
    if len(datos) < 4:
        raise ValueError("Se necesitan al menos 4 valores para calcular outliers.")

    datos_ord = sorted(datos)
    q1 = _percentil(datos_ord, 25)
    q3 = _percentil(datos_ord, 75)
    iqr = q3 - q1

    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr

    outliers = [x for x in datos if x < limite_inf or x > limite_sup]

    return {
        'outliers':   outliers,
        'limite_inf': limite_inf,
        'limite_sup': limite_sup,
    }


def normalizar(datos):
    """
    Escala los valores al rango [0, 1] usando min-max normalization.

    Fórmula: (x - min) / (max - min)

    Parámetros
    ----------
    datos : list o cualquier iterable de números

    Retorna
    -------
    list de floats en el rango [0.0, 1.0]

    Ejemplo
    -------
    >>> normalizar([0, 5, 10])
    [0.0, 0.5, 1.0]
    """
    datos = list(datos)
    minimo = min(datos)
    maximo = max(datos)

    if minimo == maximo:
        raise ValueError("Todos los valores son iguales — no se puede normalizar.")

    return [(x - minimo) / (maximo - minimo) for x in datos]


# ── Helper privado (no aparece en __all__) ────────────────────────
def _percentil(datos_ordenados, p):
    """Calcula el percentil p de una lista ya ordenada."""
    n = len(datos_ordenados)
    idx = (p / 100) * (n - 1)
    inferior = int(idx)
    fraccion = idx - inferior

    if inferior + 1 < n:
        return datos_ordenados[inferior] + fraccion * (datos_ordenados[inferior + 1] - datos_ordenados[inferior])
    return datos_ordenados[inferior]


# ════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Formateo
# ════════════════════════════════════════════════════════════════

def formato_moneda(valor, simbolo='$', decimales=2):
    """
    Formatea un número como moneda con separador de miles y decimales.

    Parámetros
    ----------
    valor    : int o float
    simbolo  : str   — símbolo de moneda (default: '$')
    decimales: int   — cantidad de decimales (default: 2)

    Retorna
    -------
    str

    Ejemplos
    --------
    >>> formato_moneda(1234567.89)
    '$ 1.234.567,89'
    >>> formato_moneda(1500, simbolo='USD', decimales=0)
    'USD 1.500'
    """
    # Separar parte entera y decimal
    if decimales > 0:
        entero = int(abs(valor))
        decimal = round(abs(valor) - entero, decimales)
        parte_decimal = f"{decimal:.{decimales}f}"[1:]  # ",89"
    else:
        entero = round(abs(valor))
        parte_decimal = ''

    # Separador de miles con punto
    entero_formateado = _separar_miles(entero, sep='.')

    signo = '-' if valor < 0 else ''
    numero = f"{entero_formateado}{parte_decimal.replace('.', ',')}"

    return f"{signo}{simbolo} {numero}"


def formato_porcentaje(valor, decimales=1):
    """
    Formatea un número como porcentaje.

    Parámetros
    ----------
    valor    : float — puede ser proporción (0.15) o ya porcentaje (15.0);
                       si el valor absoluto es <= 1, asume proporción
    decimales: int   — cifras decimales (default: 1)

    Retorna
    -------
    str

    Ejemplos
    --------
    >>> formato_porcentaje(0.1534)
    '15,3%'
    >>> formato_porcentaje(15.34)
    '15,3%'
    >>> formato_porcentaje(-0.05)
    '-5,0%'
    """
    # Detectar si viene como proporción o como porcentaje
    if abs(valor) <= 1:
        pct = valor * 100
    else:
        pct = valor

    return f"{pct:+.{decimales}f}%".replace('.', ',')


def formato_miles(valor):
    """
    Formatea un entero con separador de miles.

    Parámetros
    ----------
    valor : int o float (se trunca la parte decimal)

    Retorna
    -------
    str

    Ejemplos
    --------
    >>> formato_miles(1234567)
    '1.234.567'
    >>> formato_miles(999)
    '999'
    """
    return _separar_miles(int(valor), sep='.')


# ── Helper privado ────────────────────────────────────────────────
def _separar_miles(entero, sep='.'):
    """Agrega separador de miles a un entero."""
    s = str(abs(entero))
    grupos = []
    while len(s) > 3:
        grupos.append(s[-3:])
        s = s[:-3]
    grupos.append(s)
    return sep.join(reversed(grupos))
