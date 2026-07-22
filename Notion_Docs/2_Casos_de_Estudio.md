# 📂 2. Casos de Estudio Reales (End-to-End)

*(Copia y pega este contenido en la siguiente sub-página de tu Notion).*

---

Para validar la madurez del framework **FrontMind AI**, el sistema fue sometido a auditorías en entornos de producción reales. A continuación, se detallan dos casos de estudio End-to-End que demuestran la flexibilidad de la plataforma tanto frente a aplicaciones protegidas (crawling remoto) como frente a empaquetados de código estático local (subida ZIP).

## 📚 Caso de Estudio A: Auditoría Remota en SPA Protegida (Plataforma Macmillan)

El mayor desafío del proyecto consistió en orquestar agentes que pudieran burlar barreras de autenticación sin requerir la configuración manual de Cookies por parte del QA. Se utilizó como objetivo de prueba el portal educativo privado de Macmillan.

### Fase 1: Inyección de Credenciales y Bypass
El usuario (QA) configuró la auditoría marcando la opción *"La aplicación requiere credenciales"*. Proporcionó la URL objetivo, el correo, contraseña y los selectores CSS de los inputs (`#username`, `#password`).
- **Comportamiento del Agente:** Playwright levantó un navegador Headless, inyectó la data, hizo clic en *"Ingresar"* y extrajo el token de sesión (JWT/Cookies) tras detectar el selector de éxito.

### Fase 2: Descubrimiento Dinámico de Rutas
Una vez dentro de la SPA autenticada, el agente no se limitó a capturar la primera página. 
- **Comportamiento del Agente:** Recorrió el DOM y descubrió **6 rutas internas**.
- **Logro Técnico:** Evadió explícitamente rutas destructivas (`/logout`) y mantuvo la sesión persistente (Browser Context) para todas las visitas. Generó capturas independientes en Desktop, Tablet y Mobile por cada una.

*(En Notion: Pega aquí la imagen `macmillan_page.png` o la captura de tu plataforma listando las 6 interfaces descubiertas).*

### Fase 3: Evaluación y Resultados (ISO 25010)
Se seleccionó la ruta del *Dashboard* principal de Macmillan. El sistema aisló el HTML en el visor local de FrontMind y el motor de Python calculó la calidad de la interfaz.
- **Resultado:** FrontMind AI emitió exitosamente los hallazgos de usabilidad y estructuró las penalizaciones en el Historial del usuario, cerrando el ciclo End-to-End.

---

## 📦 Caso de Estudio B: Auditoría de Código Local (Desempaquetado ZIP)

Además de navegar URLs remotas, FrontMind AI posee un motor secundario para equipos de desarrollo que desean validar la interfaz de su proyecto *antes* de subirlo a la nube (Shift-Left Testing).

### Fase 1: Carga y Procesamiento Seguro (I/O)
El usuario subió un archivo comprimido (`demo-app.zip`) que contenía un proyecto estático de React (HTML, JS, CSS) desde la pestaña "Subir Código".
- **Comportamiento del Backend:** El controlador de FastAPI extrajo el archivo en un directorio temporal (`extracted_projects_temp/`).
- **Seguridad y Rendimiento:** El algoritmo de filtrado ignoró inteligentemente las carpetas pesadas que no aportan a la UI (como `node_modules/` o `.git/`), evitando el colapso del disco y la memoria RAM del servidor.

### Fase 2: Renderizado Aislado
- **Comportamiento del Agente:** En lugar de hacer una petición HTTP remota (como en el Caso A), Playwright apuntó su navegador hacia el archivo `index.html` recién desempaquetado en el disco del servidor (`file:///.../index.html`).

*(En Notion: Aquí puedes subir una captura de pantalla demostrando cómo se ve la interfaz de tu sección "Carga ZIP" en la app).*

### Conclusión del Caso B
El sistema fue capaz de renderizar los estilos CSS locales y tomarle las respectivas fotografías responsivas y métricas ISO exactamente de la misma manera que con una URL pública, demostrando que **FrontMind AI posee un Pipeline agnóstico a la fuente de origen del código (Remote URL o Local ZIP).**
