# 🐳 Entorno Portátil de Desarrollo Python en Docker (VS Code)

Este proyecto provee un entorno de desarrollo profesional, aislado y 100% portátil basado en **Docker** y optimizado para **Visual Studio Code (Dev Containers)**.

Incluye **Python 3.11**, **NumPy**, **Pandas** y soporte para **Jupyter Notebooks**, con permisos configurados para instalar cualquier librería adicional sobre la marcha.

---

## 📋 Características Principales

- **Multiplataforma y Portátil:** Funciona idénticamente en **Windows**, **macOS** (Intel y Apple Silicon M1/M2/M3/M4) y **Linux**.
- **Límites de Recursos:**
  - **RAM:** 2 GB fijados estrictamente vía cgroups (`mem_limit: 2g`).
  - **Disco:** Parámetro `storage_opt` prefijado en 2 GB para la capa de escritura del contenedor. Tu código reside en la carpeta `src/` del host para no saturar el contenedor y garantizar la persistencia.
- **Permisos de Usuario:** Configurado con el usuario no-root `vscode` (UID 1000) con acceso `sudo` y propiedad sobre `/usr/local`, permitiendo instalar librerías con `pip install` sin errores de permisos.
- **Integración con VS Code:** Extensiones de Python, Pylance y Jupyter listas para usar en cuanto abres el contenedor.

---

## 📁 Estructura del Proyecto

```text
docker-python-dev/
├── .devcontainer/
│   └── devcontainer.json   # Configuración para la extensión Dev Containers de VS Code
├── src/
│   └── main.py             # Tu código fuente (se sincroniza en tiempo real con el contenedor)
├── .dockerignore           # Archivos ignorados por Docker para mantener la imagen ligera
├── Dockerfile              # Definición de la imagen del contenedor (Python + herramientas del sistema)
├── docker-compose.yml      # Orquestación de servicios, volúmenes y límites de RAM/Disco
├── requirements.txt        # Librerías de Python instaladas por defecto
└── README.md               # Esta guía
```

---

## 🚀 Requisitos Previos

