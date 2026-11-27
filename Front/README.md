# FrontMind AI — Frontend

Aplicación de página única (SPA) en **React 19 + Vite**. Autenticación e historial con
**Supabase**; el análisis se delega al backend (`../frontmind-agents`).

## Ejecutar

```bash
npm install
cp .env.example .env   # completar las variables
npm run dev            # http://localhost:5173
npm run build          # genera dist/
npm run lint
```

| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL del backend (local: `http://127.0.0.1:8001`) |
| `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` | Proyecto de Supabase (clave pública) |
| `VITE_BACKEND_API_KEY` | Debe coincidir con `BACKEND_API_KEY` del backend |

## Estructura de `src/`

```text
src/
├── main.jsx, App.jsx    Punto de entrada y rutas
├── pages/               Una vista por paso del flujo
├── components/          Componentes reutilizables (layout, sidebar, reporte)
├── context/             Estado global: sesión (AuthContext) y análisis en curso (AnalysisContext)
├── services/            Acceso a datos: api.js (backend), historyService.js y storageService.js (Supabase)
├── routes/              ProtectedRoute (exige sesión iniciada)
├── lib/                 Cliente de Supabase
├── utils/               Funciones puras (nivel de calidad, etiquetas, throttling de login)
└── styles/              Estilos globales
```

## Rutas

| Ruta | Vista | Paso del flujo |
|---|---|---|
| `/login`, `/register`, `/forgot-password`, `/reset-password` | Autenticación | — |
| `/` | Home | Resumen y últimos análisis |
| `/input` | Input | 1. URL, credenciales o ZIP |
| `/capture` | Capture | 2. Interfaces capturadas |
| `/html` | HtmlReplica | 3. Réplica HTML |
| `/evaluation` | Evaluation | 4. Evaluación ISO/IEC 25010 |
| `/report` | Report | 5. Reporte consolidado (PDF) |
| `/history` | History | Análisis anteriores |
