# Operacionalización de ISO/IEC 25010 en FrontMind AI

Documento generado a partir de `services/iso_framework.py` (fuente única de verdad).

## 1. Restricciones normativas atendidas

| Restricción | Cómo se atiende en el sistema |
|---|---|
| 1. Nivel de abstracción / falta de prescripción métrica | Mapeo explícito característica → subcaracterística → métrica `X = A/B` con meta y referencia (tabla 3). |
| 2. Restricciones operativas (ISO/IEC 25040) | Cada evaluación y reporte declara herramientas, artefacto, entorno, tiempo/recursos (sección 5). |
| 3. Atributos subjetivos | Estética, aprendizaje, inteligibilidad y satisfacción se marcan como *parcial* o *no automatizable*; no se inventan puntajes. |
| 4. Dimensiones omitidas | Calidad de la información, fiabilidad, seguridad física y calidad en uso se declaran fuera de alcance (sección 4). |
| 5. Inviabilidad de evaluación integral | `POST /evaluate/iso` acepta `characteristics` (subconjunto priorizado); sólo esas entran al puntaje global. |

## 2. Escalas ISO/IEC 25040

**Severidad (0–4)** — cada hallazgo incluye `severity_grade`; cada métrica X = A/B se gradúa por cumplimiento relativo a su meta:

| Grado | Etiqueta | Criterio |
|---|---|---|
| 0 | No | Cumplimiento satisfactorio (> 90 %) |
| 1 | Cosmético | Defecto menor que no impide la operación (51 % – 89 %) |
| 2 | Menor | Inconveniente local que afecta la fluidez (11 % – 50 %) |
| 3 | Mayor | Fallo grave que dificulta completar tareas clave (1 % – 10 %) |
| 4 | Catastrófico | Bloqueo crítico o incumplimiento total (< 1 %) |

Correspondencia con la severidad cualitativa de las reglas: Crítica → 4, Alta → 3, Media → 2, Baja → 1.

**Criterio de decisión (0–10)** — `iso25040.score_10 = puntaje global / 10`: [9.0–10.0] Alta · ]6.0–9.0[ Buena · ]2.0–6.0] Regular · [0.0–2.0] Mala.

## 3. Métricas implementadas

| ID | Característica | Subcaracterística | Métrica | Fórmula | Meta | Referencia |
|---|---|---|---|---|---|---|
| ACC-01 | Accesibilidad | Perceptible | Imágenes con texto alternativo | `X = A / B` | X ≥ 0.9 | WCAG 2.2 · 1.1.1 |
| ACC-02 | Accesibilidad | Comprensible | Controles de formulario etiquetados | `X = A / B` | X ≥ 0.9 | WCAG 2.2 · 1.3.1 / 3.3.2 |
| ACC-03 | Accesibilidad | Operable | Botones con nombre accesible | `X = A / B` | X ≥ 0.9 | WCAG 2.2 · 4.1.2 |
| ACC-04 | Accesibilidad | Operable | Enlaces con texto accesible | `X = A / B` | X ≥ 0.9 | WCAG 2.2 · 2.4.4 |
| ACC-05 | Accesibilidad | Comprensible | Idioma del documento declarado | `X = A / B` | X ≥ 1.0 | WCAG 2.2 · 3.1.1 |
| USA-01 | Usabilidad | Protección contra errores del usuario | Campos con validación declarativa | `X = A / B` | X ≥ 0.5 | ISO/IEC 25023 (adaptada) |
| USA-02 | Usabilidad | Protección contra errores del usuario | Mecanismo de mensajes de estado | `X = A / B` | X ≥ 1.0 | ISO/IEC 25023 (adaptada) |
| MAN-01 | Mantenibilidad | Modularidad | Proporción de contenedores semánticos | `X = A / B` | X ≥ 0.1 | ISO/IEC 25023 (adaptada) |
| MAN-02 | Mantenibilidad | Analizabilidad | Unicidad de identificadores | `X = A / B` | X ≥ 1.0 | ISO/IEC 25023 (adaptada) |
| MAN-03 | Mantenibilidad | Capacidad de ser modificado | Elementos sin estilos inline | `X = A / B` | X ≥ 0.9 | ISO/IEC 25023 (adaptada) |
| MS4M1 | Mantenibilidad | Capacidad de ser modificado | Complejidad ciclomática (aprox.) | `X = A + 1 (A = ramificaciones por función)` | 1 ≤ X < 15 | ISO/IEC 25023 MS4M1 (adaptada) |
| POR-01 | Portabilidad | Adaptabilidad | Viewport responsive declarado | `X = A / B` | X ≥ 1.0 | ISO/IEC 25023 (adaptada) |
| EFI-01 | Eficiencia de desempeño | Comportamiento temporal | Tiempo hasta el primer byte (TTFB) | `X = valor medido` | X ≤ 800 ms | Core Web Vitals (umbral 'bueno') |
| EFI-02 | Eficiencia de desempeño | Comportamiento temporal | Largest Contentful Paint (LCP) | `X = valor medido` | X ≤ 2500 ms | Core Web Vitals (umbral 'bueno') |
| EFI-03 | Eficiencia de desempeño | Comportamiento temporal | Cumulative Layout Shift (CLS) | `X = valor medido` | X ≤ 0.1 | Core Web Vitals (umbral 'bueno') |
| EFI-04 | Eficiencia de desempeño | Utilización de recursos | Datos transferidos | `X = valor medido` | X ≤ 3000 KB | Referencia práctica de peso de página |
| EFI-05 | Eficiencia de desempeño | Utilización de recursos | Peticiones de red | `X = valor medido` | X ≤ 100 | Referencia práctica |
| EFI-06 | Eficiencia de desempeño | Utilización de recursos | Memoria JS del cliente | `X = valor medido` | X ≤ 50 MB | Referencia práctica |

