# FrontMind AI

**FrontMind AI** es un framework multiagente que audita la calidad de interfaces web frontend. Captura las pantallas de una aplicación (pública o privada) con Playwright, replica su HTML y las evalúa según la norma **ISO/IEC 25010** y las pautas de accesibilidad **WCAG**, para producir un diagnóstico por interfaz y un reporte consolidado de la aplicación.

Es el producto desarrollado en la tesis que acompaña a este repositorio.

## Cómo funciona

1. **Agente de captura**: navega la aplicación con Playwright, se autentica si hace falta (formulario o sesión guardada), descubre las rutas internas y toma capturas en escritorio, tablet y móvil.
2. **Agente de réplica HTML**: genera una réplica HTML independiente de cada interfaz capturada.
3. **Agente de evaluación ISO**: analiza el DOM de cada interfaz y calcula métricas de las características de calidad de ISO/IEC 25010 y de los criterios WCAG.
4. **Agente de reporte**: consolida los hallazgos y puntajes en un reporte de la aplicación.

El front (React) permite lanzar auditorías, revisar las interfaces capturadas, consultar el historial y descargar reportes. Los usuarios y el historial se guardan en Supabase.

## Estructura del repositorio

```
.
├── Front/                 Front-end en React + Vite (SPA)
├── frontmind-agents/      Back-end en Python / FastAPI con los agentes
│   ├── agents/            Agentes (captura, réplica HTML, evaluación ISO, reporte)
│   ├── services/          Lógica de negocio: capturas, autenticación, ISO 25010, historial
│   ├── core/              Seguridad (API key, token de Supabase) y rate limit
│   ├── tests/             Pruebas automatizadas (pytest)
│   ├── scripts/           Utilidades y scripts de experimentos de la tesis
│   ├── locustfile.py      Escenarios de pruebas de carga (Locust)
│   └── Dockerfile         Imagen para Hugging Face Spaces / Render
├── supabase/              Migraciones SQL (tablas, políticas RLS e índices)
├── docs/                  Documentación de la tesis
├── scripts/               Utilidades de documentación (Markdown a Word)
└── render.yaml            Despliegue en Render (backend Docker + front estático)
```

## Requisitos

- Python 3.11 o superior
- Node.js 20 o superior
- Un proyecto de Supabase con las migraciones de `supabase/migrations/` aplicadas

## Ejecutar el backend

```bash
cd frontmind-agents
python -m venv venv
venv\Scripts\activate          # En Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
copy .env.example .env         # En Linux/macOS: cp .env.example .env
```

Completa `.env` con tus valores y levanta la API:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

En Windows también puedes usar `iniciar-backend.bat`, que activa el entorno virtual y arranca la API en modo desarrollo en el puerto 8001.

Pruebas automatizadas:

```bash
python -m pytest tests -q
```

## Ejecutar el front

```bash
cd Front
npm install
copy .env.example .env         # En Linux/macOS: cp .env.example .env
npm run dev
```

`VITE_API_URL` debe apuntar al backend (por defecto `http://127.0.0.1:8001`) y `VITE_BACKEND_API_KEY` debe coincidir con `BACKEND_API_KEY` del backend. Para generar la versión de producción: `npm run build`.

## Despliegue

- **Backend**: imagen Docker definida en `frontmind-agents/Dockerfile`, publicada en un Space de Hugging Face y en Render.
- **Front**: sitio estático en Render (ver `render.yaml`).
- **Base de datos**: Supabase. Los secretos (`BACKEND_API_KEY`, `ABSTRACT_API_KEY`, etc.) se configuran en el panel de cada servicio, nunca en el código.

## Documentación de la tesis

Toda la documentación está en [`docs/`](docs/README.md):

- [`docs/resultados/`](docs/resultados): capítulo 6 y resultados de los objetivos específicos.
- [`docs/datos/`](docs/datos): datos recolectados en los experimentos (OE1, OE2, OE3).
- [`docs/pruebas/`](docs/pruebas): pruebas funcionales, unitarias, de caja blanca y negra, de carga, de humo y de usabilidad, y el protocolo de validación con F1-score.
- [`docs/metodologia/`](docs/metodologia): operacionalización de ISO/IEC 25010 en FrontMind AI.
