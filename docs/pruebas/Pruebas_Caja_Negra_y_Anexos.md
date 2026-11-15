# Anexos Técnicos y Documentos de Prueba - FrontMind AI

A continuación, se presenta la estructura integral de las Pruebas de Caja Negra, Evaluaciones Heurísticas y Anexos Complementarios, adaptados específicamente al flujo de operación, descubrimiento y evaluación técnica de **FrontMind AI**, siguiendo la nomenclatura y estructura requerida.

---

## 1. Anexo 9: Documento de Pruebas de Caja Negra

**Descripción del Caso de Prueba:**
**Tipo de prueba a realizar:** Pruebas de Caja Negra
**Descripción general:**
Evaluación exhaustiva de los módulos de captura de interfaces y autenticación de FrontMind AI, las interacciones con el motor Playwright (fuera de los módulos visuales de React), respuesta a las entradas del usuario (URLs y credenciales), validación del estado del sistema durante el descubrimiento dinámico de rutas, secuencia de mensajes y resiliencia de la sesión persistida (`BrowserContext`).

### Escenarios de Prueba:

#### Escenario 1: Validación y registro de credenciales para evaluación de URL protegida
**Datos de Entrada:** Ingreso de URL base (`https://sso.canvaslms.com/login`), correo de prueba y contraseña en la aplicación FrontMind AI.
**Entorno:** Módulo inicial de análisis (`Capture.jsx`), que recopila la información para la evaluación y las credenciales mediante inputs securizados.
**Parámetros:**
- URL del sistema a evaluar.
- Checkbox "Requiere Autenticación" activado.
- Correo / Nombre de Usuario.
- Contraseña.
- Selector del campo de usuario y contraseña.
**Respuesta de otros módulos:** El frontend envía el payload al endpoint `/capture/url` en FastAPI.
**Condiciones iniciales:** El backend debe estar activo, y la URL objetivo debe ser accesible.
**Datos de Salida / Resultados entregados:** El backend encripta los datos y arranca el motor Playwright. No expone contraseñas en logs (cumpliendo las restricciones de seguridad).
**Estado final de las variables:** `status = "processing"`, motor asíncrono instanciado.

#### Escenario 2: Inicio de sesión del Agente de Playwright en la aplicación objetivo
**Datos de Entrada:** Inserción simulada de credenciales en los selectores correspondientes del DOM de la página objetivo (ej. Macmillan u OVA).
**Entorno:** Entorno Headless de Chromium operado por el agente de Python.
**Parámetros:** 
- Selector usuario, Selector Password, Selector Botón Login.
**Respuesta de otros módulos:** Espera a que el selector de confirmación de éxito se acople al DOM.
**Condiciones iniciales:** Playwright ha navegado exitosamente a la ruta de inicio de sesión proporcionada en el Escenario 1.
**Datos de Salida / Resultados entregados:** El agente ingresa exitosamente y guarda el contexto en `playwright/.auth/session.json`.
**Estado final de las variables:** Generación del token JWT/Cookies en el contexto de Chromium.

#### Escenario 3: Descubrimiento de rutas internas y exclusión de acciones destructivas
**Datos de Entrada:** Recorrido por el menú lateral, enlaces de navegación y rutas de React Router tras el inicio de sesión.
**Entorno:** Clase `CaptureAgent`, utilizando algoritmos de DFS (Depth-First Search) limitados al DOM principal de la SPA.
**Parámetros:** `max_pages` (ej. 6).
**Respuesta de otros módulos:** Evasión automática de rutas que contengan `/logout`, `/delete`, `destroy`, garantizando la seguridad del scraping.
**Condiciones iniciales:** El usuario debe haber iniciado sesión como usuario real autorizado (Escenario 2).
**Datos de Salida / Resultados entregados:** Lista de hasta 6 interfaces internas accesibles identificadas como únicas (Dashboard, Perfil, Reportes).
**Estado final de las variables:** Array `discovered_routes` completado y depurado de duplicados.

#### Escenario 4: Mantenimiento de la persistencia de sesión (`BrowserContext`) entre vistas
**Datos de Entrada:** Navegación hacia una ruta descubierta (ej. `/reportes`).
**Entorno:** Motor Chromium reinyectando el `storage_state`.
**Parámetros:** Estado de almacenamiento exportado (`session.json`).
**Respuesta de otros módulos:** Evitar que la SPA redirija forzosamente al login, manteniendo la persistencia de tokens de autorización local.
**Condiciones iniciales:** `session.json` válido y no caducado.
**Datos de Salida / Resultados entregados:** Navegación exitosa a `/reportes` demostrando que el login solo se ejecutó una vez, ahorrando recursos y evitando falsos positivos.

