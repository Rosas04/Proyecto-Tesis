# Auditoría integral de FrontMind AI — 17/11/2026

**Alcance:** backend (FastAPI + Playwright), frontend (React), Supabase, despliegues (Render y Hugging Face),
evaluador ISO/IEC 25010 y motor de web scraping.
**Método:** revisión del código completo (~14 500 líneas), suite de pruebas (79/79 OK), pruebas dinámicas
del evaluador con HTML controlado, pruebas de SSRF contra un servidor local, scraping real de 12 sitios
(públicos, SPA, gubernamental, universitario, comercio electrónico y 2 sitios de práctica con login),
inspección de cabeceras/CORS de los servicios desplegados y `npm audit`.

Severidad: 🔴 Crítica · 🟠 Alta · 🟡 Media · 🔵 Baja

---

## 1. Resumen ejecutivo

| Área | Estado | Hallazgo principal |
|---|---|---|
| **Evaluador ISO/IEC 25010** | 🔴 | Se evalúa la **réplica** HTML, no la página original: oculta problemas reales (seguridad, viewport, idioma) e introduce falsos positivos. El puntaje global no se deriva de las métricas X = A/B. |
| Seguridad | 🟠 | SSRF por redirección en la descarga de CSS (demostrado). El descubrimiento con clics puede ejecutar acciones reales en sistemas autenticados. |
| Conectividad | 🟠 | La captura es una petición síncrona de 20–85 s por 4 páginas; con 10 páginas puede superar el límite de 100 s del proxy de Render/Cloudflare. |
| Web scraping | 🟡 | Capturó los 10 sitios públicos (incluido Amazon), pero el login automático falló en 1 de 2 sitios de prueba; el descubrimiento de rutas no es reproducible y puede salir del sitio (subdominios). |
| Privacidad | 🟡 | Correo enviado a un tercero (Abstract API) sin mención expresa; HTML capturado persiste en `localStorage`; se aceptan cookies en nombre del usuario. |
| Usabilidad / compatibilidad del propio sistema | 🔵 | Formularios accesibles y responsive; faltan atributos `autocomplete` y hay dos escalas de calidad distintas en la UI. |

**Lo que está bien hecho** (conviene destacarlo en la tesis): API key + verificación del token de Supabase en
cada petición (sin IDOR), RLS forzado en todas las tablas, rate limiting con bloqueo progresivo, semáforo de
capturas, extracción segura de ZIP (Zip Slip / Zip Bomb), guarda SSRF dentro de Chromium para cada petición
(probada con `2130706433`, `0x7f000001` y `127.1`: todas bloqueadas), credenciales del sitio auditado que
viajan por stdin y nunca se persisten, `storage_state` borrado en `finally`, contenedor sin root,
`/docs` desactivado en producción, HSTS y `nosniff`, y una documentación honesta de lo que no es automatizable.

---

## 2. Evaluador ISO/IEC 25010 (lo más importante para la tesis)

> **Actualización (17/11/2026):** los hallazgos E-1 a E-6 y E-9 están corregidos. El evaluador analiza ahora el
> DOM original y puntúa seis características de ISO/IEC 25010:2023: Adecuación funcional, Capacidad de
> interacción, Compatibilidad, Flexibilidad, Seguridad y Fiabilidad. Eficiencia de desempeño es opcional y
> Mantenibilidad queda excluida. Cada puntaje se deriva de 50 métricas trazables, medidas en ejecución con
> Chromium, Firefox y WebKit. El detalle está en
> [Operacionalizacion_ISO25010.md](Operacionalizacion_ISO25010.md). La tabla siguiente describe el estado
> **anterior** a la corrección.

### 2.1 Veredicto por característica

