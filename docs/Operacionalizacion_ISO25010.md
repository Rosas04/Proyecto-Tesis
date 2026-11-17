# Operacionalización de ISO/IEC 25010:2023 en FrontMind AI

Documento generado a partir de `frontmind-agents/services/iso_framework.py` e `iso_service.py` (fuente única de verdad).

## 1. Características evaluadas

| Característica | Tipo | Motivo |
|---|---|---|
| Adecuación funcional | Núcleo | Corrección funcional medida en ejecución; completitud y pertinencia frente a la lista de funciones esperadas. |
| Capacidad de interacción | Núcleo | Antes «usabilidad»; en 2023 incluye la inclusividad (accesibilidad WCAG 2.2 AA). |
| Compatibilidad | Núcleo | Interoperabilidad con APIs y entre motores de navegador (Chromium, Firefox y WebKit); coexistencia en el entorno compartido. |
| Flexibilidad | Núcleo | Antes «portabilidad»; se mide la adaptabilidad en cuatro anchos de pantalla. |
| Seguridad | Núcleo | Confidencialidad e integridad observables desde el cliente: transporte, cabeceras, cookies, credenciales y scripts. |
| Fiabilidad | Núcleo | Disponibilidad, ausencia de fallos y tolerancia a fallos al cargar cada interfaz. |
| Eficiencia de desempeño | Opcional | Opcional: sólo se puntúa si se marca «Incluir eficiencia de desempeño». |
| Mantenibilidad | Excluida | Requiere código fuente, grafo de dependencias e historial de defectos, no la interfaz desplegada. |

Las claves antiguas se traducen automáticamente: `usabilidad`/`accesibilidad` → `capacidad_interaccion`, `portabilidad` → `flexibilidad`.

## 2. Cálculo del puntaje

Cada métrica produce un cumplimiento *c* entre 0 y 1:

| Tipo | Fórmula | Cumplimiento |
|---|---|---|
| Proporción | X = A / B | c = min(1, X / meta) |
| Binaria | X = 1 si cumple, 0 si no | c = X |
| Conteo | X = nº de ocurrencias (meta 0) | c = 1 / (1 + X) |
| Máximo | X = valor medido | c = min(1, umbral / X) |

- **Puntaje de la característica** = 100 · Σ(peso · c) / Σ(peso) de sus métricas medidas.
- **Puntaje global** = promedio de las características evaluadas. Una característica sin métricas medidas figura como *no evaluada* y no entra al promedio (la ausencia de evidencia no se interpreta como calidad perfecta).
- **Hallazgos:** uno por cada métrica medida que no alcanza su meta. Su severidad es el grado por cumplimiento (escala 0–4), acotado por la severidad máxima de la métrica (tabla 3).
- **Criterio de decisión (0–10):** 9.0–10.0 Alta · 6.0–9.0 Buena · 2.0–6.0 Regular · 0.0–2.0 Mala.

**Escala de severidad**

| Grado | Etiqueta | Cumplimiento |
|---|---|---|
| 0 | No | Cumplimiento satisfactorio (≥ 90 %) |
| 1 | Cosmético | Defecto menor que no impide la operación (51 % – 89 %) |
| 2 | Menor | Inconveniente local que afecta la fluidez (11 % – 50 %) |
| 3 | Mayor | Fallo grave que dificulta completar tareas clave (1 % – 10 %) |
| 4 | Catastrófico | Bloqueo crítico o incumplimiento total (< 1 %) |

## 3. Métricas implementadas