#### Escenario 5: Captura y generación de métricas DOM individuales (Desktop, Tablet, Mobile)
**Datos de Entrada:** Carga completa del DOM principal de cada ruta descubierta.
**Entorno:** Servicio de Playwright dimensionando el Viewport (`1920x1080`, `768x1024`, `375x667`).
**Parámetros:** Pausa controlada para carga asíncrona (networkidle).
**Respuesta de otros módulos:** Guardado de las capturas PNG en un bucket o directorio temporal y extracción de `html_length`, y `dom_metrics` (nodos, botones).
**Condiciones iniciales:** La vista no es una URL repetida y el DOM finalizó el evento "attached".
**Datos de Salida / Resultados entregados:** 3 imágenes por interfaz descubierta, y un desglose DOM preciso por interfaz.

#### Escenario 6: Réplica HTML individual y aislamiento de estilos
**Datos de Entrada:** Extracción directa del HTML en memoria vía `page.content()`.
**Entorno:** Módulo de Replicación CSSOM (CSS Object Model).
**Parámetros:** Documento HTML de la SPA en un momento de tiempo exacto.
**Respuesta de otros módulos:** Inyección de estilos cacheados para construir una réplica funcional de la página sin mezclar HTMLs incompatibles de otras vistas.
**Condiciones iniciales:** `selected_interface_id` en procesamiento individual.
**Datos de Salida / Resultados entregados:** Generación de un HTML independiente estático y de alta fidelidad, listo para ser visualizado en `HtmlReplica.jsx`.

#### Escenario 7: Ejecución de la Evaluación Técnica ISO/IEC 25010 individual
**Datos de Entrada:** DOM procesado y estático de la interfaz aislada (Escenario 6).
**Entorno:** Algoritmo del `ISO 25010 Evaluator Agent` utilizando Beautiful Soup en Python.
**Parámetros:** Métricas de Complejidad DOM, Profundidad del Árbol, y Dimensiones de medios.
**Respuesta de otros módulos:** Generación de puntaje y hallazgos estructurados (Ej: "Puntaje 82, Hallazgos 14" para la interfaz Dashboard).
**Condiciones iniciales:** El HTML replica y las capturas deben estar disponibles en almacenamiento.
**Datos de Salida / Resultados entregados:** JSON individual que detalla el cumplimiento de eficiencia de desempeño (Salto de diseño, complejidad de nodos).

#### Escenario 8: Reporte consolidado del sistema completo (Dashboard)
**Datos de Entrada:** Todos los JSON de evaluaciones generados para las múltiples interfaces descubiertas.
**Entorno:** Módulo de reporte en React (`Dashboard.jsx`), gráficos de Recharts.
**Parámetros:** N/A.
**Respuesta de otros módulos:** Procesamiento de promedios, e identificación de la "Interfaz con menor calidad" y "mayor calidad".
**Condiciones iniciales:** El agente de captura ha completado el proceso y retornado el 100% de la metadata.
**Datos de Salida / Resultados entregados:** Gráficos radiales y un reporte global presentado de manera interactiva y "premium" al usuario, culminando la auditoría.

---
### Listado Técnico:
**Archivos Involucrados:**
Se usaron los servicios establecidos en el proyecto tales como: autenticación y base de datos (Supabase), servicio de captura asíncrona (`agents/capture_agent.py`), evaluador normativo (`evaluate_iso.py`), lógica de aislamiento CSS (`summary_json.py`), controladores de React Router, interfaz principal de evaluación (`Capture.jsx`), e historial (`history.json`).

**Sistemas y Bibliotecas:**
- FastAPI (Orquestador Backend)
- Playwright for Python (Chromium Headless)
- React / Vite (Frontend SPA)
- Supabase (Auth / PostgreSQL)
- Recharts (Gráficos)
- Beautiful Soup (Parsing HTML)
- Pytest (Suite de Pruebas Unitarias)