Las métricas EFI-* se miden con Playwright sobre la página original durante la captura (TTFB, LCP, CLS, bytes, peticiones, memoria JS). Si no hay medición se reportan como *no medido* y no penalizan.

## 4. Cobertura por subcaracterística

| Característica | Subcaracterística | Medición | Método | Limitación |
|---|---|---|---|---|
| Adecuación funcional | Completitud funcional | parcial (indicador aproximado) | Presencia de estructura principal (<main>, <h1>, controles, estados de carga/error). | Sin la especificación de requisitos no puede verificarse que se cubran todas las tareas del usuario. |
| Adecuación funcional | Exactitud funcional | no automatizable | Pruebas funcionales con casos y resultados esperados. | Requiere oráculos de prueba y datos esperados; no se infiere del DOM. |
| Adecuación funcional | Pertinencia funcional | parcial (indicador aproximado) | Navegación (<nav>) y controles interactivos disponibles. | Contar los pasos necesarios para una tarea requiere escenarios de uso definidos. |
| Eficiencia de desempeño | Comportamiento temporal | automatizada | TTFB, LCP y carga medidos con Playwright (Chromium) sobre la página original. | Medido desde el servidor de evaluación: depende de su red y hardware, no del dispositivo del usuario. |
| Eficiencia de desempeño | Utilización de recursos | automatizada | Bytes transferidos, número de peticiones y memoria JS del cliente (Playwright). | transferSize es 0 para recursos de otro origen sin Timing-Allow-Origin; la CPU no se mide. |
| Eficiencia de desempeño | Capacidad | no automatizable | Pruebas de carga y concurrencia (p. ej. Locust). | Requiere generar carga sobre el sistema auditado, fuera del alcance de una auditoría pasiva. |
| Usabilidad | Inteligibilidad (reconocimiento de adecuación) | no automatizable | Cuestionarios o juicio de expertos. | Depende de la percepción del usuario sobre sus propias necesidades. |
| Usabilidad | Capacidad de aprendizaje | no automatizable | Tiempo para completar la tarea correctamente en pruebas con usuarios. | Requiere participantes reales y cronometraje de tareas. |
| Usabilidad | Operabilidad | parcial (indicador aproximado) | Controles operables, foco de teclado y adaptación a 3 resoluciones. | Los pasos por unidad de tiempo requieren observar tareas reales. |
| Usabilidad | Protección contra errores del usuario | automatizada | Proporción de campos con validación declarativa y mensajes de estado (aria-live/role=alert). | No mide la tasa real de recuperación ante entradas inválidas. |
| Usabilidad | Estética de la interfaz | parcial (indicador aproximado) | Inspección objetiva: uniformidad de paleta, variables CSS, longitud de párrafos. | El agrado visual es subjetivo: requiere cuestionarios (p. ej. SUS) o juicio experto. |
| Accesibilidad | Accesibilidad técnica (WCAG: perceptible, operable, comprensible, robusto) | automatizada | Texto alternativo, etiquetas, nombres accesibles, idioma, contraste, orden de foco. | Las pruebas automáticas detectan sólo una parte de los criterios WCAG; se recomienda revisión con lector de pantalla. |
| Mantenibilidad | Modularidad | parcial (indicador aproximado) | Proporción de elementos semánticos y estilos desacoplados en el DOM. | MS1M1/MS1M2 (independencia y acoplamiento de componentes) requieren el código fuente y su grafo de dependencias. |
| Mantenibilidad | Reusabilidad | no automatizable | MS2M1: elementos reutilizados / elementos de la biblioteca. | Requiere el repositorio y la biblioteca de componentes del proyecto. |
| Mantenibilidad | Analizabilidad | parcial (indicador aproximado) | Unicidad de identificadores y estructura del DOM. | MS3M1/MS3M2 (pistas de auditoría y diagnóstico) requieren acceso a logs y especificación. |
| Mantenibilidad | Capacidad de ser modificado | parcial (indicador aproximado) | MS4M1: complejidad ciclomática aproximada de los scripts embebidos (X = A + 1). | En apps empaquetadas el JS está minificado; MS4M3 requiere historial de defectos. |
| Mantenibilidad | Capacidad de ser probado | no automatizable | MS5M1/MS5M2: cobertura y autonomía de las pruebas. | Requiere el código fuente y la suite de pruebas. |
| Compatibilidad | Coexistencia e interoperabilidad | parcial (indicador aproximado) | Estilos globales, polución de window, viewport responsive. | No se ejecuta en varios navegadores; sólo Chromium. |
| Seguridad | Confidencialidad e integridad (cliente) | parcial (indicador aproximado) | Patrones inseguros en el HTML (innerHTML sin sanitizar, datos sensibles en storage). | No es una prueba de penetración; no evalúa el backend ni la autenticación del sistema auditado. |
| Portabilidad | Adaptabilidad | automatizada | Estructura base, meta viewport y anchos rígidos; capturas en 1366, 768 y 390 px. | Instalabilidad y reemplazabilidad no aplican a una interfaz web desplegada. |

