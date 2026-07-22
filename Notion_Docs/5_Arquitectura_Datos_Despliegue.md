# 📂 5. Arquitectura de Datos y Despliegue (DevOps)

*(Copia y pega este contenido en la quinta y última sub-página de tu Notion).*

---

Una solución de Inteligencia Artificial y Crawling no está completa si no posee una infraestructura sólida que garantice la persistencia de datos y un despliegue resiliente en la nube. En esta sección se detalla la columna vertebral (Backend/DevOps) que sostiene a **FrontMind AI**.

## 🗄️ Esquema Relacional de Base de Datos (Supabase)

El sistema utiliza **PostgreSQL** a través de Supabase, gestionando un modelo de datos optimizado para consultas rápidas de JSONs anidados, lo cual es vital para recuperar métricas ISO sin re-calcular algoritmos.

**Estructura Base (Simplified Entity-Relationship):**

1. **Tabla `users` (Gestión de Autenticación)**
   - Protegida por Row Level Security (RLS) y Tokens JWT.
   - Gestiona de forma segura el estado global del QA.

2. **Tabla `history_audits` (Historial de Ejecuciones)**
   - `id` (UUID) - Primary Key.
   - `user_id` (UUID) - Foreign Key -> `users.id`. Garantiza que un QA solo vea sus reportes.
   - `target_url` (String) - URL principal escaneada.
   - `timestamp` (DateTime) - Marca temporal para trazabilidad de calidad.
   - `iso_results` (JSONB) - Columna crítica de PostgreSQL que almacena de forma nativa los árboles JSON generados por el motor matemático, permitiendo búsquedas indexadas y recuperación asíncrona ultrarrápida para el Dashboard (Recharts).

---

## 🐳 Empaquetado y Dockerización

El mayor reto de infraestructura de FrontMind AI fue lograr que un motor de Navegador Web (Chromium V8 vía Playwright) pudiera ejecutarse sin fallos en un Servidor Linux sin Interfaz Gráfica (Headless). 

Para lograr el pase a Producción en la nube de **Render**, se utilizó un esquema de Dockerización Multietapa (`Multi-stage Build`).

**Snippet de Configuración (Dockerfile):**
```dockerfile
# Se utiliza una imagen oficial pesada que contiene las dependencias del OS para navegadores
FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy

WORKDIR /app

# Copia de requerimientos de IA, FastAPI y BeautifulSoup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalación explícita de binarios de Chromium 
RUN playwright install chromium
RUN playwright install-deps

COPY . .

# Exposición del puerto del Framework FastAPI
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
*Impacto:* Esta arquitectura garantiza que el entorno de desarrollo local sea **exactamente idéntico** al entorno de producción, erradicando el clásico problema de *"En mi máquina sí funciona"*.

---

## 🚀 Roadmap y Evolución del Proyecto

El desarrollo de FrontMind AI establece un nuevo paradigma en el Shift-Left Testing (Testing en fases tempranas). Las siguientes iteraciones a futuro de esta arquitectura incluyen:

1. **Notificaciones por WebSockets:** Implementar transmisión de datos en tiempo real (Socket.io/FastAPI WebSockets) para que la UI muestre los logs de Playwright en vivo sin necesidad de refrescar, mejorando la Heurística de Visibilidad del Sistema.
2. **Integración CI/CD (GitHub Actions):** Permitir que FrontMind AI funcione como un *Webhook*. Así, cada vez que un desarrollador hace `git push`, el servidor ejecuta la auditoría ISO 25010 automáticamente y bloquea el despliegue si el puntaje es menor a 80.
3. **Escalabilidad Horizontal (Workers Celery):** Desacoplar la orquestación del escaneo web de la API HTTP principal mediante Message Brokers (Redis) para poder soportar a 10,000 analistas QA simultáneos sin agotar la RAM.
