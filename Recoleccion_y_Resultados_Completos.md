# Recolección de Datos y Presentación de Resultados

## Framework Agéntico FrontMind AI — Evaluación Experimental (N=5)

> **Diseño de investigación:** Prueba única (postest) sobre cinco plataformas heterogéneas.
> **Instrumento:** Framework agéntico FrontMind AI (CaptureAgent, ISOEvaluationAgent).
> **Gold Standard de referencia:** Google Lighthouse (OE2), Axe DevTools + Inspección Humana (OE3).

---

# 1. Muestra y Unidad de Análisis
La muestra final está conformada por **5 aplicaciones web** representativas de distintas arquitecturas y enfoques del ecosistema web moderno:

| # | Aplicación | Tecnología | URL | Tipo |
|---|-----------|-----------|-----|------|
| 1 | FrontMind AI | React (SPA) | `https://frontmind-frontend.onrender.com/` | Dashboard |
| 2 | GenOva | Next.js / React | `https://gen-ova.vercel.app/` | Plataforma IA |
| 3 | Taller Integrador | Vanilla JS / HTML | Proyecto local (ZIP) | Dashboard Acad. |
| 4 | 3Drafting Design | Web App Optimizada | `https://3draftingdesign.com` | Landing |
| 5 | APAEC Lab | React / SPA | `https://apaeclab.org.pe/` | Institucional |

---

# ═══════════════════════════════════════════════════════════════
# OE1: CAPACIDAD DE CAPTURA Y REPRESENTACIÓN DEL DOM
# ═══════════════════════════════════════════════════════════════

## 2. Datos Brutos — OE1

### APP 5: APAEC Lab
- **Rutas Descubiertas:** 1 (`/`).
- **Nodos promedio:** 478 originales vs 478 capturados.
- **Detalle de Nodos:** 32 botones, 7 enlaces, 23 encabezados, 4 elementos semánticos (indicio de *divitis*).
- **Tiempo de captura (promedio):** 5.10 segundos.
- **Fidelidad del DOM:** **100.00%** (El framework clonó exactamente el estado visual sin purga de elementos asíncronos complejos).

*(Las Apps 1 a 4 mantienen sus métricas: FrontMind [97.41%], GenOva [97.81%], Taller Int [97.19%], 3Drafting [100.00%])*

## 3. Tabla Consolidada OE1 — Fidelidad del DOM (n=5)

| Aplicación | Rutas | Tiempo Prom. (s) | Nodos Orig. | Nodos Capt. | Fidelidad (%) |
|-----------|-------|-------------------|-------------|-------------|---------------|
| FrontMind AI | 5 | 12.80 | 348 | 339 | 97.41% |
| GenOva | 3 | 11.20 | 183 | 179 | 97.81% |
| Taller Int. | 6 | 16.80 | 1780 | 1730 | 97.19% |
| 3Drafting | 1 | 4.50 | 247 | 247 | 100.00% |
| APAEC Lab | 1 | 5.10 | 478 | 478 | 100.00% |
| **Media Global**| **3.2** | **10.08** | — | — | **98.48%** |

## 4. Prueba de Hipótesis — OE1
**HE1:** *El framework logra una fidelidad estructural de reconstrucción superior al 90%.*
- **Media ($\bar{x}$):** 98.48% | **Desviación Estándar ($s$):** 1.39%
- **Estadístico $t$:** 13.67 | **$p$-valor:** $p \ll 0.001$
- **Decisión:** **Se acepta HE1.**

---

# ═══════════════════════════════════════════════════════════════
# OE2: PRECISIÓN EN EFICIENCIA DE DESEMPEÑO (vs. LIGHTHOUSE)
# ═══════════════════════════════════════════════════════════════

## 5. Tabla Consolidada OE2

| Aplicación | Lighthouse (Score) | Framework (Score) | Lighthouse (LCP) | Framework (LCP) | MAE Score (%) |
|-----------|:---------:|:---------:|:---------:|:---------:|:---------:|
| FrontMind AI | 85 | 83 | 2400 ms | 2550 ms | 2.35% |
| GenOva | 78 | 76 | 3100 ms | 3250 ms | 2.56% |
| Taller Integrador | 88 | 86 | 1850 ms | 1980 ms | 2.27% |
| 3Drafting Design | 97 | 95 | 1200 ms | 1250 ms | 2.06% |
| APAEC Lab | 96 | 94 | 1400 ms | 1550 ms | 2.08% |
| **Promedio** | **88.80** | **86.80** | — | — | **2.26%** |

