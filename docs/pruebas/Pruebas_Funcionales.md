# Plan de Especificación de Pruebas Funcionales (FTS)

**Nombre del Proyecto:** FrontMind AI (Framework Agéntico de Auditoría Frontend)
**Versión del Documento:** 1.0
**Tipo de Pruebas:** Funcionales (End-to-End, Integración de Módulos)

---

## 1. Introducción

### 1.1 Propósito
El propósito de este documento es definir el plan, alcance, estrategia y la especificación detallada de los casos de prueba funcionales para el sistema FrontMind AI. Este plan asegura que todos los requerimientos funcionales descritos en la investigación se comportan conforme a la lógica de negocio esperada, garantizando un despliegue fiable y una validación de la norma ISO/IEC 25010 aplicable a Single Page Applications.

### 1.2 Alcance
Se evaluarán a profundidad los siguientes componentes lógicos:
1. **Módulo de Autenticación** (Supabase y Gestión de Tokens JWT).
2. **Módulo de Captura Autónoma** (Orquestación del Agente Playwright en contextos autenticados y descubrimientos dinámicos de URL).
3. **Módulo de Réplica de Interfaz** (Aislamiento de Árboles DOM/CSSOM).
4. **Módulo de Evaluación Matemática** (Parser ISO/IEC 25010 con BeautifulSoup).
5. **Módulo de Consolidación y Reportes** (Representaciones de Recharts y Persistencia del Historial).

### 1.3 Referencias
- *Estándares IEEE 829-2008 / ISO/IEC/IEEE 29119* aplicados a entornos Ágiles.
- Requerimientos Funcionales de la Tesis (Evaluación ISO 25010 en Arquitecturas SPA).

---

## 2. Entorno y Configuración de Pruebas

### 2.1 Requisitos de Hardware y Software
- **Cliente:** Navegadores Web actualizados (Chrome v110+, Safari, Edge).
- **Servidor (Backend):** Python 3.10+, FastAPI, Playwright (Chromium binario instalado).
- **Servidor (Frontend):** Entorno Node.js (React/Vite) desplegado en la nube.

### 2.2 Herramientas de Ejecución
- **Monitorización de Red:** Chrome DevTools (Pestaña Network y Console).
- **Base de Datos y Auth:** Panel de Supabase Project.
- **Orquestación Asíncrona:** Logs de sistema del Cloud Provider (Render).

### 2.3 Datos de Prueba (Test Data)
- **URL Pública/Privada de Prueba:** `https://mvp-mobile.vercel.app`, `https://identity.macmillaneducationeverywhere.com`
- **Archivo de Subida de Prueba:** Paquetes `.zip` preparados conteniendo estructura estándar de React.

---

## 3. Estrategia de Pruebas Funcionales

### 3.1 Enfoque de Evaluación
Se aplicará el enfoque de **Caja Negra a Nivel Funcional** con validación End-to-End (E2E). El probador interactuará con la interfaz gráfica (GUI) como un Analista QA real y medirá que las interacciones del sistema subyacente (Playwright) funcionen sin exponer fallos estructurales a la capa visual.

### 3.2 Técnicas de Diseño de Casos
- **Pruebas de Transición de Estado:** Críticas para evaluar el comportamiento del Crawler al navegar de una URL de Login (`/login`) hacia rutas internas protegidas (`/dashboard`, `/profile`) sin perder la cookie/estado de memoria en Playwright.
- **Partición de Equivalencia:** Inyección de credenciales formales e informales.
- **Análisis de Valores Límite:** Ingreso de más URLs de las permitidas por el límite configurado (`max_pages`).

---

## 4. Matriz de Trazabilidad de Requisitos (RTM)

| ID Requerimiento | Descripción del Requerimiento Funcional | ID Caso de Prueba | Cobertura |
| :---: | :--- | :---: | :---: |
| **RF-01** | El sistema debe permitir iniciar sesión y persistir el usuario. | CP-FUN-01 | Alta |
| **RF-02** | El agente debe lograr autenticarse remotamente y evadir logouts. | CP-FUN-02, CP-FUN-03 | Crítica |
| **RF-03** | El sistema debe desempaquetar y renderizar proyectos estáticos en `.zip`. | CP-FUN-04 | Media |
| **RF-04** | El backend debe generar réplicas HTML independientes por vista. | CP-FUN-05 | Crítica |
| **RF-05** | La plataforma calculará el ISO 25010 y agrupará los datos en un dashboard. | CP-FUN-06, CP-FUN-07 | Alta |
| **RF-06** | El sistema debe persistir un historial consultable por usuario. | CP-FUN-08 | Media |