1. **Docker Desktop** (o Docker Engine en Linux):
   - **Windows:** Instalar [Docker Desktop](https://www.docker.com/products/docker-desktop/) asegurándote de usar el motor **WSL 2**.
   - **macOS:** Instalar [Docker Desktop](https://www.docker.com/products/docker-desktop/) (compatible con Intel o Apple Silicon).
   - **Linux:** Instalar `docker-ce` y `docker-compose-plugin`.
2. **Visual Studio Code:**
   - Descarga e instala [VS Code](https://code.visualstudio.com/).
   - Instala la extensión oficial **[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)** (`ms-vscode-remote.remote-containers`).

---

## 🛠️ Modo 1: Desarrollo con VS Code (Recomendado)

Esta es la forma más productiva y moderna: VS Code se conecta directamente dentro del contenedor.

1. Abre **Visual Studio Code**.
2. Ve a `Archivo` -> `Abrir carpeta...` y selecciona la carpeta `docker-python-dev`.
3. VS Code detectará la configuración y mostrará una notificación en la esquina inferior derecha:
   > *"Folder contains a Dev Container configuration file. Reopen to develop in a container."*
   - Haz clic en **Reopen in Container** (Reabrir en contenedor).
   - *Alternativa manual:* Presiona `F1` (o `Ctrl+Shift+P` / `Cmd+Shift+P`), escribe **`Dev Containers: Reopen in Container`** y presiona Enter.
4. VS Code descargará la imagen, compilará el contenedor e iniciará el entorno. (La primera vez tomará 1 o 2 minutos).
5. ¡Listo! Abre el archivo `src/main.py` y ejecútalo con el botón de Play ▶️ o abriendo una terminal en VS Code (`Ctrl + ñ` o `Cmd + J`).
   - Verás que la terminal dice `vscode@...:/workspace$`. Estás programando dentro del contenedor.

---

## 💻 Modo 2: Uso Universal desde Terminal / Docker CLI

Si estás en otra máquina o no usas la extensión de VS Code, puedes levantarlo con Docker Compose clásico:

1. **Construir e iniciar el contenedor en segundo plano:**
   ```bash
   docker compose up -d
   ```
2. **Ejecutar el script de prueba:**
   ```bash
   docker compose exec python-dev python /workspace/main.py
   ```
3. **Abrir una terminal interactiva dentro del contenedor:**
   ```bash
   docker compose exec python-dev bash
   ```
4. **Detener el contenedor cuando termines:**
   ```bash
   docker compose down
   ```

---

## 📦 Cómo Seguir Instalando Librerías de Python

Tienes dos maneras según tu flujo de trabajo:

### A. Instalación rápida al instante (durante el desarrollo)
Abre la terminal dentro del contenedor (en VS Code o mediante `docker compose exec`) y ejecuta:
```bash
pip install matplotlib seaborn scikit-learn
```
Gracias a los permisos configurados, se instalará de inmediato y podrás importarla en tus scripts.

### B. Instalación permanente (para compartir el proyecto o moverlo a otra notebook)
Para asegurar que cualquiera que clone o use el proyecto tenga las mismas librerías:
1. Edita el archivo `requirements.txt` y añade el nombre de la librería:
   ```text
   numpy>=1.26.0
   pandas>=2.2.0
   ipykernel>=6.29.0
   scikit-learn
   matplotlib
   ```
2. En VS Code, presiona `F1` y selecciona: **`Dev Containers: Rebuild Container`**.
   *(O desde la terminal: `docker compose build && docker compose up -d`)*.

---

## ⚙️ Explicación de Recursos (RAM y Disco)

### 🧠 Memoria RAM (2 GB)
- Configurada en `docker-compose.yml` mediante:
  ```yaml
  mem_limit: 2g
  mem_reservation: 2g
  ```
- **Cómo funciona:** En Linux, macOS y Windows (WSL2), Docker utiliza los *cgroups* del kernel. Si los procesos de Python superan los 2 GB de memoria asignada, el sistema de cuotas actuará evitando que consuma más RAM del equipo host.
- Puedes verificarlo en tiempo real ejecutando:
  ```bash
  docker stats python-dev-container
  ```

### 💾 Espacio de Disco (2 GB)
- En Docker, el almacenamiento de los contenedores se maneja a través del controlador de almacenamiento (generalmente `overlay2`).
- El parámetro `storage_opt: size: '2G'` está incluido en `docker-compose.yml`. En servidores Linux con sistemas de archivos compatibles con cuotas por proyecto (`xfs` o `ext4` con `pquota`), Docker impone un límite estricto de 2 GB de escritura.
- **En Windows y macOS (Docker Desktop):** Docker Desktop corre dentro de una máquina virtual ligera (WSL2 en Windows o LinuxKit en Mac). La cuota de disco general la administra Docker Desktop en:
  *Docker Desktop -> Settings -> Resources -> Virtual disk limit*.
- **Persistencia inteligente:** Todo tu código y datasets se guardan en la carpeta local `./src`, montada como volumen (`/workspace`). Esto garantiza que:
  1. No pierdas tus archivos al apagar o recrear el contenedor.
  2. La imagen del contenedor se mantenga ultra liviana (~500 MB a 1 GB).

---

## 🐬 Base de Datos MySQL (Servicio Integrado)

El entorno incluye un contenedor oficial de **MySQL 8.0** configurado automáticamente en `docker-compose.yml`.

### Credenciales configuradas:
- **Host:** `db` (desde el código Python dentro del contenedor) o `localhost` (desde tu PC / DBeaver / Workbench)
- **Puerto:** `3306`
- **Usuario:** `taller`
- **Contraseña:** `prog`
- **Base de datos:** `taller_db`
- **Usuario root:** `root` (contraseña: `root_prog`)

### Librerías instaladas en `requirements.txt`:
- `pymysql`, `mysql-connector-python`, `sqlalchemy`, `cryptography`.

### Script de prueba de MySQL:
Ejecuta desde la terminal del contenedor:
```bash
python src/test_mysql.py
```
Este script se conecta a la base de datos, crea una tabla de ejemplo con Pandas (`df.to_sql`), inserta registros y los consulta (`pd.read_sql`).

