# Usamos la imagen oficial de Playwright para Python
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos primero el requirements.txt
COPY requirements.txt .

# Instalamos las dependencias de Python como root
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido del backend
COPY . .

# Cambiamos los permisos de la carpeta al usuario pwuser (UID 1000) que usa Hugging Face
RUN chown -R pwuser:pwuser /app

# Cambiamos al usuario sin privilegios
USER pwuser

# Exponemos el puerto
EXPOSE 7860

# Iniciamos el servidor leyendo el puerto de la variable de entorno $PORT (por defecto 7860)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]

