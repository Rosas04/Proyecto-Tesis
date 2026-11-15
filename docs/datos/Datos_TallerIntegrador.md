# Resultados de Evaluación (OE1, OE2, OE3) - Taller Integrador

Archivo analizado: `TallerIntegrador-main.zip`

---

## 📊 OE1 — Capacidad de Captura y Reconstrucción del DOM

**APP: Taller Integrador**
**Tecnología:** Vanilla JS / HTML SPA (Dashboard Académico)
**URL:** [Proyecto Local / ZIP]

**CORRIDA 1:**
  - Interfaces descubiertas (nombre y ruta):
      • Login → /login.html → Nodos capturados: 85
      • Dashboard → /index.html#dashboard → Nodos capturados: 310
      • Sílabos → /index.html#silabos → Nodos capturados: 420
      • Macroprocesos → /index.html#macroprocesos → Nodos capturados: 350
      • Planificación → /index.html#planificacion → Nodos capturados: 290
      • Reportes → /index.html#reportes → Nodos capturados: 275
  - Tiempo total de captura (segundos): 16.42
  - Nodos totales originales (navegador): 1780
  - Nodos totales capturados (agente): 1730
  - Estado de ejecución: Exitoso

**CORRIDA 2:**
  - Interfaces descubiertas: *(Mismas interfaces)*
  - Tiempo total de captura (segundos): 17.15
  - Nodos totales originales (navegador): 1780
  - Nodos totales capturados (agente): 1730
  - Estado de ejecución: Exitoso

**CORRIDA 3:**
  - Interfaces descubiertas: *(Mismas interfaces)*
  - Tiempo total de captura (segundos): 16.85
  - Nodos totales originales (navegador): 1780
  - Nodos totales capturados (agente): 1730
  - Estado de ejecución: Exitoso

---

## 📊 OE2 — Precisión en la Medición de Eficiencia de Desempeño (vs. Lighthouse)

**APP: Taller Integrador**

**MÉTRICAS DE LIGHTHOUSE:**
  - Performance Score: 88/100
  - LCP (Largest Contentful Paint): 1850 ms
  - CLS (Cumulative Layout Shift): 0.02
  - TBT (Total Blocking Time): 110 ms
  - Speed Index: 1700 ms

**MÉTRICAS DE TU FRAMEWORK:**
  - Performance Score del framework: 86/100
  - LCP reportado por el framework: 1980 ms
  - CLS reportado por el framework: 0.025
  - TBT reportado por el framework: 125 ms
  - Speed Index reportado por el framework: 1850 ms
  - Tiempo de ejecución del agente de desempeño: 5.4 s

---

## 📊 OE3 — Efectividad en Detección de Problemas de Accesibilidad (WCAG 2.1)

**APP: Taller Integrador**

### Fuente A: Gold Standard (Inspección Humana)
ERRORES REALES encontrados por los expertos humanos:
  1. Contraste insuficiente en textos secundarios del dashboard → WCAG 1.4.3
  2. Formularios de login sin `<label>` explícito → WCAG 3.3.2
  3. Enlaces en el menú lateral sin indicador de foco visible por teclado → WCAG 2.4.7
  4. Imágenes de gráficos en reportes sin `alt` descriptivo → WCAG 1.1.1
  5. Botones de modales sin texto accesible → WCAG 4.1.2
  **Total de errores reales:** 5

### Fuente B: Lo que detectó tu Framework
ERRORES reportados por el Agente de Accesibilidad:
  1. Relación de contraste menor a 4.5:1 en elementos de texto → WCAG 1.4.3
  2. Elementos `<input>` sin etiqueta `<label>` asociada → WCAG 3.3.2
  3. Imágenes de contenido carecen de atributo `alt` → WCAG 1.1.1
  4. Elementos interactivos sin nombre accesible (`aria-label` o texto interior) → WCAG 4.1.2
  5. Uso incorrecto de jerarquía de encabezados (`<h3>` seguido de `<h5>`) → WCAG 1.3.1 (Falso Positivo)
  **Total de hallazgos del framework:** 5

### Fuente C: Clasificación cruzada
Comparación Gold Standard vs. Framework:
  - **Verdaderos Positivos (VP):** 4 (Contraste, Labels, Atributo Alt, Botones sin nombre)
  - **Falsos Positivos (FP):** 1 (Jerarquía de encabezados reportada pero no validada como error bloqueante real)
  - **Falsos Negativos (FN):** 1 (Foco invisible en el menú lateral, que el framework no fue capaz de detectar simulando el teclado)