**Errores Detectados e Iterados:**
- Al recorrer rutas de React Router, el SPA a veces expulsaba la sesión debido a una inyección de cookies insuficiente. Solucionado persistiendo completamente el `localStorage` en el Storage State asíncrono.
- La concatenación de estilos de múltiples vistas creaba colisiones globales, resuelto al garantizar la encapsulación individual del HTML por interfaz (Escenario 6).

**Notas:**
- Se recomienda implementar una capa de cache (Redis) si la aplicación escala y requiere la revisión en tiempo real de múltiples usuarios para la misma URL.

---

## 2. Anexo 10: Documentos de Heurísticas de Nielsen

### 1. Metodología
**1.1 Comparación entre Usabilidad y Experiencia del usuario:**
La Usabilidad de FrontMind AI garantiza la efectividad de sus paneles técnicos al presentar métricas (ISO 25010), mientras que la Experiencia de Usuario asegura que la plataforma (dirigida a Desarrolladores y Analistas QA) sea dinámica, estéticamente premium y no frustrante a pesar del elevado volumen de datos de auditoría.

**1.2 Métodos de evaluación de usabilidad**
- **1.2.1 Pruebas de usabilidad:** Se recurrió a "Pensamiento en voz alta" donde los QA testers documentaban sus problemas interpretando las gráficas radiales, y "Pruebas en Papel" durante el diseño inicial del dashboard.
- **1.2.2 Evaluación Heurística:**
  - **1.2.2.1 Interpretación:** Uso de escala de Frecuencia (0-4) y Severidad (0-4), combinados para calcular la Criticidad.
  - **1.2.2.2 Principios Heurísticos aplicados:** Visibilidad del estado, Consistencia y estándares, Prevención de errores, Estética minimalista, etc.

### 2. Preparación
**2.1 Sector:** Tecnología de la Información (Ingenieros QA, Desarrolladores Frontend, Arquitectos Cloud, edades de 22 a 45 años). Las interfaces deben lucir profesionales, oscuras (dark mode preferente) y con jerarquía de datos clara.
**2.2 Elección de principios heurísticos:**
- Visibilidad del estado del sistema (Crucial para auditorías de +15 segundos).
- Prevención de errores (Advertencias antes de inyectar rutas destructivas).
- Diseño estético minimalista.
**2.3 Herramienta de evaluación:** Tablas de Frecuencia vs. Impacto.
**2.4 Herramienta de recolección:** Plantillas con (Pantalla, Problema, Recomendación, Prioridad).
**2.5 Herramienta de contrastación:** Pantalla vs Heurística Violada vs Comentario.
**2.6 Selección de evaluadores:** 3 Analistas Senior de QA de la UTEC.

### 3. Ejecución

**3.1 Distribución de datos en tabla de evaluación:**

| PANTALLA | FRECUENCIA | IMPACTO | PERSISTENCIA |
| :--- | :--- | :--- | :--- |
| Login / Auth (Ver Anexo 1) | Comúnmente, cada vez que se audita una URL privada. | 4 | Se resuelve con tareas de inyección de credenciales. |
| Dashboard Consolidado (Ver Anexo 3) | Rara vez, cuando no existen interfaces analizadas. | 2 | Depende de que el usuario inicie un análisis primero. |
| Detalle de Interfaz e ISO (Ver Anexo 4) | Comúnmente, la App necesita desplegar los fallos técnicos. | 4 | Se resuelve tabulando los JSON del backend. |
| Carga de Proyecto ZIP (Ver Anexo 7) | Rara vez, solo cuando el proyecto no está en la nube. | 3 | Se resuelve con tareas de validación del paquete. |

**3.2 Distribución de datos en herramienta seleccionada:**

| PANTALLA | PROBLEMA | RECOMENDACIÓN | PRIORIDAD |
| :--- | :--- | :--- | :--- |
| Login / Auth (Ver Anexo 1) | Al inyectar credenciales, no hay feedback visual de espera en Playwright. | Agregar un spinner o loader asíncrono que informe del proceso. | 4 |
| Dashboard Consolidado (Ver Anexo 3) | Cuando el backend falla, la UI se queda en blanco sin error claro. | Agregar ventana de error o banner global (Toast). | 3 |
| Detalle de Interfaz e ISO (Ver Anexo 4) | Si la métrica es muy baja, no se recomienda cómo arreglar el HTML. | Mostrar recomendaciones heurísticas junto al puntaje ISO. | 4 |

