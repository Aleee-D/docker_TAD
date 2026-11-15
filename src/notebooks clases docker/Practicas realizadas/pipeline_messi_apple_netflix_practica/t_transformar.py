
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


# =============================================================================
# FUNCIÓN AUXILIAR DE OPTIMIZACIÓN DE MEMORIA RAM
# =============================================================================
def optimizar_enteros_ram(df: pd.DataFrame) -> pd.DataFrame:
    """
    Homogeniza las columnas de tipo número entero al menor subtipo posible
    (int8, int16, int32, int64 o unsigned) para minimizar el consumo de memoria RAM.
    """
    df_opt = df.copy()
    for col in df_opt.columns:
        if pd.api.types.is_integer_dtype(df_opt[col]):
            df_opt[col] = pd.to_numeric(df_opt[col], downcast="integer")
        elif pd.api.types.is_float_dtype(df_opt[col]):
            if not df_opt[col].isna().any():
                if (df_opt[col] % 1 == 0).all():
                    df_opt[col] = pd.to_numeric(df_opt[col], downcast="integer")
    return df_opt

# =============================================================================
# 2. CLASE T_TRANSFORMAR (TRANSFORMACIÓN Y APROXIMACIONES LINEALES)
# =============================================================================
class T_Transformar:
    """
    Clase encargada de la homogenización, transformación y de rellenar datos faltantes:
      - Contiene un método específico para rellenar datos faltantes para CADA fuente:
          * rellenar_datos_faltantes_messi()
          * rellenar_datos_faltantes_apple()
          * rellenar_datos_faltantes_netflix()
      - El relleno de Apple y Netflix se realiza mediante APROXIMACIONES LINEALES
        (interpolate lineal) entre los días que tienen valor sobre los valores NaN
        del dataframe obtenido en E_Obtener.
      - Aplica el groupby de Pandas sobre fechas sumando goles.
      - Homogeniza los tipos de números enteros al menor posible (int8, int32) para ahorrar RAM.
    """

    def __init__(self, extractor: Optional[E_Obtener] = None):
        self.extractor = extractor or E_Obtener()
        self.fecha_inicio: str = self.extractor.fecha_inicio
        self.fecha_fin: str = self.extractor.fecha_fin

    # -------------------------------------------------------------------------
    # Método 1: Rellenar datos faltantes para MESSI
    # -------------------------------------------------------------------------
    def rellenar_datos_faltantes_messi(self, df_messi_intermedio: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia, valida fechas y aplica groupby sobre fechas sumando los goles
        de Messi para cada encuentro de la MLS.
        """
        print("[T_Transformar] Ejecutando 'rellenar_datos_faltantes_messi'...")
        df = df_messi_intermedio.copy()

        # Cada fila extraída representa 1 gol anotado en MLS
        df["Goles"] = 1

        # =====================================================================
        # GROUPBY DE PANDAS SOBRE FECHAS SUMANDO GOLES
        # =====================================================================
        df_goles_sumados = df.groupby("Fecha", as_index=False).agg(
            Goles_Messi=("Goles", "sum")
        )

        # Homogenizar número entero de goles al menor tipo (int8)
        df_goles_sumados["Goles_Messi"] = pd.to_numeric(df_goles_sumados["Goles_Messi"], downcast="integer")
        print(f"  -> [T_Transformar] Messi: {len(df_goles_sumados)} fechas únicas consolidadas con goles sumados.")
        return df_goles_sumados

    # -------------------------------------------------------------------------
    # Método 2: Rellenar datos faltantes para APPLE (APROXIMACIÓN LINEAL)
    # -------------------------------------------------------------------------
    def rellenar_datos_faltantes_apple(self, df_apple_obtenido: pd.DataFrame, df_goles_sumados: pd.DataFrame) -> pd.DataFrame:
        """
        Rellena los valores bursátiles de Apple mediante APROXIMACIONES LINEALES
        entre los días que tienen valor sobre los valores NaN del dataframe
        con los datos obtenidos en E_Obtener.
        """
        print("[T_Transformar] Ejecutando 'rellenar_datos_faltantes_apple' con aproximación lineal sobre NaNs...")

        if ("Fecha" in df_goles_sumados):
            df_goles_sumados.rename(columns={"Fecha": "fecha"}, inplace=True)
        
        if(df_apple_obtenido.empty):
            raise ValueError("No se encontraron datos de Apple en el período especificado.")

        # Combinar calendario con los datos obtenidos en E_Obtener (los días sin cotización serán NaN)
        df_con_nans = pd.merge(df_apple_obtenido,df_goles_sumados[["fecha", "Goles_Messi"] ], on="fecha", how="outer")
        
        # =====================================================================
        # APROXIMACIÓN LINEAL ENTRE DÍAS CON VALOR SOBRE LOS VALORES NaN
        # =====================================================================
        df_con_nans["cierre"] = df_con_nans["cierre"].interpolate(method="linear").bfill().ffill()
        df_con_nans["cierre"] = np.round(df_con_nans["cierre"], 2)
        
        # Homogenizar enteros para minimizar consumo de RAM
        df_resultado = optimizar_enteros_ram(df_con_nans)
        print(f"  -> [T_Transformar] Apple: {len(df_resultado)} días completados por aproximación lineal.")
        return df_resultado

    # -------------------------------------------------------------------------
    # Método 3: Rellenar datos faltantes para NETFLIX (APROXIMACIÓN LINEAL)
    # -------------------------------------------------------------------------
    def rellenar_datos_faltantes_netflix(self, df_netflix_obtenido: pd.DataFrame, df_goles_sumados: pd.DataFrame) -> pd.DataFrame:
        """
        Rellena los valores bursátiles de Netflix mediante APROXIMACIONES LINEALES
        entre los días que tienen valor sobre los valores NaN del dataframe
        con los datos obtenidos en E_Obtener.
        """
        print("[T_Transformar] Ejecutando 'rellenar_datos_faltantes_netflix' con aproximación lineal sobre NaNs...")

        if ("Fecha" in df_goles_sumados):
            df_goles_sumados.rename(columns={"Fecha": "fecha"}, inplace=True)
        
        # Combinar calendario con los datos obtenidos en E_Obtener
        if(df_netflix_obtenido.empty):
            raise ValueError("No se encontraron datos de Netflix en el período especificado.")
        
        df_con_nans = pd.merge(df_netflix_obtenido,df_goles_sumados[["fecha", "Goles_Messi"]], on="fecha", how="outer")
        
        # =====================================================================
        # APROXIMACIÓN LINEAL ENTRE DÍAS CON VALOR SOBRE LOS VALORES NaN
        # =====================================================================
        df_con_nans["cierre"] = df_con_nans["cierre"].interpolate(method="linear").bfill().ffill()
        df_con_nans["cierre"] = np.round(df_con_nans["cierre"], 2)
        
        df_resultado = optimizar_enteros_ram(df_con_nans)
        print(f"  -> [T_Transformar] Netflix: {len(df_resultado)} días completados por aproximación lineal.")
        return df_resultado

    # -------------------------------------------------------------------------
    # Proceso de Transformación Integral y Cruce con Valores de Cierre
    # -------------------------------------------------------------------------
    def transformar_datos(
        self,
        df_messi_intermedio: pd.DataFrame,
        df_apple_intermedio: pd.DataFrame,
        df_netflix_intermedio: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Ejecuta el relleno de datos faltantes por fuente con aproximaciones lineales,
        cruza los goles sumados por fecha con los valores de CIERRE de las acciones
        y produce el DataFrame final consolidado.
        """
        print("\n[T_Transformar] Iniciando homogenización, aproximaciones lineales y cruce...")

        # 1. Relleno por fuente con aproximaciones lineales
        df_goles = self.rellenar_datos_faltantes_messi(df_messi_intermedio)
        df_apple = self.rellenar_datos_faltantes_apple(df_apple_intermedio, df_goles)
        df_netflix = self.rellenar_datos_faltantes_netflix(df_netflix_intermedio, df_goles)
        
        df_apple.rename(columns={"cierre": "Apple_Precio_Cierre"}, inplace=True)
        df_netflix.rename(columns={"cierre": "Netflix_Precio_Cierre"}, inplace=True)
        
        df_final = pd.merge(pd.merge(df_goles, df_apple, on='fecha', how='outer'), df_netflix, on='fecha', how='outer')
            
        df_final.rename(columns={"fecha": "Fecha_Partido"}, inplace=True)
        df_final["Fecha_Partido"] = pd.to_datetime(df_final["Fecha_Partido"])
        df_final = df_final.sort_values(by="Fecha_Partido").reset_index(drop=True)

        # Optimización final de memoria RAM en enteros
        df_final = optimizar_enteros_ram(df_final)

        print(f"[T_Transformar] Transformación finalizada: {len(df_final)} partidos vinculados a valores de cierre de Apple y Netflix.")
        return df_final
