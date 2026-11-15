"""
__main__.py
===========
Se ejecuta cuando corrés el paquete como programa:

    python -m analitica
"""

from .reportes import imprimir_resumen

imprimir_resumen("Demo del paquete analitica", [120, 135, 98, 150, 160, 89, 500])
