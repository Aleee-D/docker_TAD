
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
# 1. CLASE E_OBTENER (EXTRACCIÓN Y ARCHIVOS INTERMEDIOS)
# =============================================================================
class E_Obtener:
    """
    Clase de extracción de datos:
      - Encargada de obtener los datos dentro de los rangos desde las fuentes
        (API Polygon.io para Apple y Netflix; archivo CSV para Messi).
      - El método 'extraer_goles_messi_intermedio' filtra exclusivamente las fechas
        de los goles de Messi en la MLS.
      - Administra rutas y tickers mediante el diccionario de instancia 'self.activos'.
      - El método de obtención de Polygon recibe un elemento de ese diccionario.
      - Métodos 'guardar_intermedio' y 'obtener_intermedio' para persistir
        los archivos intermedios de Messi, Apple y Netflix.
    """

    def __init__(self):
        # 1. Variables de instancia operativas
        self.fecha_inicio: str = "2023-01-01"
        self.fecha_fin: str = "2026-12-31"
        self.api_key: str = "CLAVE"  # Reemplazar con tu clave de API de Polygon.io
        self.url_base_polygon: str = "https://api.polygon.io/v2/aggs/ticker"

        # 2. Diccionario de instancia con los tickers y sus carpetas asociadas
        self.activos: Dict[str, Dict[str, str]] = {
            "AAPL": {
                "ticker": "AAPL",
                "empresa": "Apple Inc.",
                "carpeta": os.path.join("datos", "apple"),
                "ruta_intermedia": os.path.join("datos", "apple", "acciones_apple_intermedio.pkl")
            },
            "NFLX": {
                "ticker": "NFLX",
                "empresa": "Netflix Inc.",
                "carpeta": os.path.join("datos", "netflix"),
                "ruta_intermedia": os.path.join("datos", "netflix", "acciones_netflix_intermedio.pkl")
            }
        }

        # Configuración de rutas para datos de Messi
        self.info_messi: Dict[str, str] = {
            "carpeta": os.path.join("datos", "messi"),
            "ruta_csv_origen": os.path.join("datos", "messi", "datos_goles_messi.csv"),
            "ruta_intermedia": os.path.join("datos", "messi", "goles_messi_intermedio.pkl")
        }

        # Cliente Polygon.io
        self.cliente_polygon = RESTClient(api_key=self.api_key)

    # -------------------------------------------------------------------------
    # Métodos de Guardar y Obtener Intermedio (Pertenecen a E_Obtener)
    # -------------------------------------------------------------------------
    def guardar_intermedio(self, df: pd.DataFrame, ruta_archivo: str) -> str:
        """
        Guarda un DataFrame intermedio en formato Pickle (.pkl),
        creando la carpeta de destino si no existe y optimizando enteros.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El objeto intermedio a guardar debe ser un pandas.DataFrame.")

        carpeta = os.path.dirname(ruta_archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        df_opt = optimizar_enteros_ram(df)
        df_opt.to_pickle(ruta_archivo)

        tamano_kb = os.path.getsize(ruta_archivo) / 1024.0
        print(f"  -> [E_Obtener] Archivo intermedio guardado: '{ruta_archivo}' ({len(df_opt)} registros, {tamano_kb:.2f} KB).")
        return ruta_archivo

    def obtener_intermedio(self, ruta_archivo: str) -> pd.DataFrame:
        """
        Recupera un DataFrame intermedio previamente serializado en Pickle.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No existe el archivo intermedio en: '{ruta_archivo}'")

        df = pd.read_pickle(ruta_archivo)

        print(f"  -> [E_Obtener] Archivo intermedio leído: '{ruta_archivo}' ({len(df)} registros cargados).")
        return df

    # -------------------------------------------------------------------------
    # Extracción de Datos desde Polygon.io (Recibe un elemento del diccionario)
    # -------------------------------------------------------------------------
    def obtener_datos_polygon(self, empresa: Dict[str, str]) -> pd.DataFrame:
        """
        Obtiene los datos desde la API de Polygon.io utilizando su iterador nativo.
        Recibe como parámetro un elemento del diccionario 'self.activos',
        por lo que no se requiere validar ningún string ingresado.
        """
        ticker = empresa['ticker']
        ruta_intermedia = empresa['ruta_intermedia']
        print(f"[E_Obtener] Extrayendo desde fuente Polygon.io para activo '{ticker}' (carpeta: '{empresa['carpeta']}')...")

        registros = []
        try:
            # Iterador nativo ofrecido por la API de Polygon.io
            aggs_iter = self.cliente_polygon.get_aggs(
                    ticker=empresa['ticker'], multiplier=1, timespan='day',
                    from_=self.fecha_inicio, to=self.fecha_fin, adjusted=True
                )
            #OBTENER EL ITERADOR DE LA API 
            #PASANDO LOS PARÁMETROS DE LA CONSULTA 

            
            for agg in aggs_iter:
                try:
                    #CONVERTIR LAS FECHAS DEVUELTAS A TIPO FECHA 
                    #CONVERTIR A FLOAT LOS VALORES DE VALOR DE CIERRE DE LA ACCIÓN EN ESE DÍA
                    #GUADRAR LOS VALORES EN UNA LISTA DE REGISTROS
                    dt_str = pd.to_datetime(agg.timestamp, unit="ms").strftime("%Y-%m-%d")
                    registros.append({
                        "fecha": dt_str,
                        "cierre": float(agg.close),
                    })
                    
                except StopIteration:
                    break

            if registros:
                print(f"  -> [E_Obtener] {len(registros)} registros extraídos directamente de Polygon.io para {ticker}.")

        except Exception as err:
            print(f"  [E_Obtener] Aviso sobre API Polygon.io ({ticker}): {err}")
        
        df_empresa = pd.DataFrame(registros)
        print(df_empresa.head())
        if(df_empresa.empty):
            raise ValueError(f"No se encontraron datos de {ticker} en el período especificado {self.fecha_inicio} - {self.fecha_fin}.")

        # Guardar en el archivo intermedio de esta fuente
        self.guardar_intermedio(df_empresa, ruta_intermedia)
        return df_empresa

    # -------------------------------------------------------------------------
    # Extracción Exclusiva de Fechas de Goles de Messi en MLS (Filtro Requerido)
    # -------------------------------------------------------------------------
    def extraer_goles_messi_intermedio(self) -> pd.DataFrame:
        """
        Lee el archivo CSV de goles de Messi iterando en bloques de self.batch_size
        mediante la variable interna de instancia,
        filtrando EXCLUSIVAMENTE los goles de Messi en la MLS en el período evaluado,
        y extrayendo las fechas correspondientes para el archivo intermedio.
        """
        ruta_csv = self.info_messi["ruta_csv_origen"]
        ruta_intermedia = self.info_messi["ruta_intermedia"]
        print(f"[E_Obtener] Extrayendo del CSV exclusivamente las fechas de goles de Messi en la MLS ...")

        #COMPROBAR SI EL ARCHIVO EXISTE, SINO LANZAR EXEPCION FILENOTFOUNDERROR
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No existe el archivo de goles origen: '{ruta_csv}'")

        #LEER EL ARCHIVO ORIGEN CSV Y QUEDARSE CON LOS DATOS DE FECHA Y COMPETICION. 
        df_completo = pd.read_csv(ruta_csv)
        total_filas = len(df_completo)
        
        #CONVERTIR LAS FECHAS A FORMATO FECHA PARA PODER USAR UNA MÁSCARA
        #CREAR FILTRO POR LAS FECHAS DEFINIDAS EN EL OBJETIVO DEL PIPELINE Y POR LA COMPETICIÓN "MLS"

        # FILTRO SOLICITADO: Solo goles en MLS y sus fechas dentro del rango 2023-2026
        if "Fecha" in df_completo.columns and "Competicion" in df_completo.columns:
            df_completo["Fecha"] = pd.to_datetime(df_completo["Fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
            mascara_mls = df_completo["Competicion"].str.upper() == "MLS"
            mascara_fechas = (df_completo["Fecha"] >= self.fecha_inicio) & (df_completo["Fecha"] <= self.fecha_fin)
            bloque_mls = df_completo[mascara_mls & mascara_fechas][["Fecha", "Competicion"]].copy()
    
        print(f"[E_Obtener] Filtro MLS aplicado en la extracción: {len(bloque_mls)} registros de goles en MLS obtenidos.")
        print(bloque_mls.head())
        
        # Guardar en archivo intermedio de Messi
        self.guardar_intermedio(bloque_mls, ruta_intermedia)
        return bloque_mls
