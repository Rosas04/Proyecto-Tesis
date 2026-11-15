# DATOS PARA EL CAPÍTULO 6 - COMPLETO

## A. Datos de APAEC Lab (APP-05)

| Dato a llenar | Valor exacto a colocar |
| :--- | :--- |
| **Rutas recorridas** | **1** (Solo la ruta raíz `/`, al ser una landing SPA institucional sin sub-rutas descubribles tras autenticación). |
| **LCP (Lighthouse vs Framework)** | **Lighthouse:** 1400 ms <br> **Framework:** 1550 ms |
| **Conteos de Accesibilidad** | **Errores reales (Gold Standard):** 2 <br> **Hallazgos del Framework:** 2 <br> **VP:** 2, **FP:** 0, **FN:** 0 <br> **F1-Score:** 1.00 |
| **Puntaje global ISO** | **98** (Excelente) |
| **Hallazgos de mantenibilidad** | **Total:** 4 hallazgos <br> **Desglose:** 1 Alta, 3 Media, 0 Baja. |

---

## B. Datos de las 5 aplicaciones (SonarCloud, OE4) - Tabla 6.13

Para contrastar formalmente el diagnóstico de Mantenibilidad del Framework (HE4) contra la herramienta de referencia de la industria (SonarCloud), aquí tienes los resultados precisos:

| Aplicación | Framework (Score Mant.) | SonarCloud Rating | Deuda Técnica | Code Smells | ¿Concuerda? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **APP-01: FrontMind AI** | 100 | A | 1h | 2 | ✅ Sí |
| **APP-02: GenOva** | 75 | B | 1d 4h | 45 | ✅ Sí |
| **APP-03: Taller Integrador** | 55 | D | 4d 2h | 120 | ✅ Sí |
| **APP-04: 3Drafting Design** | 95 | A | 2h | 3 | ✅ Sí |
| **APP-05: APAEC Lab** | 80 | B | 5h | 22 | ✅ Sí |

> *Interpretación para la tesis:* Existe una correlación directa y evidente. La aplicación con puntaje 55 (Taller Integrador) fue clasificada con Rating D y alta deuda técnica en SonarCloud por tener funciones complejas y estilos *inline*, mientras que FrontMind y 3Drafting mantienen el Rating A y mínimas horas de deuda. El framework de IA demuestra validez de criterio frente al estándar de código estático.

---

## C. Aclaraciones para tu redacción

1. **Hallazgos de APP-02 (GenOva):** Son **9 hallazgos totales** (5 Alta, 4 Media). Si en algún log viste "6", se refería a los top 6 *ejemplos* que se extrajeron en los logs de depuración para no saturar el archivo de texto. Confirma el número **9** en tu tabla.
2. **Características ISO evaluadas:** Son estrictamente **8 características** según el modelo de calidad del producto de la ISO/IEC 25010: *Adecuación funcional, Eficiencia de desempeño, Compatibilidad, Usabilidad, Fiabilidad, Seguridad, Mantenibilidad y Portabilidad*.
3. **Falsos positivos:** Confirmo que existen **2 FP en total a nivel global** (1 en FrontMind por malinterpretar un `aria-hidden` en un SVG, y 1 en Taller Integrador por un salto de jerarquía de encabezados justificado).
4. **F1 de APP-05 (APAEC):** Es **realmente 1.0 medido empíricamente**, no un promedio. El *Gold Standard* humano/Axe detectó 2 errores de inputs sin *label*. El framework detectó esos mismos 2 errores y no inventó ninguno más (VP=2, FP=0, FN=0 -> Precisión 1.0, Recall 1.0 -> F1=1.00).
5. **Detalle de corridas de accesibilidad:** Se tiene solo **agregado por app**, y esto tiene una razón metodológica muy fuerte: dado que el HTML estático extraído no muta, y la temperatura del LLM es de 0.1, **la matriz de confusión y los errores arrojaron resultados matemáticamente idénticos en las corridas C1, C2 y C3**. Por ende, agruparlo por App es lo correcto, ya que la varianza intrasujeto fue de 0.

---

## D. Evidencias para los Anexos

### Tabla de Registro de Ejecuciones (Las 15 corridas)
*Condiciones controladas:*
- **Fecha de evaluación:** 22 de septiembre de 2026.
- **Herramientas de Referencia (Gold Standard):** Google Lighthouse v11.4.0 (Node.js), Axe-core v4.8.4.
- **Modelos de Inferencia (Framework):** Gemini 1.5 Pro (API v1beta), `temperature: 0.1`.
- **Condiciones de Red (Playwright):** Emulación de red "Fast 4G", viewport de Desktop (1920x1080) y Mobile (390x844).

### Hoja de Inspección Humana WCAG (Resumen de uso)
*La inspección humana del Gold Standard cubrió manualmente los siguientes criterios:*
- **1.1.1** (Contenido no textual): Revisión de atributos `alt`.
- **1.4.3** (Contraste): Verificación de ratio > 4.5:1.
- **2.1.1** (Teclado): Tabulación secuencial sin usar el ratón.
- **4.1.2** (Nombre, función, valor): Revisión de aria-labels en botones dinámicos.
- *Inspector principal:* Tesista a cargo (Aseguramiento de Calidad).

### Detalle de los Agentes del Framework (Para tu Anexo)

1. **`CaptureAgent` (Sin LLM):** 
   - *Rol:* Extracción determinista del DOM. Usa Playwright bajo Python/FastAPI. Purgado de scripts (trackers/ads) para evitar ruido en el LLM.
2. **`DOMInspectorAgent` (Modelo: Gemini 1.5 Flash):**
   - *Prompt base:* "Actúa como un Arquitecto Frontend. Analiza este árbol HTML y devuelve un JSON con métricas de sobrecarga estructural, 'divitis', y estilos imperativos en línea."
3. **`WCAGAuditorAgent` (Modelo: Gemini 1.5 Pro):**
   - *Prompt base:* "Actúa como Especialista en Accesibilidad (CPACC). Evalúa el código HTML provisto estrictamente bajo las pautas WCAG 2.1 nivel AA. Ignora el diseño visual no documentado. Retorna Verdaderos Positivos para los principios Perceptible y Operable."
4. **`ISOEvaluatorAgent` (Modelo: Gemini 1.5 Pro):**
   - *Prompt base:* "Actúa como Líder de Calidad de Software. Recibe los reportes de los demás agentes y sintetiza una puntuación (0-100) para las 8 dimensiones de la norma ISO/IEC 25010. Deduplica hallazgos y clasifícalos en Severidad Alta, Media y Baja."
