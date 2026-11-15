"""
consola.py
==========
Submódulo de analitica.reportes: reportes impresos en la terminal.

Muestra cómo un submódulo usa funciones de OTROS submódulos del
paquete padre, con imports relativos de dos puntos (..).
"""

# ..  = "subir un nivel" → el paquete analitica
from ..estadisticas import resumen, detectar_outliers
from ..formateo import formato_moneda, formato_miles

__all__ = ['imprimir_resumen']


def imprimir_resumen(nombre, datos, simbolo='$', decimales=0, ancho=40):
    """
    Imprime un resumen estadístico formateado de una lista de números.

    Es la lógica que antes estaba repetida en main_simple.py y main_csv.py.
    """
    stats = resumen(datos)

    def m(v):
        return formato_moneda(v, simbolo=simbolo, decimales=decimales)

    print(f"\n{'═' * ancho}")
    print(f"  {nombre}")
    print(f"{'═' * ancho}")
    print(f"  N        {formato_miles(stats['n'])}")
    print(f"  Media    {m(stats['media'])}")
    print(f"  Mediana  {m(stats['mediana'])}")
    print(f"  Desvío   {m(stats['desvio'])}")
    print(f"  Mín      {m(stats['minimo'])}")
    print(f"  Máx      {m(stats['maximo'])}")
    print(f"  P25      {m(stats['p25'])}")
    print(f"  P75      {m(stats['p75'])}")

    if len(datos) >= 4:
        atip = detectar_outliers(datos)
        if atip['outliers']:
            vals = ', '.join(m(v) for v in atip['outliers'])
            print(f"\n  ⚠  Outliers: {vals}")
            print(f"     Rango normal: {m(atip['limite_inf'])} — {m(atip['limite_sup'])}")
        else:
            print("\n  ✓  Sin outliers detectados.")