**3.3 Distribución de datos con las heurísticas seleccionadas (Contrastación):**

| Número | Interfaz | Heurística Seleccionada | Comentario |
| :--- | :--- | :--- | :--- |
| 1 | Login / Auth | Visibilidad del estado del sistema. | Es vital que el agente muestre un "Cargando..." mientras Playwright scrapea. |
| 2 | Dashboard Consolidado | Diseño práctico y minimalista. | Los gráficos de Radar ayudan a no saturar de tablas de datos técnicos al usuario. |
| 3 | Detalle de Interfaz | Reconocer mejor que recordar. | Guardar en el Historial para no forzar al analista a recordar evaluaciones pasadas. |
| 4 | Carga de Proyecto ZIP | Prevención de errores. | Validar que el archivo sea estrictamente `.zip` antes de enviarlo al servidor. |

### 4. Conclusiones
Las pruebas heurísticas en FrontMind AI permitieron identificar fricciones al cargar proyectos manuales en ZIP frente al análisis URL automatizado, mejorando significativamente el *onboarding* técnico y resultando en un Dashboard limpio que traduce la complejidad del ISO 25010 en métricas digeribles.

### 5. Gráficos (Ilustraciones y capturas)
*Nota: Estos anexos referencian capturas reales de la aplicación FrontMind AI almacenadas en el proyecto.*

- **5.1 Anexo 1:** Ventana de Login y Autenticación del usuario al sistema.
![Login FrontMind](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/frontmind_login.png)

- **5.2 Anexo 2:** Mensajes de estado y carga durante el análisis automatizado Playwright (`debug_before_wait.png`).
![Debug Antes](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/debug_before_wait.png)

- **5.3 Anexo 3:** Ventana del Dashboard consolidado, visualizando los reportes históricos.
![Dashboard](file:///c:/Users/Home/Desktop/Proyecto-Tesis/Figura_11_Radar.png)

- **5.4 Anexo 4:** Pantalla de Detalle de Evaluación de Interfaz (Desglose de ISO 25010 individual).
- **5.5 Anexo 5:** Visualización del CSSOM Replicado de forma aislada.
- **5.6 Anexo 6:** Formulario de escaneo de URL privada.
- **5.7 Anexo 7:** Modal de Subida de Proyectos empaquetados en archivo `.ZIP`.
- **5.8 Anexo 8:** Captura remota de interfaz analizada (`macmillan_page.png`).
![Macmillan Page](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/macmillan_page.png)

---

## 3. Anexo 11: Encuesta realizada a Analistas/Desarrolladores post-evaluación
**Cuestionario de Evaluación de Satisfacción de FrontMind AI:** 
Dirigido a Ingenieros de Calidad de Software que testearon Single Page Applications autenticadas (Preguntas 1 a 8 centradas en precisión técnica, velocidad de ejecución y diseño premium).

---

## 4. Anexo 12: Entrevista realizada a Expertos después del uso del Framework
**a. Entrevista a Expertos QA:** Enlace a repositorio audiovisual / Drive con la validación de la metodología asíncrona del sistema.
**b. Fotos de la sesión:** Capturas de la videollamada demostrando el flujo de Replicación de la Memoria del Motor V8.

---

## 5. Anexo 13: Correo de Validación del Asesor Técnico (SME)
Correo de revisión y comentarios emitidos por el equipo de asesoría de Ingeniería de Software (UTEC) respecto a la robustez del scraping con persistencia de tokens JWT y la fidelidad del DOM estático generado.

---

## 6. Anexo 14: Correo de Aprobación de Despliegue en Render (CI/CD)
Notificación de procesamiento y Build completado exitosamente en el servidor en la nube Render, donde el orquestador backend de FrontMind AI pasó exitosamente todos los chequeos de red.

---

## 7. Secciones Finales de Evidencias y Documentación Institucional
**2. Evidencias de la ejecución de la propuesta:** Diseños de arquitectura (Diagramas C4 y Secuencia de la SPA), talleres de definición técnica (Gráficos fotográficos).
**3. R.D. que aprueba el proyecto de investigación:** Resolución administrativa de la escuela de pregrado autorizando el desarrollo del Framework.
**4. Constancia de la Institución y/o organización:** Carta de aceptación emitida por la UTEC / Departamento de Ingeniería respecto al uso de las instalaciones y repositorios de prueba.
