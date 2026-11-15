"""
main_csv.py
===========
Analiza una columna numérica de un archivo CSV usando el módulo analisis.py.

Uso:
    python main_csv.py <archivo.csv> <columna>

Ejemplos:
    python main_csv.py ventas.csv monto
    python main_csv.py empleados.csv salario
"""

import sys
import os
import analisis

# Para leer el CSV usamos solo la librería estándar (csv),
# sin depender de pandas — así el script funciona en cualquier entorno.
import csv


def leer_columna(path, columna):
    """
    Lee una columna numérica de un archivo CSV.

    Retorna
    -------
    list de floats — los valores de la columna (se ignoran celdas vacías)

    Raises
    ------
    FileNotFoundError  : si el archivo no existe
    KeyError           : si la columna no existe en el CSV
    ValueError         : si la columna no contiene valores numéricos
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    valores = []
    with open(path, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)

        # Verificar que la columna existe
        if columna not in lector.fieldnames:
            disponibles = ', '.join(lector.fieldnames)
            raise KeyError(
                f"La columna '{columna}' no existe.\n"
                f"Columnas disponibles: {disponibles}"
            )

        for i, fila in enumerate(lector, start=2):   # start=2: fila 1 es el header
            celda = fila[columna].strip()
            if not celda:
                continue   # ignorar celdas vacías

            try:
                valores.append(float(celda.replace(',', '.')))
            except ValueError:
                print(f"  Advertencia: fila {i} tiene valor no numérico ('{celda}') — se ignora.")

    return valores


def main(path_csv, columna):
    print(f"\nArchivo : {path_csv}")
    print(f"Columna : {columna}")

    # Leer datos
    try:
        datos = leer_columna(path_csv, columna)
    except (FileNotFoundError, KeyError) as e:
        print(f"\nError: {e}")
        sys.exit(1)

    if len(datos) < 2:
        print(f"\nError: se necesitan al menos 2 valores numéricos (se encontraron {len(datos)}).")
        sys.exit(1)

    # Estadísticas
    stats = analisis.resumen(datos)
    atip  = analisis.detectar_outliers(datos)

    print(f"\n{'═' * 45}")
    print(f"  Resumen estadístico — {columna}")
    print(f"{'═' * 45}")
    print(f"  N        {analisis.formato_miles(stats['n'])}")
    print(f"  Media    {analisis.formato_moneda(stats['media'])}")
    print(f"  Mediana  {analisis.formato_moneda(stats['mediana'])}")
    print(f"  Desvío   {analisis.formato_moneda(stats['desvio'])}")
    print(f"  Mín      {analisis.formato_moneda(stats['minimo'])}")
    print(f"  Máx      {analisis.formato_moneda(stats['maximo'])}")
    print(f"  P25      {analisis.formato_moneda(stats['p25'])}")
    print(f"  P75      {analisis.formato_moneda(stats['p75'])}")

    if atip['outliers']:
        print(f"\n  ⚠  Outliers detectados ({len(atip['outliers'])}):")
        for v in atip['outliers']:
            print(f"       {analisis.formato_moneda(v)}")
        print(f"     Rango normal: {analisis.formato_moneda(atip['limite_inf'])}"
              f" — {analisis.formato_moneda(atip['limite_sup'])}")
    else:
        print("\n  ✓  Sin outliers detectados.")

    print()


# ── Punto de entrada ──────────────────────────────────────────────
if __name__ == "__main__":

    # sys.argv es la lista de argumentos que recibe el script:
    #   sys.argv[0]  →  nombre del script  ("main_csv.py")
    #   sys.argv[1]  →  primer argumento   ("ventas.csv")
    #   sys.argv[2]  →  segundo argumento  ("monto")

    if len(sys.argv) != 3:
        print("Uso: python main_csv.py <archivo.csv> <columna>")
        print()
        print("Ejemplo:")
        print("  python main_csv.py ventas.csv monto")
        sys.exit(1)

    main(
        path_csv=sys.argv[1],
        columna =sys.argv[2],
    )
