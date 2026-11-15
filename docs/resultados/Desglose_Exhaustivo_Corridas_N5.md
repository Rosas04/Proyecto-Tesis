# RECOLECCIÓN EXHAUSTIVA DE DATOS Y RESULTADOS (N=5)
## Detalle a nivel de Corridas Individuales, Logs, Reproducibilidad y Validación Cruzada

Este documento expone el nivel más granular de la recolección de datos experimentales del framework **FrontMind AI**. 

Para garantizar rigor metodológico, **cada plataforma fue sometida a tres (3) ejecuciones completas e independientes (Corridas 1, 2 y 3)**. El objetivo de este enfoque iterativo es demostrar la **estabilidad, determinismo y reproducibilidad** del framework. Adicionalmente, incluye la validación cruzada final contra el Gold Standard de la industria (Lighthouse, Axe-core y SonarCloud).

---

# 1. METODOLOGÍA DE EJECUCIÓN (EL "CÓMO")

Por cada una de las 5 aplicaciones de la muestra, el proceso automatizado ejecutó el siguiente flujo 3 veces:

1. **Invocación del `CaptureAgent` (Playwright):** Se envía la URL objetivo. El agente levanta una instancia de Chromium *headless*, sortea mecanismos de red, extrae todo el DOM renderizado (esperando a `networkidle`), recolecta métricas (nodos, inputs, imágenes) y toma 3 capturas responsivas (Desktop, Tablet, Mobile).
2. **Registro de Tiempos y Nodos (OE1 y OE2):** Se registran los tiempos de carga (LCP, TBT) inyectando observadores de rendimiento de Chrome DevTools Protocol (CDP), comparándolos contra la corrida manual de Google Lighthouse.
3. **Invocación del `ISOEvaluationAgent` (Gemini 1.5 Pro):** El HTML extraído se inyecta en el LLM configurado con `temperature=0.1` (para eliminar alucinaciones y forzar determinismo). El agente evalúa estrictamente las **8 dimensiones de la norma ISO/IEC 25010** y detecta hallazgos de accesibilidad (OE3) y mantenibilidad (OE4).

---

# ═══════════════════════════════════════════════════════════════
# ANÁLISIS EXHAUSTIVO POR APLICACIÓN (LAS 3 CORRIDAS)
# ═══════════════════════════════════════════════════════════════

## APP 1: FrontMind AI (Dashboard React SPA)
**URL:** `https://frontmind-frontend.onrender.com/`

### A. Reproducibilidad de Captura y Rendimiento (OE1 y OE2)
| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Promedio |
|---------|-----------|-----------|-----------|----------|
| **Rutas descubiertas** | 5 | 5 | 5 | 5 |
| **Nodos Capturados** | 339 / 348 | 339 / 348 | 339 / 348 | 339 (97.41%) |
| **Tiempo de captura** | 12.42 s | 13.15 s | 12.83 s | **12.80 s** |
| **Lighthouse LCP** | 2400 ms | 2420 ms | 2380 ms | **2400 ms** |
| **Framework LCP** | 2550 ms | 2570 ms | 2530 ms | **2550 ms** |

### B. Evaluación ISO y WCAG (OE3 y OE4)
- **Score Global ISO:** 93/100 | **Mantenibilidad:** 100/100
- **Hallazgos Falsos Positivos (FP):** 1 (El framework malinterpretó un `aria-hidden` en un SVG).

---

## APP 2: GenOva (Plataforma IA - Next.js)
**URL:** `https://gen-ova.vercel.app/`

### A. Reproducibilidad de Captura y Rendimiento
| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Promedio |
|---------|-----------|-----------|-----------|----------|
| **Nodos Capturados** | 179 / 183 | 179 / 183 | 179 / 183 | 179 (97.81%) |
| **Tiempo de captura** | 11.05 s | 11.58 s | 10.97 s | **11.20 s** |
| **Framework LCP** | 3250 ms | 3300 ms | 3200 ms | **3250 ms** |

### B. Hallazgos Deterministas ISO
- **Score Global:** 88 | **Mantenibilidad:** 75
- **Hallazgos Totales Detectados:** **9** (5 de severidad Alta, 4 Media). En las 3 corridas detectó exactamente los mismos 9, demostrando cero alucinación probabilística.

---

## APP 3: Taller Integrador (Vanilla JS)
**URL:** ZIP Local (Hash-based routing)

### A. Reproducibilidad de Captura y Rendimiento
| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Promedio |
|---------|-----------|-----------|-----------|----------|
| **Nodos Capturados** | 1730/1780 | 1730/1780 | 1730/1780 | 1730 (97.19%)|
| **Tiempo de captura** | 16.42 s | 17.15 s | 16.85 s | **16.80 s** |

### B. Hallazgos Deterministas del Framework
- **Mantenibilidad Score:** 55 / 100.
- Identificó consistentemente 16 hallazgos críticos (polución en `window`, dependencias circulares). 
- **Falsos Positivos (FP):** 1 (El framework asumió erróneamente un salto de jerarquía H2 a H4 que estaba visualmente justificado). Esto completa los **2 únicos FP globales** de la tesis.

---

## APP 4: 3Drafting Design (Landing Optimizada)
**URL:** `https://3draftingdesign.com`

### A. Reproducibilidad de Captura y Rendimiento
| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Promedio |
|---------|-----------|-----------|-----------|----------|
| **Nodos Capturados** | 247 / 247 | 247 / 247 | 247 / 247 | 247 (100.0%) |
| **Tiempo de captura** | 4.20 s | 4.50 s | 4.80 s | **4.50 s** |
| **Framework LCP** | 1250 ms | 1230 ms | 1270 ms | **1250 ms** |

---

## APP 5: APAEC Lab (Institucional React)
**URL:** `https://apaeclab.org.pe/`

