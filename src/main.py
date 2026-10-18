import sys
import platform
import numpy as np
import pandas as pd

def check_environment():
    print("=" * 60)
    print("🚀 TALLER DE PROGRAMACIÓN PARA EL ANÁLISIS DE DATOS")
    print("(Entorno Docker con Python, NumPy y Pandas)")
    print("=" * 60)
    print("")
    print("💡 Formulario de prácticas: https://forms.gle/q36nFbf57SV478jC6")
    print("📘 Documento para compartir código: https://docs.google.com/document/d/1P_42pI1_uirrkjG00srADOwN6wXDWTllP03ksSLmiRo")
    print("📂 Carpeta de prácticas: https://drive.google.com/open?id=16o7yJ72GUeV0L6SxkvfnT4BoUFTL8b6J")
    print("")
    print("-" * 60)
    # 1. Información del Sistema y Python
    print(f"🐍 Versión de Python: {sys.version.split()[0]}")
    print(f"💻 Sistema Operativo: {platform.system()} {platform.release()} ({platform.machine()})")
    
    # 2. Información de Memoria RAM disponible para el contenedor
    try:
        # En Linux (dentro del contenedor), podemos consultar cgroups v2
        with open("/sys/fs/cgroup/memory.max", "r") as f:
            mem_max = f.read().strip()
            if mem_max != "max":
                mem_gb = int(mem_max) / (1024 ** 3)
                print(f"🧠 Límite de RAM cgroups: {mem_gb:.2f} GB")
    except Exception:
        pass
    print("-" * 60)
    print("")
    print("=" * 60)
    print("✨ Todo listo para programar. ¡Puedes crear y editar tus scripts aquí!")
    print("=" * 60)

if __name__ == "__main__":
    check_environment()