| ID | Característica | Subcaracterística | Métrica | Fórmula | Meta | Peso | Severidad máx. | Referencia |
|---|---|---|---|---|---|---|---|---|
| AF-01 | Adecuación funcional | Completitud funcional | Funciones esperadas presentes | `X = A / B` | X ≥ 1 | 2.0 | Alta | ISO/IEC 25023 · cobertura funcional |
| AF-04 | Adecuación funcional | Pertinencia funcional | Funciones esperadas disponibles como control operable | `X = A / B` | X ≥ 1 | 1.5 | Alta | ISO/IEC 25023 · pertinencia funcional |
| AF-02 | Adecuación funcional | Corrección funcional | Enlaces internos que responden sin error | `X = A / B` | X ≥ 1 | 1.5 | Alta | ISO/IEC 25023 · corrección funcional |
| AF-03 | Adecuación funcional | Corrección funcional | Imágenes de contenido que cargan | `X = A / B` | X ≥ 1 | 1.0 | Media | ISO/IEC 25023 · corrección funcional |
| CI-01 | Capacidad de interacción | Inclusividad | Imágenes con texto alternativo | `X = A / B` | X ≥ 0.9 | 1.0 | Alta | WCAG 2.2 · 1.1.1 |
| CI-02 | Capacidad de interacción | Inclusividad | Controles de formulario etiquetados | `X = A / B` | X ≥ 0.9 | 1.0 | Alta | WCAG 2.2 · 1.3.1 / 3.3.2 / 4.1.2 |
| CI-03 | Capacidad de interacción | Inclusividad | Botones con nombre accesible | `X = A / B` | X ≥ 0.9 | 1.0 | Alta | WCAG 2.2 · 4.1.2 |
| CI-04 | Capacidad de interacción | Inclusividad | Enlaces con nombre accesible | `X = A / B` | X ≥ 0.9 | 1.0 | Alta | WCAG 2.2 · 2.4.4 |
| CI-05 | Capacidad de interacción | Inclusividad | Idioma del documento declarado | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Media | WCAG 2.2 · 3.1.1 |
| CI-06 | Capacidad de interacción | Inclusividad | Texto con contraste suficiente | `X = A / B` | X ≥ 0.9 | 1.0 | Alta | WCAG 2.2 · 1.4.3 |
| CI-07 | Capacidad de interacción | Inclusividad | Zoom del usuario permitido | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Alta | WCAG 2.2 · 1.4.4 |
| CI-08 | Capacidad de interacción | Operabilidad | Objetivos táctiles de al menos 24×24 px (móvil) | `X = A / B` | X ≥ 0.9 | 1.0 | Media | WCAG 2.2 · 2.5.8 |
| CI-09 | Capacidad de interacción | Operabilidad | Orden de foco natural (sin tabindex positivo) | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Media | WCAG 2.2 · 2.4.3 |
| CI-10 | Capacidad de interacción | Protección contra errores del usuario | Campos con validación declarativa | `X = A / B` | X ≥ 0.5 | 1.0 | Media | ISO/IEC 25023 · protección contra errores |
| CI-11 | Capacidad de interacción | Protección contra errores del usuario | Campos de datos personales con autocompletado | `X = A / B` | X ≥ 0.9 | 0.5 | Media | WCAG 2.2 · 1.3.5 |
| CI-12 | Capacidad de interacción | Asistencia al usuario | Región de mensajes de estado | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Media | WCAG 2.2 · 4.1.3 |
| CI-13 | Capacidad de interacción | Autodescriptividad | Título de página descriptivo | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Media | WCAG 2.2 · 2.4.2 |
| CI-14 | Capacidad de interacción | Autodescriptividad | Encabezado principal presente | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Baja | WCAG 2.2 · 1.3.1 / 2.4.6 |
| CI-15 | Capacidad de interacción | Operabilidad | Texto legible en móvil (≥ 12 px) | `X = A / B` | X ≥ 0.6 | 1.0 | Media | Lighthouse · Legible font sizes |
| CO-01 | Compatibilidad | Interoperabilidad | Peticiones a API completadas sin error | `X = A / B` | X ≥ 0.95 | 1.5 | Alta | ISO/IEC 25023 · interoperabilidad |
| CO-02 | Compatibilidad | Interoperabilidad | Navegadores donde la interfaz funciona sin errores nuevos | `X = A / B` | X ≥ 1 | 2.0 | Alta | ISO/IEC 25023 · compatibilidad entre plataformas |
| CO-03 | Compatibilidad | Interoperabilidad | Diseño coherente con Chromium en otros motores | `X = A / B` | X ≥ 1 | 1.0 | Media | ISO/IEC 25023 · compatibilidad entre plataformas |
| CO-04 | Compatibilidad | Coexistencia | Variables globales añadidas al navegador | `X = valor medido` | X ≤ 50 | 0.5 | Baja | Referencia práctica (aislamiento de módulos) |
| FL-01 | Flexibilidad | Adaptabilidad | Meta viewport adaptable declarado | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Alta | HTML Living Standard · viewport |
| FL-02 | Flexibilidad | Adaptabilidad | Resoluciones sin desplazamiento horizontal | `X = A / B` | X ≥ 1 | 2.0 | Alta | ISO/IEC 25023 · adaptabilidad |
| FL-03 | Flexibilidad | Adaptabilidad | Reflow a 320 px sin desplazamiento horizontal | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Media | WCAG 2.2 · 1.4.10 |
| FL-04 | Flexibilidad | Instalabilidad | Manifiesto de aplicación web instalable | `X = 1 si cumple, 0 si no` | X = 1 | informativa | — | W3C Web App Manifest |
| SE-01 | Seguridad | Confidencialidad | Conexión cifrada (HTTPS) | `X = 1 si cumple, 0 si no` | X = 1 | 3.0 | Crítica | OWASP Secure Headers / ASVS 4.0 · V9.1 |
| SE-02 | Seguridad | Confidencialidad | Certificado TLS válido | `X = 1 si cumple, 0 si no` | X = 1 | 2.0 | Crítica | OWASP Secure Headers / ASVS 4.0 · V9.1 |
| SE-03 | Seguridad | Confidencialidad | HSTS (Strict-Transport-Security) | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Media | OWASP Secure Headers / ASVS 4.0 · V14.4.5 |
| SE-04 | Seguridad | Confidencialidad | Redirección de HTTP a HTTPS | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Media | OWASP Secure Headers / ASVS 4.0 · V9.1 |
| SE-05 | Seguridad | Confidencialidad | Formularios de contraseña enviados por HTTPS y POST | `X = A / B` | X ≥ 1 | 3.0 | Crítica | OWASP Secure Headers / ASVS 4.0 · V8.3.1 |
| SE-06 | Seguridad | Confidencialidad | Recursos sin contenido mixto | `X = número de ocurrencias` | X = 0 | 1.5 | Alta | W3C Mixed Content |
| SE-07 | Seguridad | Confidencialidad | Cookies con atributo Secure | `X = A / B` | X ≥ 1 | 1.0 | Media | OWASP Secure Headers / ASVS 4.0 · V3.4.1 |
| SE-08 | Seguridad | Confidencialidad | Credenciales fuera de Web Storage | `X = 1 si cumple, 0 si no` | X = 1 | 1.5 | Alta | OWASP Secure Headers / ASVS 4.0 · V3.2.3 |
| SE-09 | Seguridad | Integridad | Content-Security-Policy definida | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Media | OWASP Secure Headers / ASVS 4.0 · V14.4.3 |
| SE-10 | Seguridad | Integridad | Protección contra clickjacking | `X = 1 si cumple, 0 si no` | X = 1 | 1.0 | Media | OWASP Secure Headers / ASVS 4.0 · V14.4.7 |
| SE-11 | Seguridad | Integridad | X-Content-Type-Options: nosniff | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Baja | OWASP Secure Headers / ASVS 4.0 · V14.4.4 |
| SE-12 | Seguridad | Integridad | Scripts de terceros con integridad verificada (SRI) | `X = A / B` | X ≥ 1 | 0.5 | Baja | OWASP Secure Headers / ASVS 4.0 · V14.2.3 |
| SE-13 | Seguridad | Confidencialidad | Política de referencia (Referrer-Policy) | `X = 1 si cumple, 0 si no` | X = 1 | 0.5 | Baja | OWASP Secure Headers / ASVS 4.0 · V14.4.6 |
| FI-01 | Fiabilidad | Disponibilidad | La interfaz responde sin error HTTP | `X = 1 si cumple, 0 si no` | X = 1 | 2.0 | Crítica | ISO/IEC 25023 · disponibilidad |
| FI-02 | Fiabilidad | Ausencia de fallos | Errores JavaScript no capturados | `X = número de ocurrencias` | X = 0 | 1.5 | Alta | ISO/IEC 25023 · ausencia de fallos |
| FI-03 | Fiabilidad | Ausencia de fallos | Errores registrados en consola | `X = número de ocurrencias` | X = 0 | 0.5 | Baja | ISO/IEC 25023 · ausencia de fallos |
| FI-04 | Fiabilidad | Tolerancia a fallos | Recursos cargados sin error | `X = A / B` | X ≥ 0.98 | 1.0 | Media | ISO/IEC 25023 · tolerancia a fallos |
| EF-01 | Eficiencia de desempeño | Comportamiento temporal | Tiempo hasta el primer byte (TTFB) | `X = valor medido` | X ≤ 800 ms | 1.0 | Media | Core Web Vitals (umbral 'bueno') |
| EF-02 | Eficiencia de desempeño | Comportamiento temporal | Largest Contentful Paint (LCP) | `X = valor medido` | X ≤ 2500 ms | 1.0 | Media | Core Web Vitals (umbral 'bueno') |
| EF-03 | Eficiencia de desempeño | Comportamiento temporal | Cumulative Layout Shift (CLS) | `X = valor medido` | X ≤ 0.1 | 1.0 | Media | Core Web Vitals (umbral 'bueno') |
| EF-04 | Eficiencia de desempeño | Utilización de recursos | Datos transferidos | `X = valor medido` | X ≤ 3000 KB | 1.0 | Media | Referencia práctica de peso de página |
| EF-05 | Eficiencia de desempeño | Utilización de recursos | Peticiones de red | `X = valor medido` | X ≤ 100 | 0.5 | Baja | Referencia práctica |
| EF-06 | Eficiencia de desempeño | Utilización de recursos | Memoria JS del cliente | `X = valor medido` | X ≤ 50 MB | 0.5 | Baja | Referencia práctica |

