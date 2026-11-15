"""
=============================================================================
PIPELINE ETL: RELACIÓN ENTRE GOLES DE MESSI, ACCIONES DE APPLE (AAPL) Y NETFLIX (NFLX)
=============================================================================

Consideraciones de diseño de esta versión:
  1. Nombres de clases actualizados:
     - E_Obtener: Clase de extracción y gestión de archivos intermedios.
     - T_Transformar: Clase de homogenización, transformación y relleno de faltantes.
     - L_Cargar: Clase de persistencia y carga del dataset final en Pickle.
     - PipelineETL: Clase orquestadora y generadora del gráfico conjunto.
  2. Filtro en 'extraer_goles_messi_intermedio':
     - Filtra directamente en el método de extracción del CSV exclusivamente
       las fechas de los goles de Lionel Messi en la MLS.
  3. Métodos de guardar y obtener archivos intermedios en E_Obtener:
     - 'guardar_intermedio' y 'obtener_intermedio' pertenecen a E_Obtener.
     - Administra tickers y rutas mediante el diccionario de instancia 'self.activos'.
     - Los métodos de obtención reciben un elemento de ese diccionario sin validar strings.
  4. Relleno de datos faltantes con aproximaciones lineales en T_Transformar:
     - 'rellenar_datos_faltantes_messi'
     - 'rellenar_datos_faltantes_apple'
     - 'rellenar_datos_faltantes_netflix'
     - Los rellenos de valores bursátiles para Netflix y Apple se realizan
       mediante APROXIMACIONES LINEALES (interpolate lineal) entre los días que
       tienen valor sobre los valores NaN del dataframe obtenido en E_Obtener.
  5. Agrupación por fechas sumando goles (groupby) y valores de CIERRE para el gráfico:
     - Gráfico de BARRAS para goles de Messi (suma por fecha).
     - LÍNEAS SUPERPUESTAS con los valores de CIERRE de Apple y Netflix ($ USD).

Período evaluado: 2023 a 2026.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from xmlrpc import client

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Iterador oficial de Polygon.io
from polygon import RESTClient

import pipelineETL

# =============================================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    pipeline = pipelineETL.PipelineETL()
    df_resultado = pipeline.ejecutar_pipeline()
    pipeline.generar_grafico_conjunto()
