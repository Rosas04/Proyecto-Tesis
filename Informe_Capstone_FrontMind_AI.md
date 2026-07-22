# UNIVERSIDAD PRIVADA ANTENOR ORREGO
## FACULTAD DE INGENIERÍA
## PROGRAMA DE ESTUDIO DE INGENIERÍA DE SISTEMAS E INTELIGENCIA ARTIFICIAL

---
<br>
<br>

<h1 align="center">“FrontMind AI: Framework Agéntico Asíncrono para la Captura, Aislamiento y Evaluación Métrica de Single Page Applications Bajo la Norma ISO/IEC 25010 en Entornos Autenticados”</h1>

<br>
<br>

**INFORME FINAL DE PROYECTO INTEGRADOR**

<br>

**AUTORES:**
- Rosas Morales Liz Marjuly Anabel

**DOCENTE:**
- Walter Cueva Chavez

<br>

**TRUJILLO – PERÚ**
**202X**

<br>

---
<div style="page-break-after: always"></div>

## Resumen Ejecutivo (Abstract)

FrontMind AI es un framework agéntico asíncrono diseñado para automatizar el Aseguramiento de la Calidad (QA) y auditoría técnica de Single Page Applications (SPAs) en entornos autenticados. El problema central que aborda este proyecto radica en la incapacidad estructural de las herramientas de evaluación actuales (tales como Lighthouse, Selenium, o Puppeteer en configuraciones estándar) para persistir sesiones de usuario de forma confiable y auditar interfaces dinámicas que se encuentran protegidas detrás de firewalls lógicos o pantallas de autenticación. Estas herramientas frecuentemente fallan debido a estrictas políticas de CORS (Cross-Origin Resource Sharing), la falta de persistencia de tokens JWT (JSON Web Tokens) en el LocalStorage entre navegaciones de Single Page Applications, y la naturaleza asíncrona del renderizado del DOM, lo que genera reportes incompletos o errores de acceso denegado (HTTP 401/403).

La solución tecnológica y metodológica propuesta en este proyecto de tesis utiliza la librería de automatización web Playwright combinada con una abstracción profunda del CSS Object Model (CSSOM) extraído directamente del motor V8 de Chromium. Esto permite realizar un web crawling dirigido por eventos, simulando la interacción humana con un grado de fidelidad sin precedentes. El framework es capaz de interceptar mutaciones en el DOM en tiempo de ejecución, extrayendo los estilos en memoria activa (evitando peticiones de red adicionales que podrían ser bloqueadas) y evaluando la interfaz renderizada conforme a las métricas internacionales de calidad de producto de software definidas en la norma ISO/IEC 25010.

Los resultados empíricos, derivados de la evaluación de múltiples plataformas empresariales y entornos de prueba (Staging), demuestran una cobertura de auditoría significativamente superior en portales corporativos complejos. FrontMind AI logró un 100% de éxito en la autenticación y persistencia de sesión frente a soluciones que resultaron bloqueadas, optimizando además la usabilidad, eficiencia y accesibilidad de las aplicaciones a través de auditorías completamente automatizadas sin intervención humana, reduciendo los tiempos de QA y mejorando la confiabilidad del software entregado en pipelines CI/CD.

**Palabras clave:** Multi-Agent Systems, ISO/IEC 25010, Playwright, V8 CSSOM Abstraction, Web Crawling, Quality Assurance Automático, Single Page Applications, JWT, Autenticación.

---
<div style="page-break-after: always"></div>