**Origen de los datos:** las métricas CI-01…CI-05, CI-07, CI-09…CI-14 y FL-01 se calculan sobre el DOM original; el resto se mide en ejecución con Playwright durante la captura (`services/evidence_collector.py`): red, cabeceras, cookies, TLS (validado con el almacén del sistema y, si falta la CA intermedia, con certifi), diseño en 1366/768/390/320 px y carga en Firefox y WebKit. Las comprobaciones de enlaces (HEAD, sin seguir redirecciones), de redirección HTTP→HTTPS y de TLS se hacen sólo contra el mismo host ya validado por la política SSRF. Los enlaces con palabras como *logout*, *salir*, *delete*, *eliminar* o *checkout* no se verifican.

**Criterios de los casos límite:** un enlace con 401/403 existe pero exige permisos (no es roto) y 429 no es concluyente; un formulario con contraseña es inseguro si su destino es `http://` o si se envía de forma nativa por GET a un `action` explícito (los formularios sin `action` los procesa JavaScript); en WCAG 2.5.8 se aplican las excepciones de enlace en línea y de espaciado (círculo de 24 px); CO-02 sólo penaliza errores JavaScript *adicionales* a los de Chromium, para no contar dos veces lo que mide FI-02.

## 4. Cobertura por subcaracterística

