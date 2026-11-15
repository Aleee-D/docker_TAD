"""
config.py
=========
Módulo de configuración del proyecto.

Carga las variables del archivo .env UNA sola vez y las expone como
constantes. El resto del código hace:

    from config import POLYGON_API_KEY

y nunca necesita saber de dónde salió la clave.
"""

import os
from dotenv import load_dotenv

__all__ = ['POLYGON_API_KEY', 'DB', 'MODO_DEBUG', 'ocultar']

# Busca el archivo .env (en la carpeta actual o en las de arriba)
# y carga sus variables en os.environ
load_dotenv()


# ── Helpers privados ──────────────────────────────────────────────
def _requerida(nombre):
    """Devuelve una variable obligatoria o corta con un mensaje claro."""
    valor = os.getenv(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno '{nombre}'.\n"
            f"Revisá que exista el archivo .env y que tenga {nombre}=..."
            f"\n(usá .env.example como plantilla)"
        )
    return valor


def _booleana(nombre, default=False):
    """Interpreta 'true', '1', 'si', 'yes' como True. Todo es texto en un .env."""
    valor = os.getenv(nombre)
    if valor is None:
        return default
    return valor.strip().lower() in ('true', '1', 'si', 'sí', 'yes')


# ── Función pública ───────────────────────────────────────────────
def ocultar(secreto, visibles=4):
    """Muestra solo los últimos caracteres de un secreto: '********ab12'."""
    if not secreto:
        return '(vacío)'
    return '*' * max(len(secreto) - visibles, 4) + secreto[-visibles:]


# ── Configuración del proyecto ────────────────────────────────────
POLYGON_API_KEY = _requerida('POLYGON_API_KEY')

DB = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'port':     int(os.getenv('DB_PORT', '3306')),   # siempre llega como str
    'user':     os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', ''),
}

MODO_DEBUG = _booleana('MODO_DEBUG')