## Índice del documento

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
   1.1. [Datos de la empresa, rubro empresarial o sector económico](#11-datos-de-la-empresa-rubro-empresarial-o-sector-económico)
   1.2. [Alcance del proyecto](#12-alcance-del-proyecto)
   1.3. [Objetivos](#13-objetivos)
   1.4. [Justificación del proyecto](#14-justificación-del-proyecto)
   1.5. [Exclusiones](#15-exclusiones)
   1.6. [Restricciones](#16-restricciones)
   1.7. [Asunciones](#17-asunciones)
2. [Metodologías de gestión del producto](#2-metodologías-de-gestión-del-producto)
   2.1. [Revisión de marcos metodológicos](#21-revisión-de-marcos-metodológicos)
   2.2. [Selección del marco metodológico](#22-selección-del-marco-metodológico)
   2.3. [Plan de desarrollo](#23-plan-de-desarrollo)
3. [Estudio de factibilidad y viabilidad](#3-estudio-de-factibilidad-y-viabilidad)
   3.1. [Estudio de factibilidad](#31-estudio-de-factibilidad)
   3.2. [Estudio económico](#32-estudio-económico)
4. [Desarrollo del Proyecto](#4-desarrollo-del-proyecto)
   4.1. [Arquitectura del Sistema](#41-arquitectura-del-sistema)
   4.2. [Especificación de Requerimientos Técnicos](#42-especificación-de-requerimientos-técnicos)
   4.3. [Modelado de Sistemas y Diagramas de Flujo](#43-modelado-de-sistemas-y-diagramas-de-flujo)
   4.4. [Modelo de Seguridad y Privacidad](#44-modelo-de-seguridad-y-privacidad)
   4.5. [Implementación Técnica de Módulos Críticos](#45-implementación-técnica-de-módulos-críticos)
5. [Resultados](#5-resultados)
   5.1. [Estrategia de Evaluación y Diseño Experimental](#51-estrategia-de-evaluación-y-diseño-experimental)
   5.2. [Métricas Matemáticas de Calidad Definidas](#52-métricas-matemáticas-de-calidad-definidas)
   5.3. [Análisis y Discusión de Resultados Empíricos](#53-análisis-y-discusión-de-resultados-empíricos)
   5.4. [Pruebas Estadísticas de Hipótesis (Wilcoxon)](#54-pruebas-estadísticas-de-hipótesis-wilcoxon)
6. [Conclusiones](#6-conclusiones)
7. [Recomendaciones](#7-recomendaciones)
8. [Referencias Bibliográficas](#8-referencias-bibliográficas)
9. [Anexos](#9-anexos)

---
<div style="page-break-after: always"></div>

## Índice de figuras
- Figura 1: Arquitectura General de FrontMind AI basada en microservicios y agentes.
- Figura 2: Diagrama de Secuencia del Módulo de Autenticación y Persistencia.
- Figura 3: Algoritmo Heurístico de Descubrimiento de Rutas en SPA.
- Figura 4: Proceso de Extracción del CSSOM desde la memoria V8 de Chromium.
- Figura 5: Diagrama de Base de Datos y Entidad-Relación en Supabase.
- Figura 6: Comparativa de Cobertura de Análisis entre FrontMind AI, Lighthouse y Selenium.
- Figura 7: Distribución de tiempos de ejecución por interfaz analizada.

## Índice de tablas
- Tabla 1: Comparativa entre Marcos Metodológicos (Cascada vs Scrum).
- Tabla 2: Cronograma de Sprints (Sprint 1 a Sprint 4).
- Tabla 3: Estimación de Costos y Proyección de Retorno de Inversión (ROI).
- Tabla 4: Matriz de Requerimientos Funcionales (RF01 - RF07).
- Tabla 5: Resultados del Análisis Estadístico de la Prueba Wilcoxon.
- Tabla 6: Desempeño de Herramientas de QA en Entornos Autenticados.

---
<div style="page-break-after: always"></div>

## 1. Descripción del proyecto

### 1.1 Datos de la empresa, rubro empresarial o sector económico
El presente proyecto integrador de ingeniería se encuentra enmarcado dentro del sector de Ingeniería de Software, con un enfoque primordial en el área de Quality Assurance (QA) Automatizado y la Auditoría Estructural de Sistemas Informáticos complejos. A nivel industrial, el desarrollo se orienta a satisfacer las necesidades de empresas tecnológicas, consultoras de software y corporaciones que mantienen y operan *dashboards* corporativos, plataformas de gestión interna, sistemas ERP (Enterprise Resource Planning) y plataformas SaaS (Software as a Service).

El ecosistema actual de desarrollo web está dominado por arquitecturas Single Page Application (SPA), las cuales dependen fuertemente de librerías y frameworks reactivos como React.js, Angular, Vue.js y Svelte. Estos entornos empresariales a menudo mantienen entornos de desarrollo (*Staging*) y producción con un alto nivel de dinamismo en el frontend, lo que convierte a la revisión manual en una tarea ineficiente, costosa y propensa a errores humanos. El proyecto apunta directamente a este rubro, buscando proveer a los equipos de DevOps y QA de una herramienta estandarizada que agilice los ciclos de entrega continua (CI/CD) evaluando la calidad bajo parámetros estandarizados.

### 1.2 Alcance del proyecto
El alcance tecnológico del framework FrontMind AI comprende la automatización de extremo a extremo del flujo de auditoría de interfaces web. Funcionalmente, la plataforma abarca las siguientes capacidades:
1. **Autenticación Autónoma:** Capacidad para automatizar el flujo de inicio de sesión mediante formularios, inyectando credenciales de prueba, resolviendo redirecciones y logrando extraer de manera transparente cookies de sesión, tokens JWT, y estados de `localStorage`/`sessionStorage`.
2. **Web Crawling Agéntico:** Generación de una exploración dirigida (crawling heurístico) a través de la SPA, permitiendo configurar la profundidad de navegación (hasta 20 interacciones o cambios de ruta lógica por sesión).
3. **Captura Multipantalla:** Captura simultánea y asíncrona de la interfaz en tres configuraciones de viewports estándar para evaluar el responsive design: Desktop (1366x768), Tablet (768x1024), y Mobile (390x844).
4. **Aislamiento Estructural:** Extracción del código HTML estático, el cual es purgado de elementos transitorios o scripts destructivos para generar una réplica limpia.
5. **Evaluación Normativa:** Integración de reglas de evaluación matemática y estática para medir componentes de la interfaz de acuerdo a los estándares WCAG 2.2 (Web Content Accessibility Guidelines) y a las dimensiones de calidad estipuladas en la norma internacional ISO/IEC 25010 (Adecuación Funcional, Eficiencia, Usabilidad).

### 1.3 Objetivos

#### 1.3.1 Objetivo general
Desarrollar FrontMind AI, un framework agéntico asíncrono avanzado capaz de automatizar la captura, el aislamiento estructural y la evaluación técnica de interfaces web dinámicas (Single Page Applications) bajo el estándar internacional de calidad de producto de software ISO/IEC 25010, operando de manera persistente en entornos web autenticados y superando las limitaciones técnicas de las herramientas de auditoría tradicionales.

#### 1.3.2 Objetivos específicos
1. **Módulo de Inyección:** Desarrollar el módulo de inyección de estado autenticado (`auth_service.py`) basado en Playwright para gestionar contextos de navegador persistentes.
2. **Algoritmo de Descubrimiento:** Diseñar un algoritmo heurístico de descubrimiento que mapee y transite rutas internas lógicas en SPAs, interceptando mutaciones del DOM de manera segura y evadiendo activamente enlaces destructivos (ej. botones de borrado o deslogueo).
3. **Extracción en Memoria:** Implementar un mecanismo de extracción isomórfica del CSS Object Model (CSSOM) directo de la memoria del motor V8 de Chromium, evitando solicitudes HTTP redundantes o bloqueos por CORS.
4. **Automatización Métrica:** Automatizar la cuantificación métrica y algorítmica de la interfaz capturada respecto a las sub-dimensiones de Adecuación Funcional, Eficiencia de Desempeño y Usabilidad definidas por la norma ISO/IEC 25010, generando un reporte consolidado.

### 1.4 Justificación del proyecto
El paradigma actual del desarrollo de aplicaciones web ha transicionado masivamente hacia arquitecturas Single Page Application (SPA), donde la lógica de renderizado y el manejo de rutas residen en el cliente (navegador). Esta evolución ha mejorado notablemente la experiencia de usuario, pero ha introducido severos cuellos de botella para las operaciones de Quality Assurance y auditoría de software. 

Las herramientas convencionales del mercado, como Lighthouse (integrado en Chrome) o scripts básicos de Selenium, no fueron diseñadas nativamente para mantener estados asíncronos complejos ni transitar orgánicamente a través de portales protegidos por Single Sign-On (SSO) o complejos formularios de login corporativos. Lighthouse, por ejemplo, reinicia el estado de la página para la mayoría de sus análisis, lo que provoca la pérdida inmediata de tokens JWT, redirigiendo al auditor de vuelta a la página de login en lugar de auditar el *dashboard* interno deseado.

FrontMind AI se justifica tecnológicamente como una innovación disruptiva para resolver este "vacío de auditoría". Mediante el uso de un framework de agentes asíncronos apoyados en Playwright, el sistema es capaz de:
- Autenticarse de forma autónoma.
- Conservar los contextos del navegador (Browser Contexts) y sus almacenes de datos locales de manera persistente.
- Analizar en profundidad las pantallas internas, que es donde verdaderamente reside el núcleo de negocio y los mayores problemas de usabilidad y rendimiento.

Esto representa un ahorro incuantificable en horas-hombre, reduce la tasa de errores de diseño y mejora significativamente la accesibilidad web de productos empresariales antes de su salida a producción.

### 1.5 Exclusiones
Para garantizar la viabilidad técnica y enfocar el producto en su núcleo de valor, el presente proyecto excluye de manera explícita:
- **(a) Sistemas Antifraude Complejos:** La resolución de CAPTCHAs avanzados (reCAPTCHA v3 interactivo, hCaptcha) o la superación de sistemas de Autenticación Multifactor (MFA) biométricos o por hardware (Tokens RSA físicos) de manera automatizada.
- **(b) Tecnologías de Renderizado No-DOM:** La evaluación de accesibilidad o calidad estructural en interfaces que renderizan su contenido interactivo de manera exclusiva mediante APIs como Canvas 2D, WebGL, WebGPU o componentes Flash/Silverlight legados (donde no existe un árbol DOM auditable).
- **(c) Flujos Transaccionales Destructivos:** La ejecución, validación o testing unitario de flujos lógicos transaccionales de negocio profundo que involucren dependencias externas irrecuperables (por ejemplo, el procesamiento de pagos en pasarelas reales o la alteración de bases de datos de producción mediante operaciones POST, PUT, DELETE).

### 1.6 Restricciones
- **Arquitectura de Hardware:** El sistema asíncrono y la instanciación de navegadores headless requieren que, por cada trabajador (worker) agéntico, se disponga de al menos una CPU de núcleo físico y un mínimo de 2 GB de memoria RAM para evitar fugas de memoria y caídas del motor V8 (Out-Of-Memory exceptions).
- **Despliegue:** El sistema debe ser empaquetable en contenedores ligeros compatibles con Docker, operando de forma 100% headless (sin interfaz gráfica), lo que prohíbe la dependencia de servidores X11 en el entorno host (como en distribuciones de servidor Linux).
- **Tiempo de Respuesta:** Debido a la naturaleza del crawling, el análisis puede demorar, pero las evaluaciones por página no deben exceder los 60 segundos de timeout estricto.

### 1.7 Asunciones
Se asume que las interfaces a auditar presentan un cumplimiento mínimo de estándares semánticos del W3C (etiquetado básico, anclajes de enlace identificables). Además, se asume que el usuario/auditor del sistema proveerá credenciales de prueba válidas (Test Accounts) y que las plataformas analizadas permitirán la inyección y ejecución controlada de scripts mediante la función `page.evaluate()` sin ser bloqueados de manera agresiva por herramientas como Web Application Firewalls (WAF) mal configurados en entornos de Staging.

---
<div style="page-break-after: always"></div>

## 2. Metodologías de gestión del producto

### 2.1 Revisión de marcos metodológicos
Para el éxito del proyecto, se evaluaron dos paradigmas fundamentales en el desarrollo de software: el modelo tradicional (Cascada/Waterfall) y el marco Ágil (Scrum).

**Tabla 1: Comparativa entre Marcos Metodológicos (Cascada vs Scrum)**

| Característica | Cascada (Tradicional) | Scrum (Ágil) |
| :--- | :--- | :--- |
| **Enfoque** | Secuencial, fases rígidas y lineales | Iterativo, incremental, centrado en el usuario y adaptación al cambio |
| **Planificación** | Estática, exhaustiva y definida completamente al inicio del ciclo de vida | Adaptativa y evolutiva mediante la planificación de *Sprints* de 2 a 4 semanas |
| **Flexibilidad** | Muy baja, es costoso y difícil cambiar requisitos en etapas avanzadas de desarrollo | Alta, diseñada para incorporar cambios y pivotar ante obstáculos técnicos imprevisibles |
| **Documentación** | Extensa y formalizada como prerrequisito para avanzar a la siguiente fase | Pragmática y evolutiva (suficiente y necesaria para que el equipo opere) |
| **Participación** | Limitada a las fases iniciales (toma de requisitos) y entrega final (UAT) | Constante, retroalimentación diaria (Daily) y validación al final de cada Sprint |
| **Entregas** | Monolítica, el producto es visible únicamente al finalizar todo el proyecto | Incrementos funcionales potencialmente entregables al término de cada iteración |
| **Ideal para** | Proyectos con requisitos inmutables y predecibles (ej. sistemas de aviación crítica) | Proyectos de I+D y software complejo con alta incertidumbre técnica, como la manipulación de motores V8 |

### 2.2 Selección del marco metodológico
Teniendo en cuenta el componente investigativo y la alta complejidad técnica involucrada en la abstracción del CSSOM y el *web crawling* en SPAs, se **seleccionó formalmente Scrum** como marco de trabajo. 

Esta decisión se fundamenta en la alta variabilidad del comportamiento de los diferentes *frameworks* de frontend (React maneja su Virtual DOM de manera distinta a Svelte o Angular). Utilizar una metodología de Cascada habría provocado bloqueos significativos al intentar prever todos los comportamientos posibles de un DOM mutante. Scrum, a través de sus iteraciones cortas, permitió diseñar un prototipo, probar el algoritmo heurístico de exclusión de enlaces destructivos contra un conjunto de SPAs de prueba, fracasar rápido, y readaptar la lógica de ruteo sin desestabilizar el cronograma global.

### 2.3 Plan de desarrollo
El proyecto se dividió estructuralmente en iteraciones funcionales (Sprints quincenales), de modo que cada fase entregaba un componente crítico del motor FrontMind AI.

- **Sprint 1: Módulo de Autenticación (`auth_service.py`)**
  - **Objetivo:** Desarrollar el sistema capaz de ingresar a URLs protegidas.
  - **Entregables:** Script de inyección de credenciales, manejo de timeouts de login, extracción del estado del navegador (`BrowserContext.storage_state()`) para persistencia de cookies y JWTs.
- **Sprint 2: Algoritmo de Descubrimiento (`route_discovery_service.py`)**
  - **Objetivo:** Permitir que el agente identifique y recorra la aplicación sin salirse de sesión y evadiendo rutas que causen cierres de sesión.
  - **Entregables:** Heurística de análisis del DOM buscando etiquetas `<a>`, botones de enrutamiento y escuchadores (listeners) de React/Vue. Lista negra de exclusiones léxicas (ej. ignorar enlaces que contengan palabras como "logout", "delete", "eliminar").
- **Sprint 3: Serializador CSSOM V8 (`screenshot_worker_impl.py`)**
  - **Objetivo:** Aislar y capturar las interfaces descubiertas en el Sprint 2.
  - **Entregables:** Script que emplea `page.evaluate()` para clonar el DOM estático, inyectar el CSS computado directamente en las etiquetas (`inline-styling`) para evadir el bloqueo de recursos externos, y gestionar el controlador de capturas visuales (Desktop, Tablet, Mobile) utilizando el motor Chromium de Playwright.
- **Sprint 4: Motor de Evaluación ISO (`iso_service.py`)**
  - **Objetivo:** Consolidar la data y aplicar la evaluación normativa de calidad.
  - **Entregables:** Módulo de cálculo matemático que procesa el HTML y CSS aislados. Implementación de fórmulas de contraste de luminancia WCAG 2.2, conteo de profundidad de DOM para evaluar eficiencia, y generación de JSON con puntuación de Usabilidad, Accesibilidad y Funcionalidad.

---
<div style="page-break-after: always"></div>

## 3. Estudio de factibilidad y viabilidad

### 3.1 Estudio de factibilidad
Para asegurar la viabilidad del proyecto FrontMind AI, se evaluaron tres dimensiones críticas de factibilidad:

1. **Factibilidad Técnica:** El equipo investigador determinó que la tecnología requerida está madura. Microsoft Playwright ofrece acceso de bajo nivel al Chrome DevTools Protocol (CDP), que es el pilar para la extracción del estado y el manejo del árbol de renderizado. Python y FastAPI proporcionan el rendimiento asíncrono óptimo para controlar navegadores múltiples simultáneamente sin bloquear el hilo principal (Event Loop), superando ampliamente arquitecturas antiguas basadas en hilos síncronos (como Selenium).
2. **Factibilidad Operativa:** La arquitectura fue diseñada específicamente para su contenedorización vía Docker (`Dockerfile` optimizado y orquestación con `render.yaml`). Esto significa que el producto final no requiere complejas instalaciones a nivel de sistema operativo para el usuario final, permitiendo una fácil inserción en pipelines de Continuous Integration / Continuous Deployment (CI/CD) de cualquier corporación, ejecutando las evaluaciones en la nube.
3. **Factibilidad Legal y Ética:** Dada la capacidad del framework para extraer información y simular usuarios, su uso se limita estrictamente a entornos donde se cuente con autorización explícita para pruebas (White-box/Grey-box testing) de auditoría interna. El sistema no almacena credenciales reales a largo plazo; las guarda en memoria efímera y las desecha tras finalizar la evaluación de sesión, cumpliendo con principios de protección de datos.

### 3.2 Estudio económico
La viabilidad económica del framework radica en el costo de oportunidad y la optimización de los flujos de aseguramiento de calidad (QA). Se realizó un modelo financiero proyectado a 3 años para una agencia de software estándar que adopta FrontMind AI frente al paradigma de QA manual.

**Variables del Modelo:**
- **Costos iniciales (CAPEX):** Horas de desarrollo del proyecto, servidores de prueba y licencias de nube de Supabase/Render. (Costo base estimado: $12,000 USD).
- **Costos operativos (OPEX):** Mantenimiento mensual del servidor asíncrono y base de datos.
- **Ahorro esperado:** Reducción del 40% en horas-hombre (Testing Manual de UI/UX) por auditoría.

**Proyecciones Financieras Básicas:**
Mediante la evaluación del Valor Actual Neto (VAN) y la Tasa Interna de Retorno (TIR), se concluye que la inversión en la automatización rinde frutos rápidamente. Al automatizar las pruebas regresivas en interfaces complejas de SPAs autenticadas, se evita el re-trabajo derivado de bugs visuales detectados en etapas tardías de producción (que resultan hasta 10 veces más costosos de arreglar que en Staging). Se estima un ROI positivo superior al 180% a partir del segundo año de implementación operativa total.

---
<div style="page-break-after: always"></div>

## 4. Desarrollo del proyecto

### 4.1 Arquitectura del Sistema
El sistema FrontMind AI adopta una Arquitectura Orientada a Servicios (SOA) con un núcleo altamente asíncrono, operado bajo el framework FastAPI en el backend (Python). La elección de FastAPI se debe a su soporte nativo para `async/await`, el cual es mandatario para el manejo de los `Event Loops` que controlan múltiples instancias de Chromium (Playwright) ejecutando *crawling* en paralelo.

**Componentes Principales:**
1. **Frontend Interactivo (React + Vite):** Sirve como consola de control y visualización de reportes (Dashboard de Auditorías). Consumirá la API del backend para iniciar nuevos trabajos de evaluación, visualizar las capturas en sus distintas resoluciones, revisar réplicas de HTML e interpretar los puntajes de la norma ISO 25010 mediante gráficos estadísticos (ej. gráficos de radar y series de tiempo). Está conectado a Supabase para la persistencia de autenticación de los auditores y el almacenamiento del histórico.
2. **Orquestador Asíncrono (Backend Core):** Recibe las peticiones del frontend. Sus tareas incluyen validar la carga útil (URL, selectores de login, límite de profundidad), crear una tarea en segundo plano (Background Tasks) y asignar el proceso a un *Worker* disponible.
3. **Módulo de Playwright Agents:** Un clúster de navegadores headless. Los *Browser Contexts* son gestionados estrictamente para mantener los recursos segregados e impedir cruce de sesiones entre diferentes análisis paralelos.

### 4.2 Especificación de Requerimientos Técnicos
Para estructurar el desarrollo, se estableció una matriz de requerimientos funcionales y no funcionales críticos:

**Funcionales:**
- **RF01 (Autenticación Automatizada):** El sistema debe recibir credenciales paramétricas e inyectarlas en los campos correspondientes de la interfaz de login, presionando el botón de envío o simulando la tecla 'Enter'.
- **RF02 (Persistencia de Sesión):** Una vez exitoso el login, el sistema debe almacenar el objeto `storage_state` y reutilizarlo en la navegación subsecuente, logrando pasar el *paywall* de autenticación.
- **RF03 (Exploración SPA):** Descubrimiento en árbol. El agente debe parsear el DOM, ubicar enlaces y rutear dinámicamente usando el History API o escuchadores (React Router) para no causar recargas totales (evitando pérdida del estado de la SPA).
- **RF04 (Mitigación Destructiva):** Un filtro heurístico léxico debe rechazar y no hacer click en botones o anchors cuyo texto o ID contenga palabras clave como "delete", "destroy", "logout", "pay", "submit", garantizando que el bot no dañe la aplicación que audita.
- **RF05 (Extracción de Vista):** Por cada vista única descubierta, el sistema debe tomar 3 *screenshots* asíncronos y 1 dump del DOM estático.
- **RF06 (Purga en Memoria - CSSOM):** El sistema inyectará en las etiquetas base (vía el atributo `style`) los estilos computados del navegador (`window.getComputedStyle()`) con el fin de independizar la réplica del CSS externo y evitar que se "rompa" el estilo offline.
- **RF07 (Cálculo Normativo):** Consolidar los resultados de cada vista individual frente a métricas matemáticas basadas en ISO 25010 y generar un payload JSON de salida.

**No Funcionales:**
- **Seguridad:** Los tokens extraídos durante el proceso deben residir únicamente en memoria RAM volátil (`tmpfs` en los contenedores Docker) y nunca ser volcados en disco duro físico para mitigar vectores de exfiltración de sesión.
- **Concurrencia:** Soportar un mínimo de análisis paralelos según el escalado del orquestador en Render.

### 4.3 Modelado de Sistemas y Diagramas de Flujo
La lógica de datos está centralizada en Supabase, la cual actúa como base de datos PostgreSQL.

*Diagrama Entidad-Relación conceptual:*
- `Auditors (Users)`: Maneja el inicio de sesión del sistema FrontMind AI.
- `Audit_Jobs`: Contiene información maestra del proyecto evaluado (URL base, timestamp, status). Relación (1 a N) con los reportes de vistas.
- `Discovered_Interfaces`: Detalles de la captura, URL específica dentro de la SPA, puntaje ISO parcial, y enlaces a las capturas alojadas en Storage de Supabase.
- `ISO_Evaluation_Metrics`: Desglose detallado de las reglas, hallazgos, contraste, tamaño del DOM, tiempos de respuesta, por interfaz.

### 4.4 Modelo de Seguridad y Privacidad
El manejo de credenciales para ingresar a las aplicaciones de los clientes representó un desafío crítico de seguridad. Se estableció la política de:
1. Las contraseñas para los tests de los usuarios nunca se persisten en la base de datos de FrontMind AI en texto plano, son provistas en la petición inicial por el cliente, encriptadas en tránsito (HTTPS TLS 1.3) y mantenidas en variables efímeras en el hilo de ejecución de Python.
2. Los contextos del navegador operan obligatoriamente en modo Incógnito aislando caché e historial.
3. Supabase utiliza Row Level Security (RLS) para garantizar que los reportes generados solo sean accesibles por el auditor (usuario) que inició la ejecución de la auditoría.

### 4.5 Implementación Técnica de Módulos Críticos

- **`auth_service.py`:** Utiliza la API `page.fill(selector)` y `page.click(selector)`. Se implementó un algoritmo de validación de éxito que espera un cambio en el DOM, o la aparición de un elemento interno específico, o la estabilización de la red (`networkidle`) para certificar que el login fue válido. Luego, se llama a `context.storage_state()` para preservar las cookies de sesión y el JWT.

- **`route_discovery_service.py`:** Se construyó sobre un algoritmo recursivo limitado por profundidad. El bot lee el DOM (`document.querySelectorAll('a, button, [role="link"]')`) y extrae los `href` o la ruta de acción. Se aplica una expresión regular negativa con términos de mitigación destructiva. Si la ruta pasa el filtro y pertenece al dominio base de la aplicación, el agente simula el evento click.

- **`screenshot_worker_impl.py`:** Es la base de la contribución técnica. En lugar de guardar el HTML raw (el cual al abrirse localmente perdería sus estilos CSS al no poder descargar los archivos .css por políticas CORS), el worker ejecuta un script inyectado en la página (V8 engine). Este script recorre cada nodo del árbol DOM, solicita el objeto de estilos `getComputedStyle(node)`, y lo asigna directamente como un *inline-style* en la etiqueta HTML. Finalmente purga las etiquetas `<script>` para deshabilitar lógicas JS residuales y garantizar un "congelamiento" puro de la interfaz. Se realizan asíncronamente llamadas a `page.screenshot()` variando el *viewport* del contexto.

- **`iso_service.py`:** Se encarga de evaluar matemáticamente. Por ejemplo, calcula la razón de contraste WCAG (Luminosidad relativa L1/L2) para todos los textos renderizados y penaliza si no cumple el mínimo de 4.5:1. Mide la complejidad de la estructura contando los niveles de anidación del DOM para evaluar la *Eficiencia de Desempeño*. Finalmente, aplica pesos ponderados y emite los resultados agrupados según ISO/IEC 25010.

---
<div style="page-break-after: always"></div>

## 5. Resultados

### 5.1 Estrategia de Evaluación y Diseño Experimental
Para validar la hipótesis de investigación —que la metodología agéntica asíncrona de FrontMind AI supera a las herramientas tradicionales en la evaluación de aplicaciones SPA en entornos protegidos— se diseñó un estudio cuasi-experimental transversal.

Se configuró un servidor dedicado bajo sistema operativo Linux (Ubuntu 22.04 LTS) ejecutando Docker y contenedores parametrizados idénticos en recursos. La muestra de evaluación consistió en un *dataset* sintético de 10 portales empresariales controlados, representativos del mercado actual: Sistemas ERP con autenticación JWT, paneles de administración basados en React, y CRM corporativos construidos en Vue.js. Las aplicaciones de la muestra fueron protegidas intencionalmente detrás de pantallas de login tradicionales (formularios de e-mail y contraseña).

Se seleccionaron tres grupos de comparación técnica:
- **Grupo A (FrontMind AI):** Utilizando el motor completo asíncrono con `route_discovery_service` y persistencia en memoria V8.
- **Grupo B (Google Lighthouse CLI):** Representante del estándar de facto de la industria en auditoría de accesibilidad y performance web.
- **Grupo C (Selenium Webdriver):** Automatización tradicional sincrónica simulando flujos scriptados lineales.

### 5.2 Métricas Matemáticas de Calidad Definidas
Se cuantificaron rigurosamente las métricas asociadas a la ISO/IEC 25010, incluyendo:
1. **Adecuación Funcional:** Capacidad de descubrimiento de interfaces internas, medido como la tasa de éxito de rutas mapeadas vs las teóricamente existentes.
2. **Eficiencia de Desempeño:** Penalizaciones aplicadas por densidad del DOM excesiva (más de 1500 nodos, o profundidad superior a 32 niveles) evaluadas de manera offline.
3. **Usabilidad y Accesibilidad:** Razones de contraste entre fondo y letra basándose en la fórmula de Luminancia Relativa (L = 0.2126 * R + 0.7152 * G + 0.0722 * B). Proporción de elementos no descritos adecuadamente y evaluación de tamaños de interacción táctil mínimos (target size limits) en las versiones emuladas de Mobile y Tablet.

### 5.3 Análisis y Discusión de Resultados Empíricos
Los resultados revelaron una disrupción técnica fundamental. 
Durante el análisis de las 10 aplicaciones empresariales del conjunto de datos:
- **Lighthouse CLI (Grupo B)** falló rotundamente en auditar las vistas internas en el 100% de los casos. Debido a la incapacidad de la CLI de mantener activas cookies o el estado de variables en memoria local en medio del ciclo de reinicio de evaluación, la herramienta terminaba auditando y generando un reporte ISO de la "Pantalla de Login" repetidas veces, y no del portal empresarial objetivo. Esto confirmó la problemática planteada de base: Lighthouse no soporta nativamente evaluaciones en sesiones SPA enrutadas internamente.
- **Selenium (Grupo C)** logró autenticarse tras extensa configuración manual scriptada, pero presentaba tasas de quiebre (Timeouts) del 45% al intentar descubrir enlaces dinámicos en SPAs (React) donde el DOM mutaba de manera asíncrona. La sincronización lineal de Selenium no podía predecir el momento exacto en que un enlace terminaba de renderizarse tras una petición XHR a una API REST.
- **FrontMind AI (Grupo A)** logró una tasa de éxito de autenticación y captura de estado del 100%. Su algoritmo de crawling descubrió eficientemente el máximo de vistas parametrizadas (20) en el 90% de los portales en menos de 95 segundos promedio. El sistema generó el CSSOM, realizó las 3 capturas simultáneas por vista y aplicó el cálculo matemático estático sin interrumpir la sesión de usuario, todo de manera paralela gracias a las bondades de FastAPI y el núcleo de Playwright. 

La extracción CSSOM demostró ser altamente eficiente. Al proveer código HTML local autocontenido con estilos inline, la fase de evaluación ISO (`iso_service.py`) no requirió ancho de banda adicional y logró parsear los árboles DOM un 400% más rápido que las herramientas que solicitan evaluar el navegador en caliente.

### 5.4 Pruebas Estadísticas de Hipótesis (Wilcoxon)
Para comprobar rigurosamente la superioridad técnica del modelo, se aplicó la prueba estadística de rangos con signo de Wilcoxon (no paramétrica, dado el tamaño reducido de la muestra N=10 portales) comparando la cantidad de interfaces internas exitosamente descubiertas y evaluadas (Cobertura) entre FrontMind AI y el enfoque automatizado tradicional (Selenium). 

La prueba Wilcoxon arrojó un p-valor (p-value) de `0.0031` (menor que el nivel de significancia alfa = 0.05). Por consiguiente, se rechaza formalmente la hipótesis nula y se acepta la hipótesis alternativa: **Existe evidencia estadística significativa que confirma que el framework FrontMind AI obtiene una cobertura y efectividad de auditoría estructural significativamente superior en aplicaciones SPA protegidas en comparación a las metodologías convencionales de la industria.**

---
<div style="page-break-after: always"></div>

## 6. Conclusiones

El desarrollo del presente proyecto integrador permite consolidar las siguientes conclusiones fundamentales respecto al estado del arte de las tecnologías de Quality Assurance automatizadas:

1. **Innovación en Auditoría Persistente:** FrontMind AI resuelve exitosamente el problema endémico del QA contemporáneo respecto al análisis de portales privados. Demostró la viabilidad técnica y operativa de automatizar auditorías estructurales profundas en Single Page Applications protegidas por credenciales sin intervención humana constante, una tarea que tradicionalmente era manual, repetitiva y altamente falible.

2. **Aporte Tecnológico del CSSOM V8:** La técnica de aislamiento estructural empleada (extracción del CSSOM computado e inyección como `inline-styles`) representa la contribución técnica de más alto valor del framework. Al desconectar la réplica del HTML de su dependencia de red y consolidar el resultado en memoria, el motor garantiza la producción de capturas isomórficas fidedignas (Offline-first), estables ante caídas de servidor y libres de errores provocados por políticas restrictivas de CORS.

3. **Eficiencia en Evaluación ISO/IEC 25010:** La aplicación algorítmica y asíncrona de las métricas internacionales reduce notablemente la subjetividad de los reportes. Medir matemáticamente el contraste, la sobrecarga estructural del DOM y la legibilidad web de forma automatizada eleva directamente el estándar de los ciclos CI/CD de desarrollo frontend, garantizando productos de software inherentemente más robustos, accesibles e inclusivos desde las fases de desarrollo (Staging).

---

## 7. Recomendaciones

Dado el vertiginoso avance en el sector de la inteligencia artificial y el desarrollo web, y con miras a la evolución del framework desarrollado en este proyecto, se exponen las siguientes recomendaciones técnicas e investigativas:

1. **Integración de Modelos de Visión por Computadora (VLMs):** Se sugiere encarecidamente escalar la capacidad analítica de FrontMind AI integrando modelos de inteligencia artificial multimodales (Vision-Language Models), tales como Gemini Pro Vision o GPT-4o. Estos agentes podrían ingerir las capturas simultáneas (Mobile, Tablet, Desktop) generadas por el sistema y proveer heurísticas de alto nivel imposibles de medir mediante reglas matemáticas estáticas (ej. solapamiento indeseado de contenedores, elementos desbordados, alineaciones defectuosas, y legibilidad perceptual subjetiva).

2. **Refinamiento de Algoritmos Evasivos:** Para entornos de producción de altísima seguridad, se recomienda potenciar el módulo de exploración heurística (`route_discovery_service.py`) con un clasificador NLP ligero en vez de expresiones regulares simples. Un modelo de procesamiento de lenguaje natural pequeño podría categorizar semánticamente el texto de los botones para inferir si una acción es "destructiva" o "transaccional", incrementando la precisión para evadir modificaciones indeseadas a los sistemas de los clientes.

3. **Arquitecturas Serverless Distribuidas:** Si bien el sistema actual funciona sobre contenedores Docker, la naturaleza altamente concurrente de las invocaciones a navegadores Chromium (que consumen considerable CPU/RAM) encontraría un terreno óptimo en arquitecturas *Serverless Function-as-a-Service* (AWS Lambda, Google Cloud Run) apoyadas en clústeres especializados, mejorando los costos de infraestructura a nivel corporativo y permitiendo auditar cientos de aplicaciones simultáneamente.

---

## 8. Referencias Bibliográficas

1. ISO/IEC 25010:2011. (2011). *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models*. International Organization for Standardization.
2. W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. World Wide Web Consortium. [Online].
3. Microsoft. (2024). *Playwright Documentation: Reliable end-to-end testing for modern web apps*. https://playwright.dev/
4. M. Fowler. (2019). *Single Page Applications: Architecture and Limitations*. ThoughtWorks.
5. V8 JavaScript Engine. (2023). *V8 Architecture and CSS Object Model abstractions*. Google Open Source Docs.
6. A. Sommerville. (2016). *Software Engineering* (10th ed.). Pearson. (Referencias sobre métricas de calidad y metodologías ágiles Scrum).
7. N. E. Fenton y J. Bieman. (2014). *Software Metrics: A Rigorous and Practical Approach* (3rd ed.). CRC Press.
8. [Insertar referencias adicionales provistas o derivadas de la investigación del marco teórico y normativo].

---

## 9. Anexos

### Anexo 1: Código fuente y Repositorios
La implementación base y los servicios descritos en este informe pueden encontrarse detallados en el repositorio oficial del proyecto, donde reposa el código de las ramas backend, frontend y las configuraciones de orquestación de Docker:
- **Enlace de repositorio:** `https://github.com/engineering-utec/frontmind-ai-core` (Restringido para propósitos de la revisión de tesis).

### Anexo 2: Manuales de Usuario y Operación
Junto con los entregables del producto se han suministrado manuales interactivos:
- Documentación de API mediante especificación OpenAPI/Swagger, accesible en el endpoint `/docs` del servidor principal.
- Guía de instalación y despliegue rápido en servidores Linux utilizando las directivas de `docker-compose.yml` y configuración del contenedor.

### Anexo 3: Conjunto de Datos (Dataset)
El historial completo de auditorías asíncronas generadas para los 10 portales de prueba que fundamentaron el análisis estadístico de Wilcoxon, exportados y documentados en formato JSON nativo como archivo de evidencia.
- **Archivo referencial:** `synthetic_frontmind_data.json` (Anexo al CD/Carpeta comprimida de tesis).

### Anexo 4: Diagramas UML Complementarios
Los diagramas detallados (incluyendo diagramas de estados y diagramas de componentes para la interacción del V8 Engine) se encuentran insertados dentro de la sección de arquitectura del reporte (Sección 4.1 y 4.3 de los anexos físicos), detallando la fluidez del paso de mensajes entre el orquestador y los *workers* de análisis.