| Característica | Subcaracterística | Medición | Método | Limitación |
|---|---|---|---|---|
| Adecuación funcional | Completitud funcional | parcial (indicador aproximado) | AF-01: funciones esperadas (declaradas por el evaluador) presentes en la interfaz. | Requiere la lista de funciones esperadas; sin ella no se evalúa. |
| Adecuación funcional | Corrección funcional | automatizada | AF-02 enlaces internos que responden sin error; AF-03 imágenes de contenido que cargan. | No verifica que los cálculos o datos mostrados sean correctos (requiere oráculos de prueba). |
| Adecuación funcional | Pertinencia funcional | parcial (indicador aproximado) | AF-04: funciones esperadas disponibles como control operable (enlace, botón o campo). | Requiere la lista de funciones esperadas; no mide el número de pasos de una tarea. |
| Capacidad de interacción | Reconocibilidad de adecuación | no automatizable | Cuestionarios o juicio de expertos. | Depende de la percepción del usuario. |
| Capacidad de interacción | Aprendibilidad | no automatizable | Tiempo para completar tareas en pruebas con usuarios. | Requiere participantes reales. |
| Capacidad de interacción | Operabilidad | automatizada | CI-08 objetivos táctiles ≥ 24 px (WCAG 2.5.8), CI-09 orden de foco (2.4.3), CI-15 texto legible en móvil. | No mide el esfuerzo real de operación de una tarea. |
| Capacidad de interacción | Protección contra errores del usuario | automatizada | CI-10 validación declarativa, CI-11 autocompletado de datos personales (WCAG 1.3.5). | No mide la tasa real de recuperación ante entradas inválidas. |
| Capacidad de interacción | Compromiso del usuario | no automatizable | Cuestionarios (p. ej. SUS, UEQ). | Atributo subjetivo. |
| Capacidad de interacción | Inclusividad | automatizada | CI-01…CI-07: texto alternativo, etiquetas, nombres accesibles, idioma, contraste y zoom (WCAG 2.2 AA). | Las pruebas automáticas cubren sólo una parte de WCAG; se recomienda revisión con lector de pantalla. |
| Capacidad de interacción | Asistencia al usuario | parcial (indicador aproximado) | CI-12: región de mensajes de estado en interfaces con formularios (WCAG 4.1.3). | No evalúa la calidad de la ayuda ofrecida. |
| Capacidad de interacción | Autodescriptividad | automatizada | CI-13 título de página (WCAG 2.4.2), CI-14 encabezado principal. | No evalúa si el texto es comprensible. |
| Compatibilidad | Coexistencia | parcial (indicador aproximado) | CO-04: variables globales añadidas al entorno compartido del navegador. | No se prueba junto a otros productos concretos (extensiones, widgets). |
| Compatibilidad | Interoperabilidad | automatizada | CO-01 peticiones a API exitosas; CO-02 carga sin errores nuevos en Chromium, Firefox y WebKit; CO-03 diseño coherente entre motores. | Navegadores de escritorio en modo headless; no cubre versiones antiguas ni navegadores móviles reales. |
| Flexibilidad | Adaptabilidad | automatizada | FL-01 meta viewport, FL-02 sin desbordamiento en 1366/768/390 px, FL-03 reflow a 320 px (WCAG 1.4.10). | Resoluciones simuladas en un navegador headless. |
| Flexibilidad | Escalabilidad | no automatizable | Pruebas de carga creciente. | Requiere generar carga sobre el sistema auditado. |
| Flexibilidad | Instalabilidad | parcial (indicador aproximado) | FL-04 (informativa): manifiesto de aplicación web instalable. | Sólo aplica si el sistema pretende instalarse (PWA); no puntúa. |
| Flexibilidad | Reemplazabilidad | no automatizable | Análisis de dependencias y contratos de integración. | Requiere documentación del sistema. |
| Seguridad | Confidencialidad | automatizada | SE-01 HTTPS, SE-02 certificado válido, SE-03 HSTS, SE-04 redirección HTTP→HTTPS, SE-05 formularios de contraseña seguros, SE-06 sin contenido mixto, SE-07 cookies Secure, SE-08 credenciales fuera de Web Storage, SE-13 Referrer-Policy. | Observación pasiva de la interfaz; no es una prueba de penetración. |
| Seguridad | Integridad | automatizada | SE-09 Content-Security-Policy, SE-10 protección anti-clickjacking, SE-11 nosniff, SE-12 SRI en scripts de terceros. | Comprueba la presencia de la política, no su solidez completa. |
| Seguridad | No repudio, responsabilidad y autenticidad | no automatizable | Revisión de registros de auditoría y del mecanismo de autenticación. | Ocurre en el servidor; no es observable desde la interfaz. |
| Seguridad | Resistencia | no automatizable | Pruebas de penetración autorizadas. | Fuera del alcance de una auditoría pasiva. |
| Fiabilidad | Disponibilidad | automatizada | FI-01: la interfaz responde sin error HTTP. | Medición puntual; la disponibilidad sostenida requiere monitoreo en el tiempo. |
| Fiabilidad | Ausencia de fallos | automatizada | FI-02 errores JavaScript no capturados, FI-03 errores en consola. | Sólo detecta fallos que ocurren al cargar la interfaz, no durante tareas. |
| Fiabilidad | Tolerancia a fallos | automatizada | FI-04: recursos (scripts, estilos, imágenes, API) cargados sin error. | No inyecta fallos de red para observar la degradación. |
| Fiabilidad | Recuperabilidad | no automatizable | Pruebas de recuperación ante caídas. | Requiere provocar fallos en el sistema. |
| Eficiencia de desempeño | Comportamiento temporal | automatizada | EF-01 TTFB, EF-02 LCP, EF-03 CLS medidos con Playwright. | Medido desde el servidor de evaluación, no desde el dispositivo del usuario. |
| Eficiencia de desempeño | Utilización de recursos | automatizada | EF-04 bytes transferidos, EF-05 peticiones, EF-06 memoria JS. | transferSize es 0 en recursos de otro origen sin Timing-Allow-Origin. |
| Eficiencia de desempeño | Capacidad | no automatizable | Pruebas de carga y concurrencia. | Requiere generar carga sobre el sistema auditado. |

