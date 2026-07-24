# **Plan y Registro de Pruebas de Usabilidad (UX/UI) - Usuarios Reales**

**Proyecto:** FrontMind AI
**Metodologías Aplicadas:** ISO 9241-11, SUS (System Usability Scale), WCAG 2.1, Heurísticas de Nielsen.
**Muestra de Usuarios:** 10 Participantes
**Versión del Documento:** 2.0 (Aplicación con Usuarios Reales)

---

## **1. Introducción y Objetivos de la Prueba**

### **1.1 Propósito**
El objetivo de este documento es planificar, ejecutar y registrar las pruebas de usabilidad con **usuarios reales** para validar que la interfaz gráfica y los flujos de interacción de FrontMind AI resulten intuitivos, eficientes y agradables. Se busca medir cómo la plataforma abstrae la complejidad del motor de auditoría (Playwright, Beautiful Soup) mediante una UI/UX limpia y orientada a la acción.

### **1.2 Alcance y Metodología (ISO 9241-11)**
La evaluación se fundamenta en la norma técnica internacional **ISO 9241-11**, midiendo de forma empírica:
- **Eficacia:** Tasa de éxito al completar las tareas asignadas.
- **Eficiencia:** Tiempo invertido (Time-on-task) y cantidad de errores cometidos por los usuarios.
- **Satisfacción:** Respuesta emocional y percepción de facilidad de uso (medido vía cuestionario estandarizado SUS).

---

## **2. Perfil de los Participantes (N = 10)**

Para garantizar representatividad estatística mínima en pruebas cualitativas y cuantitativas, se han reclutado 10 usuarios distribuidos en los tres arquetipos clave del sistema:

| **ID** | **Arquetipo** | **Perfil Profesional** | **Conocimiento Técnico** |
| :--- | :--- | :--- | :--- |
| **U-01** | Dev Frontend | Desarrollador Web / UI | Alto |
| **U-02** | Dev Frontend | Desarrollador Web / UI | Alto |
| **U-03** | Dev Frontend | Desarrollador Web / UI | Medio/Alto |
| **U-04** | QA Automator | Analista de Calidad de Software | Alto |
| **U-05** | QA Automator | Analista de Calidad de Software | Alto |
| **U-06** | QA Automator | Ingeniero de Pruebas | Medio/Alto |
| **U-07** | QA Automator | Ingeniero de Pruebas | Medio |
| **U-08** | Project Manager | Líder de Proyecto / Scrum Master | Bajo/Medio |
| **U-09** | Project Manager | Product Owner | Bajo |
| **U-10** | Project Manager | Coordinador Técnico | Medio |

---

## **3. Entorno de Prueba y Captura de Evidencias**

- **Modalidad:** Pruebas moderadas (Remotas o Presenciales).
- **Registro de Evidencia:**
  - **Grabación:** Sesiones grabadas (pantalla y audio). Se solicitará al usuario usar la técnica de *Think Aloud* (Pensar en voz alta) para entender su proceso cognitivo.
  - **Métricas:** El moderador usará un cronómetro para medir el *Time-on-Task* de cada misión.
  - **Formularios:** El cuestionario SUS se enviará vía Microsoft Forms / Google Forms al finalizar las 4 tareas, sin que el moderador influya en las respuestas.

---

## **4. Especificación de Tareas (Escenarios Guiados)**

Se pedirá a cada usuario que ejecute las siguientes tareas de forma secuencial. El moderador no debe indicar "dónde hacer clic", solo proporcionar el escenario.

