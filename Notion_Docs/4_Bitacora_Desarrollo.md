# 📂 4. Bitácora de Desarrollo e Implementación

*(Copia y pega este contenido en la cuarta y última sub-página de tu Notion).*

---

La construcción de un framework agéntico capaz de realizar crawling dinámico y aplicar heurísticas de auditoría matemática ISO en entornos SPA (Single Page Applications) fue un reto tecnológico significativo. A continuación, documento los desafíos arquitectónicos más grandes que se superaron para dar vida a **FrontMind AI**.

## 🚧 Reto 1: Orquestación Asíncrona de Headless Browsers
**El Problema:** Renderizar el contenido de aplicaciones web modernas (construidas con React, Vue o Angular) no es posible mediante un simple request HTTP tradicional (como `requests` en Python), ya que el DOM requiere de un motor de JavaScript para pintarse (Client-Side Rendering).

**La Solución Implementada:** 
Integrar **Playwright** en el backend de FastAPI. Esto nos permitió levantar instancias invisibles del motor Chromium V8.
- *Desafío adicional:* Empaquetar Playwright dentro de un contenedor Docker en la nube (Render) requirió la inyección de múltiples dependencias del sistema operativo Linux (`libnss3`, `libasound2`) para que Chromium pudiera arrancar sin interfaz gráfica.

## 🚧 Reto 2: Evasión de Barreras y Crawling Seguro
**El Problema:** Acceder a las vistas internas (rutas protegidas) de plataformas de terceros sin que la sesión expire o el agente de clic por error en un botón destructivo (Ej: *"Borrar Cuenta"* o *"Cerrar Sesión"*).

**La Solución Implementada:** 
Se desarrolló un script dinámico que escanea el árbol DOM de la página interceptada. 
1. Se programó el agente para buscar el formulario de Login, rellenarlo y capturar el contexto del navegador (Cookies, SessionStorage, LocalStorage).
2. Con el `Storage State` en memoria, el agente comenzó a navegar recursivamente interceptando las etiquetas `<a>` y los botones.
3. Se añadió un diccionario de palabras excluidas (Blacklist) para que el agente ignorara botones peligrosos, manteniendo viva la sesión y el recorrido estable.

## 🚧 Reto 3: Motor ISO 25010 y Aislamiento CSSOM
**El Problema:** La norma ISO 25010 exige la medición de contraste visual y accesibilidad. Si enviamos las 6 páginas capturadas de una misma app al analizador de un solo golpe, los estilos globales de una podrían corromper la interfaz visual de la otra.

**La Solución Implementada:** 
Se programó un "Limpiador HTML". Tras capturar una ruta, Playwright extrae el DOM exacto, purga todos los `<script>` para evitar inyecciones XSS y ataques, e inyecta los archivos `.css` en línea (In-line). Este DOM purificado es enviado luego a **BeautifulSoup** en Python, donde una ecuación heurística analiza el contraste de colores, profundidad de nodos e imágenes rotas, sin que las interfaces se contaminen entre sí.

## 🏗️ Arquitectura de Software Final

Para asegurar la alta disponibilidad y un despliegue ágil, el ecosistema se ensambló usando:

- **Frontend (Cliente):** React.js empaquetado con Vite. Encargado de renderizar los gráficos vectoriales del Dashboard (Recharts).
- **Backend (API Core):** Python (FastAPI). Gestiona los hilos asíncronos de Playwright y el motor evaluador BeautifulSoup.
- **Base de Datos & Auth (BaaS):** Supabase (PostgreSQL). Gestiona los usuarios QA autenticados, y almacena el JSON final del reporte (Historial) mediante validación JWT.
- **Infraestructura Cloud:** Render. El backend se configuró mediante un `render.yaml` y un `Dockerfile` multietapa para soportar dependencias del navegador.

> *"FrontMind AI no es solo un auditor visual, es un orquestador de Inteligencia Artificial que abstrae por completo la dificultad técnica del aseguramiento de calidad frontend".*
