# ==============================================================================
# Dockerfile para entorno de desarrollo Python portátil en VS Code
# Compatible con Windows, macOS (Intel y Apple Silicon) y Linux
# ==============================================================================

# Imagen oficial de Python ligera basada en Debian Bookworm
FROM python:3.11-slim

# Evitar prompts interactivos durante apt y configurar Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    SHELL=/bin/bash

# Instalar utilidades esenciales del sistema para compilación y desarrollo
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    procps \
    sudo \
    tree \
    nano \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario 'vscode' no-root (UID/GID 1000) con permisos sudo
# Esto evita problemas de permisos de archivos al compartir carpetas entre Windows/Mac/Linux
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Dar propiedad a vscode sobre /usr/local para que pueda ejecutar 'pip install'
# sin necesidad de usar sudo ni banderas especiales dentro de la terminal
RUN chown -R $USERNAME:$USER_GID /usr/local

# Crear y asignar el directorio de trabajo
WORKDIR /workspace
RUN chown -R $USERNAME:$USER_GID /workspace

# Copiar el archivo de requerimientos e instalar dependencias iniciales
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Cambiar al usuario no-root por defecto para una experiencia de desarrollo segura y estándar
USER $USERNAME

# Mantener el contenedor vivo indefinidamente para que VSCode y Docker Compose puedan conectarse
CMD ["sleep", "infinity"]