---

## 5. Especificación de Casos de Prueba Detallados

A continuación, la ejecución documentada paso a paso para la certificación de los módulos:

### **CP-FUN-01: Autenticación, Autorización y Contexto de Usuario en Supabase**
- **Módulo:** Autenticación
- **Precondiciones:** La API de Supabase está en línea y el proyecto base configurado con `anon_key`.
- **Datos de Entrada:** Correo y Password válidos.
- **Pasos de Ejecución:**
  1. Ingresar a `https://frontmind-frontend.onrender.com/login`.
  2. Rellenar los inputs de autenticación y hacer click en "Ingresar".
  3. Refrescar la pestaña actual (F5).
- **Resultado Esperado:** El usuario es autenticado. Al recargar la página, la SPA no redirige de vuelta al login debido a que recupera exitosamente la sesión persistente.
- **Resultado Obtenido:** **[PASSED]** El token JWT persistió en Local Storage, manteniendo la sesión intacta tras el F5.
- **Evidencia requerida:**
![Login FrontMind](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/frontmind_login.png)

### **CP-FUN-02: Autenticación de Agente Remoto y Persistencia de Storage State (Core)**
- **Módulo:** Captura Autónoma
- **Precondiciones:** Aplicación FrontMind funcional.
- **Datos de Entrada:** URL Privada (ej. Macmillan), selectores CSS (`#username`, `#password`), credenciales válidas y selector de confirmación de éxito.
- **Pasos de Ejecución:**
  1. En el módulo Captura, configurar "La aplicación requiere credenciales".
  2. Ingresar la data de entrada respectiva.
  3. Ejecutar "Iniciar Análisis".
- **Resultado Esperado:** Playwright arranca, inserta las credenciales en la web remota, extrae la Cookie y Session del Browser y la almacena sin devolver Timeout o fallos de inyección DOM.
- **Resultado Obtenido:** **[PASSED]** El agente logró inyectar los datos e identificó exitosamente el selector de éxito.
- **Evidencia requerida:**
![Captura Asíncrona](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/debug_before_wait.png)

### **CP-FUN-03: Algoritmo Dinámico de Crawling y Evasión de Rutas Destructivas**
- **Módulo:** Captura Autónoma
- **Precondiciones:** El agente completó exitosamente el `CP-FUN-02` y tiene el Storage State válido.
- **Datos de Entrada:** N/A (Flujo automático).
- **Pasos de Ejecución:**
  1. El agente carga la primera vista del Dashboard remoto con el Token inyectado.
  2. El crawler evalúa el DOM buscando etiquetas `<a>` o botones con eventos click.
- **Resultado Esperado:** Se mapean múltiples interfaces, pero algoritmos de exclusión ignoran estrictamente enlaces que contengan palabras como `/logout`, `/delete` o `cerrar-sesion` para evitar perder el Storage State.
- **Resultado Obtenido:** **[PASSED]** Se recolectaron 6 vistas diferentes, evadiendo eficientemente la ruta de finalización de sesión y manteniendo persistencia en todo el recorrido.
- **Evidencia requerida:**
![Macmillan Route Scan](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/macmillan_page.png)

### **CP-FUN-04: Extracción y Procesamiento Seguro de Empaquetados (ZIP)**
- **Módulo:** Captura (Vía ZIP)
- **Precondiciones:** Archivo comprimido con un proyecto Front-end válido de tamaño menor a 50MB.
- **Datos de Entrada:** Archivo `demo-app.zip`.
- **Pasos de Ejecución:**
  1. Ingresar a la sección "Subir Código".
  2. Arrastrar el archivo comprimido y dar click en Analizar.
- **Resultado Esperado:** El backend de Python descomprime el código omitiendo carpetas inútiles (`node_modules`), lo renderiza estáticamente y extrae la métrica sin dependencias externas.
- **Resultado Obtenido:** **[PASSED]** El archivo se extrajo y el HTML fue leído correctamente, evitando desbordamientos de memoria en el servidor.

### **CP-FUN-05: Aislamiento Estructural de Réplicas (CSSOM/DOM)**
- **Módulo:** Réplica de Interfaz
- **Precondiciones:** Análisis remoto finalizado con múltiples interfaces recolectadas.
- **Datos de Entrada:** Selección manual de una interfaz específica desde la Cuadrícula del Dashboard.
- **Pasos de Ejecución:**
  1. Clic en "Ver Interfaz Evaluada".
