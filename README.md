# FrontMind AI

Framework agéntico para la **auditoría de calidad de aplicaciones frontend** según la norma
**ISO/IEC 25010**. A partir de una URL (pública o con inicio de sesión) o de un proyecto en ZIP,
el sistema descubre las interfaces de la aplicación, las captura en varias resoluciones, genera
una réplica HTML independiente de cada una, las evalúa y produce un reporte consolidado.

## Contenido

| Qué | Dónde |
|---|---|
| Backend (API y agentes) | [frontmind-agents/](frontmind-agents/README.md) |
| Frontend (React) | [Front/](Front/README.md) |
| Esquema de base de datos | [supabase/](supabase/) |
| Modelo de evaluación ISO/IEC 25010 (métricas, umbrales y alcance) | [docs/Operacionalizacion_ISO25010.md](docs/Operacionalizacion_ISO25010.md) |

---

## Flujo del sistema

```text
URL (pública o privada) / ZIP
  → Autenticación (si la aplicación lo requiere)
  → Descubrimiento de rutas internas
  → Captura de cada interfaz (escritorio, tablet, móvil)
  → Réplica HTML individual
  → Evaluación ISO/IEC 25010 por interfaz
  → Reporte consolidado (PDF) e historial
```

## Arquitectura

```text
┌──────────────────────┐   HTTPS + X-API-Key   ┌──────────────────────────────┐
│  Front/ (React+Vite) │ ────────────────────▶ │ frontmind-agents/ (FastAPI)  │
│  Sitio estático      │   Bearer de Supabase  │ Agentes + Playwright (Docker)│
└──────────┬───────────┘                       └──────────────┬───────────────┘
           │ Auth + historial                                  │ Verifica el token
           ▼                                                   ▼
                     ┌───────────────────────────────┐
                     │ Supabase (PostgreSQL + Auth)  │
                     │ Tablas con Row Level Security │
                     └───────────────────────────────┘
```

**Agentes del backend** (`frontmind-agents/agents/`):

| Agente | Responsabilidad |
|---|---|
| `CaptureAgent` | Inicia sesión, descubre rutas y captura cada interfaz con Playwright. |
| `HtmlReplicationAgent` | Genera una réplica HTML aislada por interfaz. |
| `ISOEvaluationAgent` | Calcula las métricas ISO/IEC 25010 y los hallazgos. |
| `ReportAgent` | Consolida los resultados en el reporte final. |

## Estructura del repositorio

```text
.
├── Front/                 Frontend React + Vite (ver Front/README.md)
├── frontmind-agents/      Backend FastAPI + agentes + pruebas (ver frontmind-agents/README.md)
├── supabase/              Migraciones SQL (tablas, RLS e índices)
├── docs/                  Modelo de evaluación ISO/IEC 25010 implementado
└── render.yaml            Despliegue en Render (backend Docker + frontend estático)
```

## Ejecución local

Requisitos: Python 3.11, Node.js 20+ y un proyecto de Supabase.

**Backend** (puerto 8001):

```bash
cd frontmind-agents
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
copy .env.example .env           # Linux/macOS: cp .env.example .env  — y completar valores
python -m uvicorn main:app --reload --port 8001
```

**Frontend** (puerto 5173):

```bash
cd Front
npm install
copy .env.example .env           # Linux/macOS: cp .env.example .env
npm run dev
```

**Base de datos:** ejecutar en orden los archivos de `supabase/migrations/` en el SQL Editor de
Supabase (o `supabase db push`). `supabase/setup_completo.sql` contiene el esquema base en un solo archivo.

## Pruebas automatizadas

```bash
cd frontmind-agents
pytest
```

## Despliegue

- **Backend:** imagen Docker (`frontmind-agents/Dockerfile`) publicada en Hugging Face Spaces o Render.
- **Frontend:** sitio estático en Render (`render.yaml`).
- Los secretos se configuran en el panel de cada servicio; nunca se suben al repositorio
  (ver los archivos `.env.example`).
