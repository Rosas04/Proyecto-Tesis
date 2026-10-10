# Usamos la imagen oficial de Playwright para Python
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRONTMIND_ENV=production \
    DOCS_ENABLED=false

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos primero el requirements.txt
COPY requirements.txt .

# Instalamos las dependencias de Python como root
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el backend (ver .dockerignore: sin venv, sesiones, capturas ni .env)
COPY . .

# Cambiamos los permisos de la carpeta al usuario pwuser (UID 1000) que usa Hugging Face
RUN chown -R pwuser:pwuser /app

# Cambiamos al usuario sin privilegios
USER pwuser

# Exponemos el puerto
EXPOSE 7860

HEALTHCHECK --interval=60s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:%s/' % os.environ.get('PORT','7860'),timeout=4)"

# Un solo worker: el rate limit y el semáforo de capturas viven en memoria del proceso
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