- **Resultado Esperado:** Se carga el HTML renderizado, pero aislado en un contenedor independiente, asegurando que los estilos base de la SPA analizada no se contaminen mutuamente si se procesan múltiples rutas a la vez.
- **Resultado Obtenido:** **[PASSED]** Inyección de HTML independiente funcional, garantizando alta fidelidad frente al sitio original.

### **CP-FUN-06: Motor Matemático y Reglas ISO/IEC 25010**
- **Módulo:** Evaluación Técnica y Auditoría
- **Precondiciones:** DOM asilado (Generado en el paso anterior).
- **Datos de Entrada:** Código fuente replicado y metadata extraída del motor Playwright.
- **Pasos de Ejecución:**
  1. El módulo de Python inicia las validaciones estáticas.
- **Resultado Esperado:** BeautifulSoup debe parsear las etiquetas (`img`, `iframes`), el contraste de estilos y profundidad de nodos. Debe arrojar un Score que no sea negativo y clasificar el estado ("Crítico", "Mayor", "Menor").
- **Resultado Obtenido:** **[PASSED]** Evaluador ejecutó correctamente la fórmula matemática asignando un Score proporcional al volumen de fallos encontrados. (Score 82 validado).

### **CP-FUN-07: Consolidado de Reportes Analíticos Radiales**
- **Módulo:** Reportes
- **Precondiciones:** Objeto JSON con el listado completo de interfaces analizadas.
- **Datos de Entrada:** `resultado_iso.json`.
- **Pasos de Ejecución:**
  1. Finaliza el análisis backend.
  2. FrontMind AI transiciona automáticamente a la vista de "Reportes".
- **Resultado Esperado:** Se muestra un consolidado claro de todo el sistema. El Radar Chart (polígono) se renderiza correctamente con las subcaracterísticas evaluadas y no presenta campos rotos.
- **Resultado Obtenido:** **[PASSED]** Recharts procesó exitosamente el mapeo de arrays de datos. La interfaz principal exhibe el radar consolidado.
- **Evidencia requerida:**
![Dashboard Radar Chart](file:///c:/Users/Home/Desktop/Proyecto-Tesis/Figura_11_Radar.png)

### **CP-FUN-08: Gestión de Persistencia Histórica (Trazabilidad)**
- **Módulo:** Historial
- **Precondiciones:** Tener más de un reporte de captura ejecutado.
- **Datos de Entrada:** Navegar a la pestaña "Historial".
- **Pasos de Ejecución:**
  1. Visualizar la tabla de listado.
  2. Hacer clic en una auditoría anterior para rehidratarla.
- **Resultado Esperado:** La base de datos recupera el payload JSON almacenado vinculado al usuario. El Dashboard se dibuja instantáneamente sin necesidad de arrancar Playwright de nuevo.
- **Resultado Obtenido:** **[PASSED]** Carga de datos diferida perfecta, ahorrando valiosos recursos de computación en la nube.

---

## 6. Criterios de Aceptación, Suspensión y Reanudación

### 6.1 Criterios de Aceptación
Para que las pruebas funcionales se consideren "Exitosas" y listas para Producción, el sistema FrontMind AI debe cumplir que:
- El 100% de los casos de la Malla Crítica (CP-FUN-02, CP-FUN-03, CP-FUN-06) estén en estado **PASSED**.
- Ningún error catastrófico (Crash a nivel SO o Fallo de memoria en el servidor) ocurra durante el scraping recursivo de rutas.
- Las penalizaciones matemáticas del sistema de calidad ISO 25010 nunca otorguen puntajes inválidos (Ej: `-15` de Score).

### 6.2 Criterios de Suspensión
Las pruebas funcionales se abortarán y reiniciarán en caso de que ocurran los siguientes escenarios críticos:
- La base de datos de Supabase pierda conexión o se modifique su esquema impidiendo el guardado de reportes.
- El servidor Cloud agote sus recursos (RAM > 95%) por la orquestación simultánea de Headless Browsers.

### 6.3 Reanudación
La suite de pruebas continuará solo después de que el Equipo de DevOps asegure el parche, verifique un `pull request` limpio, y el despliegue del componente se confirme como estable en las Pruebas de Humo (Smoke Tests).

---

## 7. Entregables de la Prueba

El proceso de QA y Certificación emite los siguientes entregables adjuntos a la tesis:
1. **Plan de Especificación de Pruebas (FTS):** Este documento, completo y detallado.
2. **Matriz de Defectos (Bug Tracker):** Documentación interna de correcciones.
3. **Registro Gráfico (Log):** Colección de capturas visuales de cada uno de los 8 hitos críticos del sistema, certificando su correcto comportamiento orgánico.