**Fuera de alcance:**

- **Mantenibilidad:** Sus métricas (modularidad, reusabilidad, analizabilidad, capacidad de prueba) requieren el código fuente, el grafo de dependencias y el historial de defectos, no la interfaz desplegada.
- **Seguridad física (Safety, ISO/IEC 25010:2023):** No aplica a interfaces web sin riesgo físico para personas o entorno.
- **Calidad en uso (efectividad, eficiencia, satisfacción):** Requiere usuarios reales, cuestionarios y tareas observadas.

## 5. Condiciones de la evaluación

- **Herramientas y metodología:** Análisis del DOM renderizado (BeautifulSoup) y observación en ejecución con Playwright (Chromium, Firefox y WebKit). Las métricas son una operacionalización propia de la norma.
- **Artefacto evaluado:** DOM original de cada interfaz capturada (no su réplica). No se analiza el código fuente.
- **Entorno de prueba:** Resoluciones 1366×768, 768×1024, 390×844 y 320×640 en navegadores headless. Las evidencias de ejecución se midieron una vez desde el servidor de evaluación.
- **Tiempo y recursos:** Máximo de interfaces configurable (por defecto 10), hasta 15 enlaces verificados por interfaz y compatibilidad multinavegador en las primeras 5 interfaces.
- **Atributos subjetivos:** Aprendibilidad, compromiso y reconocibilidad requieren cuestionarios o juicio experto y no se puntúan.
- **Selección de características:** Se evalúan Adecuación funcional, Capacidad de interacción, Compatibilidad, Flexibilidad, Seguridad y Fiabilidad; Eficiencia de desempeño es opcional. Las características sin métricas medidas no influyen en el puntaje global.

## 6. Configuración

| Variable | Por defecto | Uso |
|---|---|---|
| `COMPAT_BROWSERS` | `firefox,webkit` | Motores adicionales para compatibilidad |
| `COMPAT_MAX_INTERFACES` | `3` | Interfaces verificadas en otros motores |
| `COMPAT_BUDGET_S` | `150` | Tiempo máximo de la verificación multinavegador |
| `EVIDENCE_MAX_LINKS` | `15` | Enlaces internos verificados por interfaz |
| `EVIDENCE_LINK_BUDGET_S` | `20` | Tiempo máximo de verificación de enlaces por interfaz |
