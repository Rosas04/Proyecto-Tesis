# Usamos la imagen oficial de Playwright para Python que ya viene con todos los navegadores y dependencias instaladas
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos primero el requirements.txt para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido del backend
COPY . .

# Exponemos el puerto en el que corre FastAPI por defecto
EXPOSE 8000

# Iniciamos el servidor con Uvicorn escuchando en todas las interfaces de red (0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
