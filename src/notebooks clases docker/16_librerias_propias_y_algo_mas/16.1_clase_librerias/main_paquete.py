"""
main_paquete.py
===============
Mismo resultado que main_simple.py, pero usando el paquete analitica.

Uso:
    python main_paquete.py
"""

from analitica.reportes import imprimir_resumen

ventas = [120, 135, 98, 150, 160, 89, 143, 127, 500, 115, 132, 141]

if __name__ == "__main__":
    imprimir_resumen("Ventas mensuales", ventas)
