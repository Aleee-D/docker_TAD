"""
analitica
=========
Paquete de utilidades para análisis y formateo de datos numéricos.

Es la evolución de analisis.py: en vez de un solo archivo con todo,
las funciones están repartidas en submódulos según su tema.

Estructura
----------
analitica/
├── __init__.py        ← este archivo: convierte la carpeta en paquete
├── estadisticas.py    ← resumen, detectar_outliers, normalizar
├── formateo.py        ← formato_moneda, formato_porcentaje, formato_miles
├── _utils.py          ← helpers internos (privado)
└── reportes/          ← subpaquete
    ├── __init__.py
    └── consola.py     ← imprimir_resumen
"""

# Re-exportamos lo más usado para que se pueda escribir
#     from analitica import resumen
# en lugar de
#     from analitica.estadisticas import resumen
from .estadisticas import resumen, detectar_outliers, normalizar
from .formateo import formato_moneda, formato_porcentaje, formato_miles

__all__ = [
    'resumen',
    'detectar_outliers',
    'normalizar',
    'formato_moneda',
    'formato_porcentaje',
    'formato_miles',
]

__version__ = '0.1.0'

print(f"[analitica] paquete inicializado (v{__version__})")