| Característica (ISO/IEC 25010:2023) | ¿Lo mide bien hoy? | Problema | Cómo medirlo de verdad (Playwright ya lo permite) |
|---|---|---|---|
| **Adecuación funcional** | ❌ No | Se mide con `<main>`, `<nav>`, `<h1>` y palabras como "error" en el HTML. Eso es semántica/accesibilidad, no funcionalidad. `example.com` (100 % funcional) obtiene 65. | Enlaces rotos (status HTTP de las rutas descubiertas), errores JS (`page.on("pageerror")`), peticiones fallidas 4xx/5xx, formularios con `action` válido, páginas que cargan con 200. |
| **Flexibilidad** (antes Portabilidad) · Adaptabilidad | ⚠️ Parcial | Sólo comprueba `meta viewport` y una regex de `width:Npx` que además cuenta `max-width:1200px` (el patrón responsive *correcto*) como fallo. Las capturas en 3 resoluciones existen pero no se miden. | En 390 px: desbordamiento horizontal (`scrollWidth > innerWidth`), objetivos táctiles < 24 px (WCAG 2.5.8), reflow a 320 px (WCAG 1.4.10), texto < 12 px. |
| **Compatibilidad** | ⚠️ Débil | Sólo Chromium. Marca como "Alta" cualquier `body{}` o `h1{}` en `<style>` (CSS normal) y cualquier `window.x =` (p. ej. `dataLayer` de Analytics). | Capturar también con Firefox y WebKit (Playwright los trae) y comparar errores de consola/diseño; interoperabilidad = peticiones API fallidas o CORS bloqueados. |
| **Seguridad** | ❌ No | Sólo 2 reglas de texto sobre los scripts. Una página con login que envía la contraseña por **HTTP con GET**, `target="_blank"` sin `rel`, scripts de terceros sin SRI e iframe HTTP obtuvo **seguridad = 100**. Además, como se evalúa la réplica (sin scripts), estas 2 reglas casi nunca se disparan: seguridad = 100 en 10 de 11 sitios. | HTTPS y certificado válido, contenido mixto, formularios con contraseña sobre HTTP o GET, cabeceras (CSP, HSTS, X-Frame-Options, Referrer-Policy) leídas de la respuesta de Playwright, cookies sin `Secure/HttpOnly/SameSite`, SRI en scripts de CDN, `rel="noopener"`. |
| **Capacidad de interacción** (antes Usabilidad) + Inclusividad/Accesibilidad | ⚠️ Aceptable con errores | Las reglas WCAG (alt, labels, nombres accesibles, contraste con estilos computados, `lang`) son razonables. Pero: `required` no se detecta (falso positivo en todos los formularios), el idioma siempre "pasa" porque la réplica fuerza `lang="es"`. | Corregir los bugs de la sección 2.3; opcionalmente integrar axe-core en Playwright para ampliar cobertura WCAG. |
| Eficiencia de desempeño | ✅ Bien (en ejecución) | TTFB, LCP, CLS, bytes y peticiones se miden de verdad. Hay doble penalización con las heurísticas estáticas (LCP y CLS se penalizan dos veces). | Usar sólo la medición real cuando exista. |
| Mantenibilidad | ⚠️ Parcial (bien declarado) | Sobre la réplica, el CSS de todo el sitio se concatena y dispara "HTML > 80 KB" y paletas de 194–319 colores. | Evaluar el original; contar colores sólo en estilos del documento, no de bibliotecas. |
| Fiabilidad | ❓ Incoherente | Se reportan hallazgos de "Fiabilidad" pero no afectan ningún puntaje (la clave no existe) y la documentación la declara fuera de alcance. | Quitar esos hallazgos o incorporarla de forma explícita. |

### 2.2 Hallazgos del evaluador

**🔴 E-1. Se evalúa la réplica y no la interfaz original.**
`Front/src/pages/HtmlReplica.jsx:219` guarda `htmlPreview` (la réplica) como HTML a evaluar. La réplica
(`agents/html_replication_agent.py:96-127`) fuerza `lang="es"` y `meta viewport`, elimina todos los `<script>`,
agrega `body{}` global y Tailwind CDN, y concatena todo el CSS del sitio.
Evidencia (mismo HTML, original vs. réplica):

| Sitio | Original | Réplica | Qué cambió |
|---|---|---|---|
| quotes.toscrape.com | 89 | 87 | La falta de `meta viewport` del original **desaparece**; aparecen "234 anchos rígidos" y "194 colores" que no son del sitio. |
| react.dev | 78 | 81 | El hallazgo de seguridad (token en `localStorage`) **desaparece**: seguridad 85 → 100. |
| books.toscrape.com | 90 | 84 | +4 hallazgos artificiales (HTML > 80 KB, 160 anchos rígidos, estilos globales, 238 colores). |
| news.ycombinator.com | 81 | 77 | +4 hallazgos artificiales. |

