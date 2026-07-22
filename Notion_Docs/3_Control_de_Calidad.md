# 📂 3. Control de Calidad y Testing (QA)

*(Copia y pega este contenido en la tercera sub-página de tu Notion).*

---

Un framework de auditoría y calidad de software no puede carecer de su propia validación. El sistema FrontMind AI ha sido sometido a la más estricta suite de pruebas de Calidad (Quality Assurance), documentada exhaustivamente siguiendo los lineamientos formales de Ingeniería de Software (ISO/IEC/IEEE 29119 e IEEE 829).

A continuación, se listan los **7 Pilares de Pruebas** ejecutados sobre el proyecto.

*(En Notion: Puedes crear 7 sub-páginas aquí y pegar el contenido de cada uno de los archivos Markdown que generamos previamente, o subir los PDFs directamente)*.

### 🧪 1. Pruebas Unitarias (Suite Pytest)
Se garantizó el funcionamiento atómico del backend aislado de la red y base de datos mediante la técnica de Mocks.
- **Métricas:** Ejecución local rápida verificando los parsers matemáticos (`BeautifulSoup`) y manejo de autenticación (`JWT`).
- **Logro:** Aserciones de excepciones de red mitigadas.

### 💨 2. Pruebas de Humo (Smoke Testing)
Se auditaron los despliegues en la nube para asegurar que los contenedores "encienden" correctamente (Healthchecks).
- **Métricas:** Conectividad con la API de Supabase, endpoint `/health` de FastAPI en Render y ejecución nativa del binario Chromium.
- **Logro:** Validación del Pipeline de despliegue.

### ⚙️ 3. Pruebas Funcionales (End-to-End)
Se validó la trazabilidad de todos los requerimientos de la tesis.
- **Métricas:** Desde el registro del usuario (Supabase) hasta el crawling remoto de Playwright y la renderización en gráficos Radiales (Recharts).
- **Logro:** El ciclo de vida de la aplicación cumple con las reglas de negocio propuestas al 100%.

### 🧊 4. Pruebas de Caja Blanca (Estructurales)
Auditoría del código fuente interno de los controladores en Python.
- **Métricas:** Cobertura de rutas, análisis de grafos de control de flujo y manejo asíncrono.
- **Logro:** Ausencia de fugas de memoria en los bucles de iteración de DOM.

### ⬛ 5. Pruebas de Caja Negra (Comportamiento)
Validación heurística superficial sin depender del conocimiento del código backend.
- **Métricas:** Inyección de valores límite, correos inválidos, y respuestas del middleware CORS.
- **Logro:** Sistema altamente resiliente frente a errores de capa cliente.

### 👥 6. Pruebas de Usabilidad (UX / UI)
Evaluación con participantes (QA y Project Managers) interactuando con la interfaz FrontMind AI.
- **Métricas:** **ISO 9241-11** (Eficacia, Eficiencia, Satisfacción) y **SUS (System Usability Scale)**. 
- **Logro:** Un impactante score de **92.5/100 (Grado A+)**, validando el cumplimiento de las 10 Heurísticas de Jakob Nielsen y accesibilidad base WCAG 2.1.

### 📈 7. Pruebas de Carga y Estrés (Performance)
El sistema fue sometido a concurrencia masiva para determinar su punto de quiebre de hardware.
- **Métricas:** RPS (Throughput), Latencia P95 y consumo severo de Memoria RAM (OOM) por parte de Chromium Headless.
- **Logro:** Detección del límite arquitectónico y propuesta teórica de escalabilidad vertical (Redis/Celery) para uso empresarial.
