import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Content-Security-Policy sólo para el build de producción (en desarrollo
// rompería el HMR de Vite). Las réplicas HTML se muestran en un iframe srcdoc
// que hereda esta política: por eso se permiten estilos, fuentes e imágenes
// https externos, pero nunca scripts de terceros.
const CSP = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self' 'unsafe-inline' https:",
  "img-src 'self' data: blob: https: http://localhost:* http://127.0.0.1:*",
  "font-src 'self' data: https:",
  "connect-src 'self' https: wss: http://localhost:* http://127.0.0.1:*",
  "frame-src 'self' blob: data:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join('; ')

function cspPlugin() {
  return {
    name: 'frontmind-csp',
    apply: 'build',
    transformIndexHtml(html) {
      return html.replace(
        '<meta charset="UTF-8" />',
        `<meta charset="UTF-8" />\n    <meta http-equiv="Content-Security-Policy" content="${CSP}" />\n    <meta name="referrer" content="strict-origin-when-cross-origin" />`
      )
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), cspPlugin()],
  build: {
    sourcemap: false,
    rolldownOptions: {
      output: {
        // Separa librerías pesadas en chunks cacheables por el navegador
        advancedChunks: {
          groups: [
            { name: 'react-vendor', test: /node_modules[\\/](react|react-dom|react-router|react-router-dom|scheduler)[\\/]/ },
            { name: 'supabase', test: /node_modules[\\/]@supabase[\\/]/ },
            { name: 'pdf', test: /node_modules[\\/](jspdf|jspdf-autotable|html2canvas|canvg|dompurify|fflate)[\\/]/ },
            { name: 'charts', test: /node_modules[\\/](recharts|d3-[^\\/]+|victory-vendor)[\\/]/ },
          ],
        },
      },
    },
  },
})