*Mejora:* evaluar siempre `iface.html_content` (DOM capturado) junto con `performance_metrics` de esa interfaz;
la réplica sólo para visualizar. Además el usuario puede editar la réplica en el textarea antes de evaluar
(`HtmlReplica.jsx:428`), lo que permite alterar el resultado de una auditoría.

**🟠 E-2. El puntaje no se deriva de las métricas X = A/B.** `compute_metrics()` calcula ACC-01…EFI-06 con meta
y grado 0–4, pero el puntaje sale de `100 − penalizaciones` fijas e independientes (`iso_service.py:137-920`).
Para la tesis se rompe la trazabilidad norma → subcaracterística → métrica → puntaje.
*Mejora:* puntaje de cada característica = promedio ponderado de `min(1, X/meta)` de sus métricas; los hallazgos
sirven de explicación, no de fuente del número.

**🟠 E-3. "Sin evidencia" = 100 puntos.** Toda característica parte en 100; si no tiene reglas que se disparen, queda
perfecta y sube el promedio global (seguridad, compatibilidad, portabilidad). *Mejora:* marcar "no evaluado" y
excluirla del promedio, o exigir cobertura mínima de métricas.

**🟠 E-4. Falsos positivos confirmados con HTML controlado** (una página correcta obtuvo 3 hallazgos falsos):
- `<input required>` no cuenta como validado: BeautifulSoup devuelve `""` y `any(input_tag.get(...))` es falso
  (`iso_service.py:381-383`). Tampoco cuenta `type="email"`, aunque la métrica USA-01 sí lo cuenta.
- La regex `width\s*:\s*(\d+)px` (`iso_service.py:899`) captura `max-width: 1200px`.
- `body{margin:0}` en `<style>` se reporta como problema de compatibilidad de severidad Alta (`iso_service.py:665-682`).
- Estados de carga/error: basta que la palabra "error" o "status" aparezca en cualquier parte del HTML (incluido
  JS) para darlo por cumplido (`iso_service.py:255-265`) → falso negativo casi universal.
- "Datos sensibles en storage": basta que aparezcan las palabras `localStorage` y `token`/`session` en cualquier script.

**🟡 E-5. Inconsistencias internas del reporte.** El hallazgo de botones no considera `aria-labelledby` ni `<img alt>`
y la métrica ACC-03 sí; el de enlaces cuenta `<a>` sin `href`, la métrica ACC-04 no. Resultado: la métrica dice
"cumple" y el hallazgo dice lo contrario. Además conviven dos escalas: *Excelente/Alto/Medio/Bajo/Crítico*
y *Alta/Buena/Regular/Mala* (`decision_criterion`).

**🟡 E-6. Doble penalización.** LCP (heurística de scripts + medición real) y CLS (imágenes sin dimensiones +
medición real) penalizan dos veces la misma causa.

**🟡 E-7. Resultados no reproducibles.** El descubrimiento ordena los enlaces con `list(set(...))`
(`route_discovery_service.py:278, 329, 407`); el orden de un `set` varía entre ejecuciones, así que dos auditorías
del mismo sitio pueden capturar interfaces distintas. Para una tesis esto afecta la validez del experimento.
*Mejora:* ordenar (enlaces de `<nav>` primero, luego por profundidad y alfabético).

**🔵 E-8. El reporte confía en el cliente.** `/report/generate` recibe los puntajes desde el navegador y no los
recalcula; lo mismo ocurre al guardar en Supabase. *Mejora:* que el backend recalcule o firme (HMAC) la evaluación.

**🔵 E-9. Nomenclatura de la versión 2023.** El sistema mezcla 25010:2011 y 2023. En 2023: Usabilidad →
*Capacidad de interacción* (incluye *Inclusividad*, *Autodescriptividad*, *Asistencia al usuario*),
Portabilidad → *Flexibilidad* (Adaptabilidad, **Escalabilidad**, Instalabilidad, Reemplazabilidad),
Seguridad añade *Resistencia*, y aparece *Seguridad física (Safety)*. Conviene elegir una versión y usarla en todo
el reporte y la tesis.

---

## 3. Seguridad del sistema

