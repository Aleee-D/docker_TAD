import os
import time
import pandas as pd
from sqlalchemy import create_engine, text

def test_mysql_connection():
    print("=" * 60)
    print("🐬 PROBANDO CONEXIÓN A MYSQL DESDE PYTHON")
    print("=" * 60)

    # Parámetros de conexión (desde variables de entorno o valores por defecto)
    host = "localhost" #os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "taller")
    password = os.getenv("DB_PASSWORD", "prog")
    database = os.getenv("DB_NAME", "taller_db")

    connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    print(f"🔗 Conectando a: {user}@{host}:{port}/{database}...")

    engine = create_engine(connection_url)

    # Intentar conexión con reintentos (útil si MySQL apenas está iniciando)
    connected = False
    for attempt in range(1, 11):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT VERSION();")).scalar()
                print(f"✅ Conexión exitosa a MySQL (Versión del servidor: {result})")
                connected = True
                break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print(f"⏳ Esperando que MySQL esté listo... (Intento {attempt}/10)")
            time.sleep(3)

    if not connected:
        print("❌ No se pudo conectar a MySQL. Asegúrate de que el contenedor 'db' esté corriendo.")
        return

    print("-" * 60)
    print("📊 Creando tabla de prueba e insertando datos con Pandas...")

    # Crear un DataFrame de ejemplo
    data = {
        "id": [1, 2, 3],
        "alumno": ["Lucas Martínez", "Sofía Pérez", "Martín Rossi"],
        "curso": ["Programación", "Bases de Datos", "Análisis de Datos"],
        "nota": [9.5, 8.0, 10.0]
    }
    df = pd.DataFrame(data)

    # Guardar en MySQL
    df.to_sql("alumnos_taller", con=engine, if_exists="replace", index=False)
    print("   Tabla 'alumnos_taller' guardada en la base de datos.")

    print("-" * 60)
    print("📥 Leyendo datos desde MySQL con pd.read_sql()...")

    # Leer de MySQL
    df_read = pd.read_sql("SELECT * FROM alumnos_taller", con=engine)
    print(df_read.to_string(index=False))

    print("=" * 60)
    print("✨ ¡MySQL y Python funcionando al 100%!")
    print("=" * 60)

if __name__ == "__main__":
    test_mysql_connection()
