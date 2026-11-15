"""
main_simple.py
==============
Ejemplo de uso del módulo analisis.py ejecutado directamente desde la terminal.

Uso:
    python main_simple.py
"""

import analisis


# ── Datos de ejemplo ──────────────────────────────────────────────
ventas = [120, 135, 98, 150, 160, 89, 143, 127, 500, 115, 132, 141]


def mostrar_resumen(nombre, datos):
    """Imprime un resumen estadístico formateado de una lista de datos."""
    stats = analisis.resumen(datos)
    atip  = analisis.detectar_outliers(datos)

    print(f"\n{'═' * 40}")
    print(f"  {nombre}")
    print(f"{'═' * 40}")
    print(f"  N        {analisis.formato_miles(stats['n'])}")
    print(f"  Media    {analisis.formato_moneda(stats['media'],   decimales=0)}")
    print(f"  Mediana  {analisis.formato_moneda(stats['mediana'], decimales=0)}")
    print(f"  Desvío   {analisis.formato_moneda(stats['desvio'],  decimales=0)}")
    print(f"  Mín      {analisis.formato_moneda(stats['minimo'],  decimales=0)}")
    print(f"  Máx      {analisis.formato_moneda(stats['maximo'],  decimales=0)}")
    print(f"  P25      {analisis.formato_moneda(stats['p25'],     decimales=0)}")
    print(f"  P75      {analisis.formato_moneda(stats['p75'],     decimales=0)}")

    if atip['outliers']:
        vals = ', '.join(analisis.formato_moneda(v, decimales=0) for v in atip['outliers'])
        print(f"\n  ⚠  Outliers: {vals}")
        print(f"     Rango normal: {analisis.formato_moneda(atip['limite_inf'], decimales=0)}"
              f" — {analisis.formato_moneda(atip['limite_sup'], decimales=0)}")
    else:
        print("\n  ✓  Sin outliers detectados.")


# ── Punto de entrada ──────────────────────────────────────────────
#
# if __name__ == "__main__" es la forma estándar de indicar
# "este bloque solo se ejecuta si corrés este archivo directamente".
#
# Si otro archivo hace  import main_simple,  este bloque NO se ejecuta.
# Eso permite que un .py sea tanto un módulo importable
# como un script ejecutable.
#
if __name__ == "__main__":
    mostrar_resumen("Ventas mensuales", ventas)