**Fuera de alcance:**

- **Fiabilidad:** Madurez, disponibilidad y tolerancia a fallos requieren monitoreo en el tiempo, no una captura puntual.
- **Seguridad física (Safety, ISO/IEC 25010:2023):** No aplica a interfaces web sin riesgo físico para personas o entorno.
- **Calidad en uso (efectividad, eficiencia, satisfacción):** Requiere usuarios reales, cuestionarios y tareas observadas.
- **Calidad de la información producida:** La norma no la contempla directamente y depende del dominio de los datos.

## 5. Restricciones de evaluación declaradas

- **Herramientas y metodología:** Análisis estático del DOM (BeautifulSoup) y ejecución en Chromium headless (Playwright). Las reglas son una operacionalización propia de la norma, que no prescribe algoritmos.
- **Artefacto evaluado:** HTML renderizado de cada interfaz (o su réplica). No se analiza el repositorio fuente, por lo que las métricas de modularidad, reusabilidad y testabilidad son parciales o no medibles.
- **Entorno de prueba:** Resoluciones 1366×768, 768×1024 y 390×844 en un único navegador (Chromium). Las métricas de desempeño se midieron una vez desde el servidor de evaluación.
- **Tiempo y recursos:** Máximo de interfaces configurable (por defecto 10), tiempo límite por página y hasta 2 capturas simultáneas.
- **Atributos subjetivos:** Estética, satisfacción y facilidad de aprendizaje se reportan como indicadores aproximados; su validación requiere cuestionarios o juicio de expertos.
- **Selección de características:** Se evalúa un subconjunto priorizado de características; las no seleccionadas o fuera de alcance no influyen en el puntaje global.

## 6. Parámetros solicitados sin medición automática

| Parámetro | Motivo | Método complementario |
|---|---|---|
| MS1M1 Capacidad de condensación / MS1M2 Acoplamiento | Requiere código fuente y grafo de dependencias | Análisis estático del repositorio (ZIP) con herramientas como dependency-cruiser |
| MS2M1 Reusabilidad | Requiere biblioteca de componentes | Inventario de componentes del repositorio |
| MS3M1/MS3M2 Pistas de auditoría y diagnóstico | Requiere logs y especificación | Revisión documental |
| MS4M2 Profundidad de herencia / MS4M3 Localización de corrección | Requiere jerarquía de clases e historial de defectos | Análisis del repositorio y del gestor de incidencias |
| MS5M1/MS5M2 Testabilidad | Requiere suite de pruebas | Reporte de cobertura (pytest-cov, vitest --coverage) |
| Capacidad de aprendizaje (tiempo de tarea) | Requiere usuarios reales | Pruebas de usabilidad cronometradas |
| Inteligibilidad y satisfacción / estética percibida | Atributos subjetivos | Cuestionario SUS o juicio de expertos |
| Operabilidad (pasos por unidad de tiempo) | Requiere escenarios de tarea | Pruebas de usabilidad con tareas definidas |
| Exactitud y completitud funcional | Requiere especificación de requisitos | Pruebas funcionales con oráculo |
| Capacidad (concurrencia) | Requiere generar carga sobre el sistema auditado | Pruebas de carga (Locust) |
| Uso de CPU | Chromium headless no expone CPU por página de forma fiable | Perfilado con DevTools/Lighthouse |