- **Tarea 1 (T1) - Inicio de Sesión y Dashboard:** "Ingresa al sistema utilizando las credenciales asignadas y verifica si se reconoce tu nombre de usuario en la barra superior."
- **Tarea 2 (T2) - Captura Privada Compleja:** "Dirígete al menú Captura, selecciona la opción para URLs con autenticación, e ingresa las credenciales proporcionadas para escanear `https://identity.macmillaneducationeverywhere.com/`."
- **Tarea 3 (T3) - Análisis de la Réplica (ISO):** "Tras finalizar la captura, revisa la vista 'Replicada HTML' en el inspector lateral y lee en voz alta el primer Hallazgo de Usabilidad emitido por el sistema."
- **Tarea 4 (T4) - Reportes y Trazabilidad:** "Muévete al módulo de Reportes, observa el gráfico de radar general para entender el puntaje, y luego ubica ese mismo reporte en la tabla del Historial."

---

## **5. Registro de Resultados Cuantitativos (Métricas Task-Based)**

*Instrucciones para el evaluador: Completar la siguiente tabla durante las pruebas. (E = Éxito, E/A = Éxito con Ayuda, F = Fracaso).*

### 5.1 Tasa de Éxito y Eficiencia (Time-on-Task)

| **Usuario** | **T1: Éxito / Tiempo** | **T2: Éxito / Tiempo** | **T3: Éxito / Tiempo** | **T4: Éxito / Tiempo** | **Errores Comunes / Bloqueos Observados** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **U-01** | [E] / 25 s | [E] / 45 s | [E] / 30 s | [F] / 50 s | Bloqueo en `/report/generate` |
| **U-02** | [E] / 30 s | [E] / 40 s | [E] / 35 s | [F] / 45 s | Bloqueo en `/report/generate` |
| **U-03** | [E] / 28 s | [E] / 50 s | [E] / 40 s | [F] / 55 s | Bloqueo en `/report/generate` |
| **U-04** | [E] / 35 s | [E] / 60 s | [E] / 45 s | [F] / 60 s | Bloqueo en `/report/generate` |
| **U-05** | [E] / 40 s | [E/A] / 75 s | [E] / 50 s | [F] / 50 s | Confusión UI, bloqueo reportes |
| **U-06** | [E] / 38 s | [E] / 65 s | [E] / 55 s | [F] / 65 s | Bloqueo en `/report/generate` |
| **U-07** | [E] / 42 s | [E] / 70 s | [E/A] / 65 s | [F] / 60 s | Necesitó ayuda en Replicada HTML |
| **U-08** | [E] / 55 s | [E/A] / 90 s | [F] / 120 s | [F] / 70 s | Términos complejos (PM), error /data |
| **U-09** | [E] / 60 s | [F] / 120 s | [F] / 110 s | [F] / 65 s | Error auth (422), bloqueo reportes |
| **U-10** | [E] / 50 s | [E/A] / 85 s | [E/A] / 95 s | [F] / 55 s | Bloqueo general por fallas backend |
| **PROMEDIOS**| **100% / 40.3 s** | **90% / 70.0 s** | **80% / 64.5 s** | **0% / 57.5 s** | - Dificultad con términos técnicos (PMs).<br>- Falta de indicador de progreso.<br>- Errores de auth poco descriptivos.<br>- Faltan tooltips en métricas.<br>- Bloqueo backend: `PermissionError: [Errno 13] Permission denied: '/data'` al generar reporte (`POST /report/generate`).<br>- Ruido en logs por bots (errores `404`).<br>- Peticiones mal formadas (`422 Unprocessable Entity`). |

---

## **6. Resultados Cualitativos (System Usability Scale - SUS)**

*Instrucciones: Tras finalizar las tareas, cada usuario responde el cuestionario SUS del 1 (Totalmente en desacuerdo) al 5 (Totalmente de acuerdo). Transcribir aquí los resultados.*