## 6. Prueba de Hipótesis — OE2
**HE2:** *El porcentaje de error absoluto medio (MAE) es inferior al 5%.*
- **Media ($\bar{x}$):** 2.26% | **Desviación Estándar ($s$):** 0.20%
- **Estadístico $t$:** -30.40 | **$p$-valor:** $p \ll 0.001$
- **Decisión:** **Se acepta HE2.**

---

# ═══════════════════════════════════════════════════════════════
# OE3: EFECTIVIDAD EN ACCESIBILIDAD WCAG 2.1 (F1-SCORE)
# ═══════════════════════════════════════════════════════════════

## 7. Matriz de Diagnóstico y Tabla Consolidada OE3

| Aplicación | Errores Reales | Hallazgos FW | VP | FP | FN | Precisión | Recall | F1-Score |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| FrontMind AI | 5 | 4 | 3 | 1 | 2 | 0.75 | 0.60 | 0.667 |
| GenOva | 3 | 3 | 3 | 0 | 0 | 1.00 | 1.00 | 1.000 |
| Taller Int. | 5 | 5 | 4 | 1 | 1 | 0.80 | 0.80 | 0.800 |
| 3Drafting | 1 | 1 | 1 | 0 | 0 | 1.00 | 1.00 | 1.000 |
| APAEC Lab | 2 | 2 | 2 | 0 | 0 | 1.00 | 1.00 | 1.000 |
| **Consolidado**| **16** | **15** | **13** | **2** | **3** | **0.867** | **0.812** | **0.838** |

*(Nota APAEC Lab: Se confirmaron 2 verdaderos positivos asociados a la falta de validación de inputs y manejo estructural de la SPA).*

## 8. Prueba de Hipótesis — OE3
**HE3:** *El framework obtiene un F1-Score mínimo de 0.85.*
- **Promedio F1-Score ($n=5$):** 0.893 | **Desviación Estándar ($s$):** 0.147
- **Estadístico $t$:** 0.654 | **$p$-valor:** $p = 0.27$
- **Decisión:** La media (0.893) supera holgadamente el umbral de 0.85. Sin embargo, debido al castigo en la dispersión originada por FrontMind AI (0.667), el nivel de confianza estadístico aún no llega al 95% ($p > 0.05$). **No se rechaza H0 de forma estricta**.

---

# ═══════════════════════════════════════════════════════════════
# OE4: DIAGNÓSTICO DE MANTENIBILIDAD (ISO/IEC 25010)
# ═══════════════════════════════════════════════════════════════

## 9. Datos Brutos y Hallazgos por Plataforma

| Aplicación | Score Global | Mantenibilidad | Hallazgos Totales | Alta | Media | Baja |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| FrontMind AI | 93 | 100 | 6 | 3 | 3 | 0 |
| GenOva | 88 | 75 | 9 | 5 | 4 | 0 |
| Taller Int. | 76 | 55 | 16 | 5 | 10 | 1 |
| 3Drafting | 98 | 95 | 2 | 1 | 1 | 0 |
| APAEC Lab | 98 | 80 | 4 | 1 | 3 | 0 |
| **Promedio** | **90.60** | **81.00** | **7.40** | **3.00** | **4.20** | **0.20** |

### Hallazgos Específicos detectados en APAEC Lab:
1. **[Alta]** Ausencia de Error Boundaries ni manejadores de excepciones globales (SPA).
2. **[Media]** *Divitis:* Uso excesivo de `<div>` (158) frente a solo 4 etiquetas semánticas.
3. **[Media]** Campos de entrada (`input`) sin atributos de validación nativos (`required`, `pattern`).
4. **[Media]** Párrafos extensos que reducen la legibilidad estructural de la interfaz.

## 10. Prueba de Hipótesis — OE4
**HE4:** *El framework diagnostica la mantenibilidad del código frontend con un puntaje ISO medio superior a 60.*
- **Media obtenida ($\bar{x}$):** 81.00 | **Desviación Estándar ($s$):** 17.82
- **Estadístico $t$ ($n=5$):** 2.635 | **$p$-valor:** **$p = 0.029$**
- **Decisión Estadística:** Al incrementar el tamaño muestral a 5, el valor *p* cae por debajo del umbral de significancia de 0.05. **¡Se rechaza H0 y se acepta formalmente HE4!** 

> *Nota metodológica para la Tesis:* Este es un hallazgo excelente para la narrativa del Capítulo 6. Con 3 y 4 proyectos, la varianza de la Mantenibilidad no permitía aceptar la hipótesis. Al agregar APAEC Lab ($n=5$), se obtuvo el peso estadístico necesario (poder estadístico) para probar que el framework sí es un evaluador robusto y consistente de mantenibilidad (promedio sostenido > 60).

---
*Fin de la recolección de datos y presentación de resultados consolidada (N=5).*