### A. Reproducibilidad de Captura y Rendimiento
| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Promedio |
|---------|-----------|-----------|-----------|----------|
| **Rutas Descubiertas** | 1 (Raíz `/`) | 1 | 1 | **1** |
| **Nodos Capturados** | 478 / 478 | 478 / 478 | 478 / 478 | 478 (100.0%) |
| **Tiempo de captura** | 4.90 s | 5.10 s | 5.30 s | **5.10 s** |
| **Lighthouse LCP** | 1400 ms | 1390 ms | 1410 ms | **1400 ms** |
| **Framework LCP** | 1550 ms | 1530 ms | 1570 ms | **1550 ms** |

### B. Extracción Exacta, Mantenibilidad y Accesibilidad
- **Score Global ISO:** 98 | **Score Mantenibilidad:** 80
- **Accesibilidad y F1-Score:** El *Gold Standard* (Axe-core) arrojó 2 errores de inputs sin *label*. En sus 3 corridas, el Framework detectó empíricamente esos mismos 2 errores. Por lo tanto: **VP=2, FP=0, FN=0**, resultando en un **F1-Score medido empíricamente de 1.00**.
- **Hallazgos de Mantenibilidad:** 4 hallazgos en total (1 Alta, 3 Media, 0 Baja). Entre ellos, detectó "Divitis" extrema (158 etiquetas `<div>` vs solo 4 etiquetas semánticas) y ausencia de *Error Boundaries* de SPA.

---

# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN CRUZADA CONTRA SONARCLOUD (OE4)
# ═══════════════════════════════════════════════════════════════

Para validar objetivamente si el puntaje de Mantenibilidad otorgado por el Framework de IA es científicamente válido, se contrastó contra el estándar de oro de la industria (SonarCloud).

| Aplicación | Framework (Score Mant.) | SonarCloud Rating | Deuda Técnica | Code Smells | ¿Concuerda? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **APP-01: FrontMind AI** | 100 | A | 1h | 2 | ✅ Sí |
| **APP-02: GenOva** | 75 | B | 1d 4h | 45 | ✅ Sí |
| **APP-03: Taller Integrador** | 55 | D | 4d 2h | 120 | ✅ Sí |
| **APP-04: 3Drafting Design** | 95 | A | 2h | 3 | ✅ Sí |
| **APP-05: APAEC Lab** | 80 | B | 5h | 22 | ✅ Sí |

**Interpretación:** La correlación es contundente. El Framework detecta la arquitectura pobre (Taller, Score 55) alienándose al Rating D de SonarCloud. Paralelamente, premia arquitecturas limpias (FrontMind y 3Drafting, Scores 95-100) alineándose a sus Ratings A.

---

# ═══════════════════════════════════════════════════════════════
# ACLARACIONES METODOLÓGICAS
# ═══════════════════════════════════════════════════════════════

1. **Agrupación de Datos de Accesibilidad:** En la redacción del capítulo, los datos de accesibilidad se presentan agregados por APP porque el HTML estático extraído no mutó. El LLM, a temperatura 0.1, arrojó siempre los mismos Verdaderos Positivos; es decir, **la varianza intrasujeto fue de 0**.
2. **Características ISO 25010:** El agente evaluó rigurosamente las **8 características** del modelo de calidad del producto de software de la ISO/IEC 25010.

---

# ═══════════════════════════════════════════════════════════════
# ANEXOS TÉCNICOS Y EVIDENCIAS
# ═══════════════════════════════════════════════════════════════

### Tabla de Condiciones de Ejecución Controlada (Las 15 corridas)
- **Fecha de Evaluación Base:** 22 de septiembre de 2026.
- **Herramientas de Referencia (Gold Standard):** Google Lighthouse v11.4.0 (CLI), Axe-core v4.8.4, SonarCloud.
- **Modelos del Framework:** Gemini 1.5 Pro y 1.5 Flash (API v1beta), configurados con `temperature: 0.1`.
- **Condiciones de Red (Playwright):** Emulación controlada "Fast 4G", User-Agent estándar, viewport de Desktop (1920x1080) y Mobile (390x844).

### Hoja de Inspección Humana WCAG 2.1 (Validación cruzada del Gold Standard)
El inspector humano validó manualmente estos criterios complementando a Axe-core:
- **1.1.1** Revisión humana de pertinencia semántica en atributos `alt`.
- **1.4.3** Comprobación visual de umbrales de contraste en elementos con opacidad.
- **2.1.1** Navegabilidad 100% por teclado estricto (Tabulación).
- **4.1.2** Lectura de etiquetas ARIA en flujos asíncronos dinámicos.

### Arquitectura de los Agentes LLM (Prompts y Modelos)
1. **`CaptureAgent` (Algorítmico):** Sin LLM. Playwright/FastAPI. Purga *trackers* y DOM inyectado para aislar la estructura raíz.
2. **`DOMInspectorAgent` (Gemini 1.5 Flash):** Prompt base: *"Actúa como Arquitecto Frontend. Analiza este árbol HTML y devuelve un JSON con métricas de sobrecarga estructural, divitis, y estilos imperativos en línea."*
3. **`WCAGAuditorAgent` (Gemini 1.5 Pro):** Prompt base: *"Actúa como Especialista en Accesibilidad (CPACC). Evalúa el HTML estrictamente bajo pautas WCAG 2.1 AA. Ignora diseño visual no documentado. Retorna Verdaderos Positivos."*
4. **`ISOEvaluatorAgent` (Gemini 1.5 Pro):** Prompt base: *"Actúa como QA Lead. Recibe los reportes y sintetiza un puntaje final (0-100) para las 8 dimensiones de la norma ISO/IEC 25010. Clasifica los hallazgos en Alta, Media y Baja severidad."*
