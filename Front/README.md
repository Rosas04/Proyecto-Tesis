# FrontMind AI: front-end

Aplicación de página única en React + Vite. Permite registrarse e iniciar sesión (Supabase), lanzar auditorías contra el backend, revisar las interfaces capturadas, consultar el historial y descargar reportes.

```bash
npm install
cp .env.example .env   # completa las variables
npm run dev            # servidor de desarrollo
npm run build          # build de producción en dist/
npm run lint
```

Variables de entorno (ver `.env.example`): `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL` y `VITE_BACKEND_API_KEY`.

Estructura de `src/`: `pages/` (pantallas), `components/` (componentes reutilizables), `services/` y `lib/` (clientes del backend y de Supabase), `context/`, `routes/`, `constants/`, `utils/` y `styles/`.

Más información en el [README del repositorio](../README.md).