**🟠 S-1. SSRF por redirección en la descarga de CSS — demostrado.** `fetch_css` valida sólo la primera URL y luego
`requests.get` sigue redirecciones (`html_replication_agent.py:131-152`). Prueba: un servidor que responde
`302 → http://127.0.0.1:8765/` devolvió el contenido interno (`SECRETO_INTERNO`) dentro de la réplica. Explotable
desde `/replicate/content`, donde el usuario envía el HTML. Tampoco hay límite de tamaño de la respuesta.
*Mejora:* `allow_redirects=False` validando cada salto, `stream=True` con tope (2 MB), o descargar CSS sólo
desde Playwright, que ya tiene la guarda SSRF.

**🟠 S-2. Clics automáticos en sesión autenticada.** `extract_routes_via_clicks` dice "NO usar en flujo autenticado"
pero `discover_routes_authenticated` lo llama (`route_discovery_service.py:277, 328`). Hace clic con `force=True`
en hasta 8 botones por página; la lista negra no cubre "Aprobar", "Publicar", "Enviar solicitud", "Añadir al
carrito", "Archivar", "Suscribirse"… Puede modificar datos reales del sistema auditado.
*Mejora:* sin clics en modo autenticado, y una red de seguridad: tras el login, abortar con `route` toda petición
`POST/PUT/PATCH/DELETE`.

**🟡 S-3. Réplica sin sanitizar.** El `<title>` y los atributos de `<body>` se insertan sin escapar (inyección
de marcado demostrada) y se conservan `onerror=`, `onclick=` y `href="javascript:"`. Hoy lo mitiga el
`iframe sandbox=""` y la CSP; si la réplica se descarga o abre aparte, es XSS. *Mejora:* `html.escape`, eliminar
atributos `on*` y URLs `javascript:`, quitar el `<script>` de Tailwind CDN.

**🟡 S-4. CORS abierto en Hugging Face.** El proxy de HF responde `Access-Control-Allow-Origin` con cualquier origen
(probado con `https://evil.example`); la restricción de `ALLOWED_ORIGINS` no aplica allí. Render sí lo rechaza.
El impacto es bajo porque la sesión viaja como Bearer (no cookie), pero la tesis no debería afirmar que CORS
protege la API en HF.

**🟡 S-5. Rate limit evadible.** Con `TRUST_PROXY_HEADERS=true` se usa el **primer** valor de `X-Forwarded-For`,
que lo controla el cliente (`core/rate_limit.py:40-43`), y uvicorn corre con `--forwarded-allow-ips='*'`.
Permite agotar la cuota de Abstract API vía `/auth/verify-email`. *Mejora:* usar el último salto añadido por el
proxy de confianza.

**🟡 S-6. `validate_url` falla abierta.** Si el DNS no resuelve, permite la URL; no bloquea `100.64.0.0/10`; acepta
`http://2130706433` o `http://127.1`. La guarda de Chromium los bloquea (probado), pero `requests` no tiene esa
segunda barrera. *Mejora:* exigir `ip.is_global` y fallar cerrado.

**🟡 S-7. `history.json` sin límites.** `/report/generate` no limita el tamaño de `evaluation`, reescribe el archivo
completo en cada llamada y sin bloqueo (corrupción con peticiones concurrentes); crece sin retención.

**🔵 S-8.** Mensajes internos de Playwright (`str(exc)`) devueltos al cliente. **🔵 S-9.** `ignore_https_errors=True`
oculta certificados inválidos (debería reportarse como hallazgo de seguridad del sitio auditado). **🔵 S-10.**
Código muerto `agents/orchestrator.py` y `agents/tools/*` (LangChain/OpenAI) sin guarda SSRF, con la contraseña en el
prompt del LLM; se copia en la imagen Docker. Eliminar. **🔵 S-11.** `npm audit`: 9 vulnerabilidades (1 crítica en
`dompurify` vía `jspdf`, 5 altas: `vite`, `zod`, `picomatch`…); `npm audit fix` las resuelve. `pip-audit` está en
`requirements-dev.txt` pero no instalado en el venv. **🔵 S-12.** La CSP del frontend va en `<meta>` (no admite
`frame-ancestors`) y permite `localhost` en producción; añadir cabeceras en `render.yaml`.

---

## 4. Conectividad y disponibilidad

**🟠 C-1. Captura síncrona larga.** Tiempos medidos localmente con 4 páginas: 19 s (example.com) a 85 s (react.dev).
Con el valor por defecto de 10 páginas es fácil superar los ~100 s de Cloudflare delante de Render → error 524
aunque el backend termine. El worker admite 30 min y el `fetch` del frontend no tiene timeout.
*Mejora:* trabajo asíncrono: `POST /capture/url` devuelve `job_id`; el resultado se consulta con
`GET /capture/result/{job_id}` (el polling de progreso ya existe).

