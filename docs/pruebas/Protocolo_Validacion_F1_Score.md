# Protocolo de Validación Computacional mediante F1-score

El protocolo de **validación computacional mediante $F1\text{-score}$** está diseñado para evaluar con rigor cuantitativo la exactitud y capacidad de detección del framework multiagente frente a una línea base de verdad experta.

A continuación se detalla paso a paso cómo se estructura, calcula y ejecuta este proceso de validación:

---

### **1. Construcción del Gold Standard (Línea Base de Verdad)**
Para medir la precisión de manera objetiva y sin sesgos, se utiliza una **muestra censal técnica de 5 aplicaciones web frontend**.
* **Evaluación Experta:** Dos evaluadores expertos en desarrollo web y auditoría UX/UI inspeccionan manualmente las 5 aplicaciones.
* **Matriz de Defectos Conocidos ($N_{\text{total}}$):** Se consolida un inventario real de fallas clasificadas según las subcaracterísticas de la norma ISO/IEC 25010 (ej. errores de contraste de color, ausencia de atributos `aria-label`, falta de validaciones de formulario o fallas de navegación por teclado).

---

### **2. Matriz de Confusión para la Clasificación de Hallazgos**
Cada detección u omisión realizada de forma autónoma por el framework multiagente sobre las aplicaciones de prueba se contrasta con el **Gold Standard** dentro de cuatro categorías:

* **Verdaderos Positivos ($TP$):** Defectos reales del Gold Standard que el framework **detectó correctamente**.
* **Falsos Positivos ($FP$):** Defectos reportados por el framework que **NO existen** en el Gold Standard (corresponden a alucinaciones o falsas alarmas).
* **Falsos Negativos ($FN$):** Defectos reales presentes en el Gold Standard que el framework **omitió o no logró detectar**.
* **Verdaderos Negativos ($TN$):** Componentes o reglas conformes que el framework **identificó correctamente como sin defectos**.

---

### **3. Formulación Matemática del $F1\text{-score}$**
El $F1\text{-score}$ es la media armónica entre la **Precisión ($P$)** y el **Recall/Sensibilidad ($R$)**, lo que evita que la métrica se sesgue por un alto número de aciertos triviales:

1. **Precisión ($P$):** Mide la exactitud del framework para evitar falsos positivos y alucinaciones.
   $$P = \frac{TP}{TP + FP}$$

2. **Recall / Sensibilidad ($R$):** Mide la cobertura del framework para no pasar por alto fallas reales.
   $$R = \frac{TP}{TP + FN}$$

3. **$F1\text{-score}$:** Balancea armónicamente la precisión y la exhaustividad en una escala de 0 a 1:
   $$F1\text{-score} = 2 \cdot \frac{P \cdot R}{P + R} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}$$

---

### **4. Criterio de Validación de la Hipótesis ($H_{1a}$)**
* **Umbral de Aprobación:** La hipótesis específica $H_{1a}$ se considera demostrada y validada si el artefacto alcanza un **$F1\text{-score} \ge 0.85$**.
* **Interpretación:** Un valor igual o superior a 0.85 garantiza que el framework no solo detecta la gran mayoría de fallas de interfaz (alto Recall), sino que lo hace con un margen mínimo de falsas alarmas o alucinaciones (alta Precisión).

---

### **5. Plan de Ejecución y Procesamiento de Datos**
1. **Corridas Experimentales:** Se ejecutan **3 corridas consecutivas automatizadas** del framework sobre cada una de las 5 aplicaciones (15 ejecuciones en total) para verificar la estabilidad e irretroactividad de los hallazgos.
2. **Procesamiento de Datos:** Los resultados se tabulan en matrices de datos mediante scripts en **Python (`pandas` y `scikit-learn`)**, calculando automáticamente los valores de $TP, FP, FN, TN$, el $F1\text{-score}$ resultante y la desviación estándar del rendimiento.
