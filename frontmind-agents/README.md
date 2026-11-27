---
title: ProyectoTesisBack
emoji: 🏆
colorFrom: yellow
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

<!-- El bloque anterior es la configuración del Space de Hugging Face: no eliminarlo. -->

# FrontMind AI — Backend

API en **FastAPI** que orquesta los agentes de auditoría. Usa **Playwright** (Chromium) para
navegar, autenticarse y capturar interfaces. Se despliega como contenedor Docker.

## Ejecutar en local

```bash
python -m venv venv
venv\Scripts\activate             # Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
cp .env.example .env              # completar valores (ver comentarios del archivo)
python -m uvicorn main:app --reload --port 8001
```

En Windows también puede usarse `iniciar-backend.bat`.

## Estructura

```text
frontmind-agents/
├── main.py              API: endpoints, validación de entradas y límites
├── agents/              Agentes del flujo de auditoría
│   ├── capture_agent.py           Login, descubrimiento de rutas y capturas
│   ├── html_replication_agent.py  Réplica HTML aislada por interfaz
│   ├── iso_evaluation_agent.py    Evaluación ISO/IEC 25010
│   ├── report_agent.py            Reporte consolidado
│   ├── orchestrator.py            (Experimental, LLM; no se usa en producción)
│   └── tools/                     Herramientas de apoyo de los agentes
├── services/            Lógica reutilizable
│   ├── iso_framework.py           Definición de métricas y umbrales ISO (fuente única)
│   ├── iso_service.py             Cálculo de puntajes y hallazgos
│   ├── auth_service.py            Inicio de sesión en aplicaciones privadas
│   ├── route_discovery_service.py Descubrimiento de rutas internas
│   ├── screenshot_*.py            Capturas en escritorio, tablet y móvil (proceso aislado)
│   ├── spa_helpers.py             Esperas para aplicaciones SPA
│   ├── zip_service.py             Extracción segura de proyectos ZIP
│   ├── history_service.py         Historial de análisis
│   ├── progress_service.py        Progreso de cada captura
│   └── llm_service.py             (Opcional, requiere requirements-agents.txt)
├── core/                Seguridad (API key, token de Supabase) y rate limiting
├── scripts/             Utilidades: verificación de archivos de despliegue y sesión manual
└── tests/               Pruebas automatizadas con pytest (agents/, services/)
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Estado del servicio |
| POST | `/capture/url` | Captura una aplicación desde su URL (con o sin credenciales) |
| GET | `/capture/progress` | Progreso de una captura en curso |
| POST | `/upload/zip` | Analiza un proyecto subido en ZIP |
| POST | `/replicate/html` | Réplica HTML de una interfaz |
| POST | `/replicate/content` | Réplica a partir de contenido HTML |
| POST | `/evaluate/iso` | Evaluación ISO/IEC 25010 |
| POST | `/report/generate` | Reporte consolidado |
| GET | `/history` | Historial del usuario autenticado |
| POST | `/auth/verify-email` | Verificación de correo en el registro |

Todos los endpoints (salvo `/`) exigen el header `X-API-Key`; los que manejan datos del usuario
exigen además su token de Supabase (`Authorization: Bearer ...`).

## Pruebas

```bash
pytest                                   # suite unitaria
pytest --cov=agents --cov=services       # con cobertura
```

## Dependencias

| Archivo | Uso |
|---|---|
| `requirements.txt` | Producción (versiones fijadas) |
| `requirements-dev.txt` | Desarrollo y pruebas |
| `requirements-agents.txt` | Opcional: orquestador LLM experimental |