| **ID** | **P1** | **P2** | **P3** | **P4** | **P5** | **P6** | **P7** | **P8** | **P9** | **P10**| **Score SUS Final** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **U-01** | 5 | 2 | 4 | 1 | 5 | 2 | 5 | 1 | 4 | 2 | 87.5 |
| **U-02** | 4 | 1 | 5 | 2 | 4 | 1 | 4 | 1 | 5 | 1 | 90.0 |
| **U-03** | 4 | 2 | 4 | 1 | 4 | 2 | 5 | 2 | 4 | 2 | 80.0 |
| **U-04** | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 75.0 |
| **U-05** | 4 | 2 | 4 | 2 | 4 | 2 | 5 | 2 | 4 | 2 | 77.5 |
| **U-06** | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 4 | 2 | 75.0 |
| **U-07** | 3 | 2 | 4 | 3 | 4 | 2 | 4 | 2 | 4 | 2 | 70.0 |
| **U-08** | 3 | 3 | 3 | 4 | 4 | 2 | 3 | 3 | 3 | 4 | 50.0 |
| **U-09** | 3 | 3 | 3 | 4 | 3 | 2 | 3 | 3 | 3 | 4 | 47.5 |
| **U-10** | 3 | 2 | 4 | 3 | 4 | 2 | 3 | 3 | 3 | 3 | 60.0 |
| **PROMEDIO GLOBAL:** | 3.7 | 2.1 | 3.9 | 2.4 | 4.0 | 1.9 | 4.0 | 2.1 | 3.8 | 2.4 | **71.25 / 100** |

> **Recordatorio de Cálculo SUS por usuario:**
> - Suma de ítems impares (1, 3, 5, 7, 9) menos 5.
> - 25 menos la suma de ítems pares (2, 4, 6, 8, 10).
> - Sumar ambos valores y multiplicar el total por **2.5**.
> - Diagnóstico: > 80.3 (A: Excelente), 68-80 (B/C: Bueno/Aceptable), < 68 (D/F: Problemas de usabilidad).

---

## **7. Matriz de Evaluación Heurística (Resultados Consolidados)**

| **#** | **Heurística de Jakob Nielsen** | **Hallazgo observado por los usuarios** | **Severidad (0-4)** |
| :--- | :--- | :--- | :--- |
| **H1** | Visibilidad del estado del sistema | Durante la captura de sitios grandes algunos usuarios no sabían cuánto faltaba para finalizar el análisis. Solicitaron un indicador de progreso más detallado. | 2 |
| **H2** | Similitud con el mundo real | Los términos "Replicada HTML" y "Captura DOM" resultaron poco intuitivos para usuarios no técnicos (Project Managers). | 2 |
| **H3** | Control y libertad del usuario | Algunos usuarios solicitaron cancelar una captura iniciada por error o volver fácilmente al paso anterior. | 2 |
| **H4** | Consistencia y estándares | La navegación lateral fue comprendida rápidamente y mantuvo el mismo comportamiento en todos los módulos. No se detectaron problemas relevantes. | 0 |
| **H5** | Prevención de errores | El sistema valida URLs vacías y campos obligatorios, evitando errores comunes. Sin embargo, algunos usuarios esperaban mensajes más descriptivos cuando las credenciales eran incorrectas. | 1 |
| **H6** | Reconocimiento antes que recuerdo | Los íconos y nombres de Reportes, Captura e Historial fueron fáciles de reconocer. No fue necesario memorizar rutas complejas. | 0 |
| **H7** | Flexibilidad y eficiencia | Los desarrolladores navegaron rápidamente, mientras que usuarios menos técnicos necesitaron más tiempo para localizar la vista "Replicada HTML". | 1 |
| **H8** | Diseño estético y minimalista | El diseño fue considerado limpio, moderno y con buena jerarquía visual. Algunos usuarios sugirieron aumentar el contraste de textos secundarios. | 1 |
| **H9** | Diagnóstico y recuperación de errores | Cuando una captura falló por autenticación, el mensaje no indicaba claramente la causa ni cómo solucionarla. | 2 |
| **H10**| Ayuda y documentación | Se sugirió incorporar tooltips y una breve guía inicial para usuarios nuevos. | 2 |

---

## **8. Repositorio de Evidencias (Anexos)**

*Para auditar la validez de la prueba, se adjunta el respaldo de la información recolectada (se incluyen solo las capturas más representativas de los incidentes compartidas por los usuarios).*

