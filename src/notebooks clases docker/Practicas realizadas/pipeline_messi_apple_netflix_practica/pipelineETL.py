
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

import e_obtener 
import t_transformar 
import l_cargar 


# =============================================================================
# 4. CLASE PIPELINEETL (ORQUESTACIÓN Y GRÁFICO FINAL CONJUNTO)
# =============================================================================
class PipelineETL:
    """
    Clase orquestadora principal:
      1. Utiliza E_Obtener para extraer desde las fuentes y crear los 3 archivos
         intermedios (Apple, Netflix y Messi con filtro MLS).
      2. Utiliza T_Transformar para rellenar datos faltantes mediante aproximaciones
         lineales sobre los valores de E_Obtener y agrupar goles por fecha.
      3. Utiliza L_Cargar para guardar y recuperar el archivo final consolidado.
      4. Genera el gráfico conjunto: BARRAS para goles de Messi y LÍNEAS SUPERPUESTAS
         para los valores de CIERRE de Apple y Netflix.
    """

    def __init__(self):
        self.fecha_inicio: str = "2023-01-01"
        self.fecha_fin: str = "2026-12-31"
        self.ruta_grafico: str = "grafico_messi_apple_netflix.png"

        # Instancias de componentes con los nuevos nombres de clase
        self.extractor = e_obtener.E_Obtener()
        self.cargador = l_cargar.L_Cargar()
        self.transformador = t_transformar.T_Transformar(extractor=self.extractor)

    def ejecutar_pipeline(self) -> pd.DataFrame:
        """
        Ejecuta el pipeline completo cumpliendo todas las directrices:
          - E_Obtener extrae y crea los archivos intermedios de Messi (filtrando MLS), Apple y Netflix.
          - T_Transformar rellena datos faltantes con aproximaciones lineales y agrupa por fecha.
          - L_Cargar persiste el resultado final en Pickle.
        """
        print("\n" + "=" * 80)
        print("EJECUTANDO PIPELINE ETL (CLASES: E_Obtener, T_Transformar, L_Cargar)")
        print("=" * 80)

        # ---------------------------------------------------------------------
        # Configuración del pipeline
        # ---------------------------------------------------------------------
        ObtenerDatos = False
        TransformarDatos = True
        CargarDatos = True


        if (ObtenerDatos == True):    
            # ---------------------------------------------------------------------
            # FASE 1: E_Obtener genera archivos intermedios para cada fuente
            # ---------------------------------------------------------------------
            print("\n[Fase 1 - Extracción y Archivos Intermedios (E_Obtener)]")

            # Pasar directamente los elementos del diccionario 'self.extractor.activos'
            for ticker_key, activo_dict in self.extractor.activos.items():
                self.extractor.obtener_datos_polygon(activo_dict)

            # Extraer exclusivamente goles de Messi en MLS y generar intermedio
            self.extractor.extraer_goles_messi_intermedio()
        else:
            print("\n[Fase 1 - Extracción y Archivos Intermedios (E_Obtener)] SALTEADA")

        if (TransformarDatos == True):
            # ---------------------------------------------------------------------
            # FASE 2: T_Transformar carga intermedios, aplica aproximaciones lineales y transforma
            # ---------------------------------------------------------------------
            print("\n[Fase 2 - Carga de Intermedios y Transformación (T_Transformar)]")

            # Cargar los intermedios usando los métodos de E_Obtener
            df_messi_inter = self.extractor.obtener_intermedio(self.extractor.info_messi["ruta_intermedia"])
            df_apple_inter = self.extractor.obtener_intermedio(self.extractor.activos["AAPL"]["ruta_intermedia"])
            df_netflix_inter = self.extractor.obtener_intermedio(self.extractor.activos["NFLX"]["ruta_intermedia"])

            # Transformar aplicando aproximaciones lineales sobre los datos obtenidos
            df_final = self.transformador.transformar_datos(
                df_messi_intermedio=df_messi_inter,
                df_apple_intermedio=df_apple_inter,
                df_netflix_intermedio=df_netflix_inter
            )
        else:
            print("\n[Fase 2 - Carga de Intermedios y Transformación (T_Transformar)] SALTEADA")

        if (CargarDatos == True):
            # ---------------------------------------------------------------------
            # FASE 3: L_Cargar persiste y valida el archivo final
            # ---------------------------------------------------------------------
            print("\n[Fase 3 - Persistencia del Dataset Final (L_Cargar)]")
            self.cargador.guardar_datos_finales(df_final)

            df_recuperado = self.cargador.cargar_datos_finales()

            print("\n" + "=" * 80)
            print("SE RECUPERARON LOS DATOS PROSESADOS")
            print("=" * 80)
        
            return df_recuperado
        else:
            print("\n[Fase 3 - Persistencia del Dataset Final (L_Cargar)] SALTEADA")


        print("\n" + "=" * 80)
        print("PIPELINE ETL FINALIZADO")
        print("=" * 80)
        
        return None

    def generar_grafico_conjunto(self) -> Dict[str, Any]:
        """
        Genera el gráfico conjunto:
          - BARRAS para los goles de Messi (sumados por fecha).
          - LÍNEAS SUPERPUESTAS con los valores de CIERRE de Apple y Netflix.
        """
        print("\n" + "=" * 80)
        print("GENERANDO GRÁFICO CONJUNTO (BARRAS GOLES + LÍNEAS VALORES DE CIERRE)")
        print("=" * 80)

        df = self.cargador.cargar_datos_finales()
        if df.empty:
            raise ValueError("El DataFrame cargado está vacío.")

        fechas = df["Fecha_Partido"].dt.to_pydatetime()
        goles = df["Goles_Messi"].values
        cierre_apple = df["Apple_Precio_Cierre"].values
        cierre_netflix = df["Netflix_Precio_Cierre"].values

        sns.set_theme(style="whitegrid")
        fig, ax_izq = plt.subplots(figsize=(16, 8))

        # 1. BARRAS: Goles de Messi (Eje Izquierdo)
        ancho_barra = timedelta(days=10)
        barras_goles = ax_izq.bar(
            fechas,
            goles,
            width=ancho_barra,
            color="#FFB300",
            alpha=0.60,
            edgecolor="#E65100",
            linewidth=1.3,
            label="Goles de Messi (MLS - Suma por Fecha)"
        )
        ax_izq.set_ylabel("Goles de Messi (Suma por Partido)", fontsize=13, fontweight="bold", color="#E65100")
        ax_izq.set_ylim(0, 4)
        ax_izq.set_yticks([0, 1, 2, 3])
        ax_izq.tick_params(axis="y", labelcolor="#E65100", labelsize=11)
        ax_izq.set_xlabel("Fecha del Partido MLS (2023 - 2026)", fontsize=13, fontweight="bold", labelpad=10)

        # 2. LÍNEA SUPERPUESTA 1: Valor de Cierre Apple AAPL (Eje Derecho 1)
        ax_der_apple = ax_izq.twinx()
        linea_apple, = ax_der_apple.plot(
            fechas,
            cierre_apple,
            color="#007AFF",
            linewidth=2.8,
            marker="o",
            markersize=6,
            label="Apple AAPL - Valor de Cierre ($ USD)"
        )
        ax_der_apple.set_ylabel("Cierre Apple AAPL ($ USD)", color="#007AFF", fontsize=12, fontweight="bold")
        ax_der_apple.tick_params(axis="y", labelcolor="#007AFF", labelsize=11)
        ax_der_apple.grid(False)

        # 3. LÍNEA SUPERPUESTA 2: Valor de Cierre Netflix NFLX (Eje Derecho 2 desplazado)
        ax_der_netflix = ax_izq.twinx()
        ax_der_netflix.spines["right"].set_position(("axes", 1.07))
        linea_netflix, = ax_der_netflix.plot(
            fechas,
            cierre_netflix,
            color="#E50914",
            linewidth=2.8,
            marker="s",
            markersize=6,
            linestyle="--",
            label="Netflix NFLX - Valor de Cierre ($ USD)"
        )
        ax_der_netflix.set_ylabel("Cierre Netflix NFLX ($ USD)", color="#E50914", fontsize=12, fontweight="bold")
        ax_der_netflix.tick_params(axis="y", labelcolor="#E50914", labelsize=11)
        ax_der_netflix.grid(False)

        # Formato de fechas en eje X
        ax_izq.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax_izq.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        fig.autofmt_xdate(rotation=30)

        plt.title(
            "Gráfico Conjunto: Goles de Messi (Barras) y Valores de Cierre Superpuestos de Apple y Netflix (2023-2026)",
            fontsize=15, fontweight="bold", pad=15
        )

        elementos = [barras_goles, linea_apple, linea_netflix]
        etiquetas = [elem.get_label() for elem in elementos]
        ax_izq.legend(elementos, etiquetas, loc="upper left", framealpha=0.92, fontsize=11)

        plt.tight_layout()
        plt.savefig(self.ruta_grafico, dpi=300, bbox_inches="tight")
        print(f"\n[PipelineETL] Gráfico guardado exitosamente en: '{self.ruta_grafico}'")
        plt.close()