**🟡 C-2. Arranque en frío.** Render (plan free) tardó 36 s en la primera respuesta; HF no respondió en 40 s al
primer intento. Mostrar un estado "despertando servidor" y precalentar con `checkBackendHealth` al iniciar sesión.

**🟡 C-3. Dos backends con configuración distinta** (HF y Render, CORS diferente). Elegir uno como oficial.

**✅** Supabase responde en < 1 s; el frontend en Render sirve HSTS con preload; `/docs` devuelve 404 en producción.

---

## 5. Web scraping: pruebas con sitios reales

Límite: 4 interfaces por sitio, 3 resoluciones cada una (escritorio, tablet, móvil).

| Sitio | Tipo | Tiempo | Interfaces | Resultado |
|---|---|---|---|---|
| example.com | Estático mínimo | 19 s | 1/1 | ✅ |
| quotes.toscrape.com | Multipágina | 45 s | 4/4 | ✅ |
| books.toscrape.com | Catálogo | 43 s | 4/4 | ✅ |
| react.dev | SPA (Next.js) | 85 s | 4/4 | ✅ pero eligió un post de blog antes que secciones principales |
| wikipedia.org | Portal | 70 s | 4/4 | ⚠️ saltó a Wikipedias de otros idiomas (subdominios) |
| news.ycombinator.com | Tablas | 38 s | 4/4 | ✅ |
| gob.pe | Gubernamental | 91 s | 4/4 | ⚠️ "Búsquedas" capturada 2 veces (misma página, distinto query) |
| upao.edu.pe | Universitario | 85 s | 4/4 | ⚠️ eligió noticias y un manual en vez de secciones principales |
| amazon.com | Comercio (anti-bot) | 99 s | 4/4 | ✅ sin bloqueo; HTML de 1,5 MB por interfaz |
| frontmind-frontend (propio) | SPA React | 35 s | 3/3 | ✅ (sólo páginas públicas) |
| the-internet.herokuapp.com | **Con login** | 61 s | 4/5 | ⚠️ login correcto; "Two Factor" marcada como "sesión perdida" (falso: la página tiene un campo de contraseña); además capturó la propia página de login como interfaz |
| practicetestautomation.com | **Con login** | 79 s | 5/5 | ❌ **el login automático falló** con credenciales válidas y un formulario estándar; capturó sólo páginas públicas sin avisar claramente al usuario |

Además, en 4 de estos sitios la réplica cambió el puntaje global frente al original: UPAO 53 → 62,
Amazon 63 → 76, practicetestautomation 80 → 86 (la réplica *oculta* problemas), the-internet 92 → 87 (agrega
falsos). Esto confirma E-1.

Tiempo total para 4 interfaces: **19–99 s** (promedio ≈ 62 s). Con 10 interfaces se esperan 2–4 min (ver C-1).

- **🟠 T-0. Login automático poco fiable.** Falló en un formulario estándar (`#username`, `#password`, `#submit`) y
  cuando falla el flujo continúa con páginas públicas; el resultado dice `login_succeeded: false` pero la
  auditoría se presenta como completa. *Mejora:* si el login falla, detener y pedir selectores manuales; mostrar
  claramente "no se pudo iniciar sesión". La detección de "página de login" por campo de contraseña visible
  produce falsos positivos (p. ej. 2FA, cambio de contraseña).

**Problemas del motor de scraping**

- **🟡 T-1. Sale del sitio.** `is_safe_internal_url` compara un "dominio base" heurístico
  (`route_discovery_service.py:82-91`): todos los `*.wikipedia.org` (observado), todos los `*.github.io` o
  cualquier `*.co.uk` cuentan como el mismo sitio. *Mejora:* mismo host por defecto, o Public Suffix List (`tldextract`).
- **🟡 T-2. No reproducible** (ver E-7) y no prioriza la navegación principal.
- **🟡 T-3. Doble navegación.** Cada ruta se carga en el descubrimiento y otra vez en la captura: casi duplica el tiempo.
- **🟡 T-4. Capturas `full_page` sin límite de altura**: en páginas con scroll infinito generan imágenes enormes.
  Recortar (p. ej. 15 000 px).
