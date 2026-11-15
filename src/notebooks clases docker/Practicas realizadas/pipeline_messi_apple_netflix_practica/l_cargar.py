    
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
# 3. CLASE L_CARGAR (PERSISTENCIA Y RECUPERACIÓN DEL ARCHIVO FINAL)
# =============================================================================
class L_Cargar:
    """
    Clase encargada de guardar el archivo consolidado final en formato Pickle (.pkl)
    y de recuperarlo para el análisis y graficación.
    """

    def __init__(self, ruta_archivo_final: str = "datos/datos_messi_apple_netflix.pkl"):
        self.ruta_archivo_final: str = ruta_archivo_final

    def guardar_datos_finales(self, df: pd.DataFrame) -> str:
        """Serializa el dataset final en Pickle optimizando enteros."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El objeto final debe ser un pandas.DataFrame.")

        df_opt = optimizar_enteros_ram(df)
        with open(self.ruta_archivo_final, "wb") as f:
            pickle.dump(df_opt, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        tamano_kb = os.path.getsize(self.ruta_archivo_final) / 1024.0
        print(f"[L_Cargar] Dataset final guardado en Pickle: '{self.ruta_archivo_final}' ({len(df_opt)} filas, {tamano_kb:.2f} KB).")
        return self.ruta_archivo_final

    def cargar_datos_finales(self) -> pd.DataFrame:
        """Carga el dataset final desde Pickle."""
        if not os.path.exists(self.ruta_archivo_final):
            raise FileNotFoundError(f"No existe el archivo final: '{self.ruta_archivo_final}'")

        with open(self.ruta_archivo_final, "rb") as f:
            df = pickle.load(f)

        print(f"[L_Cargar] Dataset final recuperado desde Pickle: '{self.ruta_archivo_final}' ({len(df)} registros).")
        return df