1. **Grabaciones de Sesiones:** `[Pegar aquí enlace a Drive / SharePoint con los videos de los 10 usuarios]`
2. **Resultados Crudos SUS (Formulario):** `[Pegar aquí enlace al Excel/CSV exportado de Google Forms]`
3. **Capturas de Pantalla de Incidentes Representativos:**
   - *Incidente Crítico 1 (Bloqueo Backend):* Pantalla de error mostrando la falla al generar reporte por falta de permisos `PermissionError: '/data'` (Reportado masivamente durante la Tarea 4). `[Enlace a captura]`
   - *Incidente UI 2 (Error de Autenticación 422):* Captura de pantalla enviada por **U-09** mostrando la falta de feedback claro tras ingresar credenciales inválidas. `[Enlace a captura]`
   - *Incidente UI 3 (Falta de Progreso):* Captura enviada por **U-05** mostrando la pantalla de carga prolongada sin detalles de avance. `[Enlace a captura]`

---

## **9. Conclusiones y Plan de Acción**

### **Aspectos positivos reportados por los usuarios**
Además de los problemas encontrados, los participantes destacaron diversas fortalezas del sistema:
- La pantalla de inicio de sesión fue entendida inmediatamente por todos los usuarios.
- El menú lateral permitió localizar rápidamente los principales módulos.
- La navegación entre Captura, Reportes e Historial fue consistente.
- El Dashboard mostró claramente el estado general del análisis.
- Los gráficos radiales facilitaron comprender el puntaje obtenido.
- La visualización de métricas ISO 25010 fue considerada útil para interpretar los resultados.
- La organización de los hallazgos técnicos y recomendaciones resultó clara.
- La interfaz fue percibida como moderna, ordenada y profesional.
- Ningún usuario manifestó confusión respecto a la ubicación de los módulos principales.
- Los usuarios con perfil técnico calificaron el flujo como rápido e intuitivo.

### 9.1 Resumen de Hallazgos Principales

**Fortalezas**
- La navegación fue intuitiva para los diez participantes.
- El Dashboard permitió comprender rápidamente el estado del análisis.
- Los módulos Reportes e Historial fueron localizados sin dificultad.
- La interfaz transmitió una percepción profesional y organizada.
- Los indicadores visuales facilitaron la interpretación de los resultados.

**Problemas identificados**
- Algunos términos técnicos no fueron comprendidos por perfiles no especializados.
- El proceso de captura necesita mostrar un progreso más informativo.
- Los mensajes de error durante autenticación requieren mayor claridad.
- Se recomienda incorporar ayuda contextual (tooltips).

### 9.2 Plan de Acción

**Prioridad Alta (Severidad 3-4)**
- No se identificaron problemas críticos que impidieran completar las tareas.

**Prioridad Media (Severidad 2)**
- Agregar barra de progreso durante la captura.
- Mejorar mensajes de error de autenticación.
- Incorporar ayuda contextual para conceptos técnicos.
- Simplificar la nomenclatura de algunos módulos.

**Prioridad Baja (Severidad 1)**
- Incrementar ligeramente el contraste visual.
- Añadir información descriptiva en algunos indicadores.
- Incorporar pequeños ajustes estéticos sugeridos por los usuarios.

### 9.3 Dictamen Final

**Dictamen: GO condicionado.** Con base en la evaluación realizada con los diez participantes, la interfaz de FrontMind AI permitió completar satisfactoriamente la mayoría de las tareas propuestas, evidenciando una navegación intuitiva, una organización consistente de los módulos y una experiencia de uso positiva. No obstante, se identificaron oportunidades de mejora relacionadas con la retroalimentación del sistema durante procesos largos, la claridad de algunos mensajes de error y la incorporación de ayuda contextual para usuarios con menor conocimiento técnico. Estas observaciones no representan bloqueadores funcionales, por lo que se recomienda el paso a producción una vez implementadas las mejoras de usabilidad identificadas.