- **🔵 T-5. Lista de exclusión por subcadena**: "pay" excluye `/display`; faltan `salir`, `cerrar_sesion`,
  `unsubscribe`, `cancel`.
- **🔵 T-6. Ética del rastreo.** User-Agent falso de Chrome 120, no se consulta `robots.txt`. Para una tesis conviene un
  UA identificable (`FrontMind-Audit/1.1`) y respetar `robots.txt` o exigir la declaración de autorización (los
  términos ya la piden).

---

## 6. Privacidad

- **🟡 P-1.** El correo del usuario se envía a Abstract API (tercero, fuera del Perú) y los datos se alojan en
  Supabase/Render/HF; los términos sólo dicen "servicios en la nube de terceros". La Ley 29733 pide informar
  destinatarios y flujo transfronterizo. Nombrar los proveedores y el plazo de conservación (capturas: 24 h).
- **🟡 P-2.** El HTML capturado (que en sistemas autenticados puede contener datos personales) y la URL se guardan en
  `localStorage`; se borra al cerrar sesión (bien), pero persiste si el usuario sólo cierra el navegador.
  Usar `sessionStorage` o memoria.
- **🟡 P-3.** Capturas de páginas autenticadas accesibles por URL pública durante 24 h (el token de 128 bits impide
  adivinarlas, pero cualquiera con el enlace las ve). Considerar URLs firmadas de corta duración.
- **🟡 P-4.** El backend hace clic en "Aceptar todas" en los banners de cookies de los sitios auditados
  (`auth_service.py:83-110`): consiente en nombre de alguien. Preferir "Rechazar" / "Sólo necesarias".
- **🔵 P-5.** `history.json` del servidor duplica evaluaciones con `user_id` y no se borra cuando el usuario elimina su
  historial en Supabase (derecho de supresión).
- **✅** Credenciales del sitio auditado: no se guardan, no se registran en logs, la sesión temporal se elimina.

---

## 7. Usabilidad, compatibilidad y flexibilidad del propio FrontMind

- ✅ Registro e inicio de sesión: etiquetas correctas, un `<h1>`, `lang="es"`, sin desbordamiento a 375 px.
- 🔵 Faltan `autocomplete="email"` / `"new-password"` (WCAG 1.3.5) en los formularios de acceso.
- 🔵 Espera de 1–3 min sin estimación de tiempo; con C-1 resuelto, mostrar progreso por interfaz.
- 🔵 Dos escalas de calidad distintas en pantalla (E-5) confunden la lectura del reporte.
- 🔵 Compatibilidad: la CSP permite `localhost`; el build no define `browserslist` de soporte explícito en el README.

---

## 8. Plan de mejora priorizado

| # | Acción | Resuelve | Esfuerzo |
|---|---|---|---|
| 1 | Evaluar el DOM original de cada interfaz (no la réplica) y bloquear la edición antes de evaluar | E-1 | Bajo |
| 2 | Corregir falsos positivos (`required`, `max-width`, `body{}`, detección de estados) y unificar reglas con métricas | E-4, E-5 | Bajo |
| 3 | `fetch_css` sin redirecciones automáticas + tope de tamaño; `validate_url` con `is_global` y fallo cerrado | S-1, S-6 | Bajo |
| 4 | Desactivar clics en modo autenticado y abortar métodos no-GET tras el login | S-2 | Bajo |
| 5 | Puntaje por característica derivado de métricas X = A/B; "no evaluado" fuera del promedio | E-2, E-3 | Medio |
| 6 | Nuevas métricas de Seguridad, Adecuación funcional y Flexibilidad (sección 2.1) | E-1…E-4 | Medio |
| 7 | Captura asíncrona por `job_id`; detener la auditoría si el login falla | C-1, T-0 | Medio |
| 8 | Descubrimiento determinista y limitado al mismo host | E-7, T-1 | Bajo |
| 9 | Sanitizar la réplica; corregir `X-Forwarded-For`; límites en `/report/generate` | S-3, S-5, S-7 | Bajo |
| 10 | Términos con proveedores y plazos; `sessionStorage`; rechazar cookies | P-1…P-4 | Bajo |
| 11 | Compatibilidad multinavegador (Firefox/WebKit) | Sección 2.1 | Medio |
| 12 | `npm audit fix`, eliminar código muerto, instalar `pip-audit` | S-10, S-11 | Bajo |
