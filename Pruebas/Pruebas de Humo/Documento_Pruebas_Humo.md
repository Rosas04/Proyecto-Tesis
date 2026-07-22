# Anexo: Documento de Pruebas de Humo

**Descripción del Caso de Prueba:**
**Tipo de prueba a realizar:** Pruebas de Humo (Smoke Testing)
**Descripción general:**
Evaluación básica y preliminar de los componentes críticos y dependencias principales de FrontMind AI tras un nuevo despliegue. Estas pruebas no evalúan la profundidad de la lógica de negocio, sino que aseguran que el sistema "encienda" correctamente (bases de datos, orquestador, renderizado del SPA, motor de scraping) sin errores catastróficos inmediatos, permitiendo el pase a fases de pruebas de caja blanca y negra.

---

### Escenarios de Prueba:

#### Escenario 1: Renderizado Inicial del Frontend (SPA)
**Datos de Entrada:** Navegación del usuario hacia la URL principal de la aplicación.
**Entorno:** Entorno web público (Render).
**Parámetros:** `url: https://frontmind-frontend.onrender.com/`
**Respuesta de otros módulos:** Frontend descarga los bundles de JavaScript (React/Vite) desde el CDN.
**Condiciones iniciales:** El build de Render debe estar en estado `Live` o `Deploys Completed`.
**Datos de Salida / Resultados entregados:** El navegador recibe HTTP 200 y el DOM inicial se pinta correctamente en la pantalla mostrando el modal de bienvenida. No hay pantallas blancas por errores de React (White Screen of Death).
**Estado final de las variables:** La aplicación SPA está operativa.
**Requisitos de configuración para hacer la prueba:** Conexión a Internet.
**Método de Prueba:** Verificación de Healthcheck Visual.
**Módulos:** Cliente Web.
**Hardware y Software:** Navegador Chrome/Safari actualizado.
**Procedimientos necesarios:** Ingresar a la URL y revisar la consola del navegador.
**Dependencias:** Prerrequisito para cualquier auditoría de usuario.

#### Escenario 2: Verificación del Endpoint de Salud del Backend (FastAPI)
**Datos de Entrada:** Petición HTTP GET al endpoint raíz de la API.
**Entorno:** Postman, cURL o navegador.
**Parámetros:** `url: https://frontmind-api.onrender.com/health` (O similar según entorno).
**Respuesta de otros módulos:** El framework FastAPI procesa el request sin conectarse a la Base de datos.
**Condiciones iniciales:** El contenedor Docker del backend está iniciado.
**Datos de Salida / Resultados entregados:** El endpoint retorna un JSON básico: `{"status": "ok", "version": "1.0.0"}`.
**Estado final de las variables:** `status_code = 200`.
**Requisitos de configuración:** Herramienta de testing de APIs.
**Método de Prueba:** Ping de Disponibilidad de Servicios.
**Módulos:** Core de FastAPI.
**Hardware y Software:** Terminal con cURL.
**Procedimientos necesarios:** Enviar `curl -X GET <API_URL>`.
**Dependencias:** Sin el backend operativo, ninguna captura puede realizarse.

#### Escenario 3: Disponibilidad del Motor Chromium Headless (Playwright)
**Datos de Entrada:** Ejecución de una auditoría simple en el sistema (`test_url.py`).
**Entorno:** Máquina host o Docker Container donde reside Playwright.
**Parámetros:** URL de prueba `https://mvp-mobile.vercel.app`.
**Respuesta de otros módulos:** El agente invoca el subproceso del motor de navegador V8.
**Condiciones iniciales:** Las dependencias del SO (`libnss3`, `libasound2`, etc.) han sido instaladas exitosamente.
**Datos de Salida / Resultados entregados:** Playwright arranca sin devolver el error catastrófico `Executable doesn't exist`.
**Estado final de las variables:** Subproceso del navegador iniciado correctamente en memoria.
*Ilustración: Comprobación de estado de Playwright.*
![Logs de Playwright](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/debug_before_wait.png)
**Requisitos de configuración:** Binarios de Playwright descargados (`playwright install`).
**Método de Prueba:** Prueba de Integridad de Instalación.
**Módulos:** Motor `playwright.sync_api`.
**Hardware y Software:** Servidor backend.
**Procedimientos necesarios:** Validar el output en consola tras enviar una URL pública.
**Dependencias:** Fallar aquí detiene por completo el proyecto de tesis.

#### Escenario 4: Conexión Básica a Supabase (PostgreSQL / Auth)
**Datos de Entrada:** Inicialización del cliente de Supabase al levantar FastAPI.
**Entorno:** Backend.
**Parámetros:** `SUPABASE_URL` y `SUPABASE_KEY` en el archivo `.env`.
**Respuesta de otros módulos:** Respuesta de la red del Cloud de Supabase.
**Condiciones iniciales:** Variables de entorno correctamente inyectadas.
**Datos de Salida / Resultados entregados:** El cliente se inicializa sin arrojar error `AuthApiError` o `Invalid API Key`.
**Estado final de las variables:** Objeto `supabase_client` listo para ser usado.
**Requisitos de configuración:** Credenciales válidas del proyecto.
**Método de Prueba:** Prueba de Credenciales Externas.
**Módulos:** Supabase SDK.
**Hardware y Software:** Python 3.10.
**Procedimientos necesarios:** Comprobar logs de arranque del backend.
**Dependencias:** Prerrequisito para almacenar los JSON generados por el evaluador ISO.

#### Escenario 5: Accesibilidad de la Ruta Principal a Evaluar
**Datos de Entrada:** Envío de URL a auditar (Ej. Macmillan).
**Entorno:** Módulo de validación de URLs en el backend.
**Parámetros:** URL remota.
**Respuesta de otros módulos:** Validación DNS del sistema anfitrión.
**Condiciones iniciales:** Ninguna política de red bloquea el tráfico de salida del servidor.
**Datos de Salida / Resultados entregados:** La URL objetivo está en línea y devuelve código 200 al primer request, evitando colapsar al agente de scraping antes de iniciar.
**Estado final de las variables:** Target vivo.
**Requisitos de configuración:** Red no restringida.
**Método de Prueba:** Comprobación de Red (DNS/Ping).
**Módulos:** Capa de red base.
**Hardware y Software:** OS local.
**Procedimientos necesarios:** El sistema hace un `ping` implícito.
**Dependencias:** Requerido para iniciar flujos de recolección DOM.

#### Escenario 6: Validaciones del Middleware de CORS
**Datos de Entrada:** Petición OPTIONS desde el frontend en Render hacia el backend.
**Entorno:** Capa de seguridad perimetral de la API.
**Parámetros:** Origin: `https://frontmind-frontend.onrender.com`.
**Respuesta de otros módulos:** Aprobación de la capa CORS en FastAPI.
**Condiciones iniciales:** El origen está incluido en el array de orígenes permitidos.
**Datos de Salida / Resultados entregados:** La API responde aceptando los métodos (GET, POST, OPTIONS) sin bloquear el request por `CORS policy`.
**Estado final de las variables:** Request aceptado y ruteado al controlador adecuado.
**Requisitos de configuración:** Orígenes permitidos configurados.
**Método de Prueba:** Solicitud Preflight de integración.
**Módulos:** CORS Middleware.
**Hardware y Software:** Cliente Web / Servidor HTTP.
**Procedimientos necesarios:** Iniciar auditoría desde el Front y observar panel de red (F12).
**Dependencias:** Fundamental para la integración Front-Back.

#### Escenario 7: Validación de Accesibilidad del Módulo ISO 25010
**Datos de Entrada:** Llamado a la función maestra del evaluador.
**Entorno:** Analizador Beautiful Soup.
**Parámetros:** Mock HTML de prueba.
**Respuesta de otros módulos:** Retorno numérico.
**Condiciones iniciales:** Librerías de Python instaladas.
**Datos de Salida / Resultados entregados:** El algoritmo no sufre de excepciones por librerías faltantes (ej. módulo `bs4` no encontrado) y calcula un resultado preliminar.
**Estado final de las variables:** Resultado `>= 0`.
**Requisitos de configuración:** `requirements.txt` instalado.
**Método de Prueba:** Lógica básica de componente.
**Módulos:** Evaluador ISO.
**Hardware y Software:** Entorno Python.
**Procedimientos necesarios:** Import de la clase principal en consola.
**Dependencias:** Núcleo de la tesis académica.

#### Escenario 8: Despliegue de Gráficos Radiales (Recharts)
**Datos de Entrada:** Renderizado del componente `Dashboard.jsx`.
**Entorno:** Interfaz de usuario (React).
**Parámetros:** Datos simulados básicos de los resultados ISO.
**Respuesta de otros módulos:** Recharts construye los polígonos del SVG basándose en los datos de entrada.
**Condiciones iniciales:** JSON con al menos un resultado consolidado.
**Datos de Salida / Resultados entregados:** El radar renderiza sin romperse (`TypeError: Cannot read properties of undefined`).
**Estado final de las variables:** Visualización de métricas correcta.
*Ilustración: Gráfico de radar sin errores de renderizado.*
![Radar](file:///c:/Users/Home/Desktop/Proyecto-Tesis/Figura_11_Radar.png)
**Requisitos de configuración:** N/A.
**Método de Prueba:** Smoke Test de Interfaz.
**Módulos:** Módulo de Reportes.
**Hardware y Software:** Navegador.
**Procedimientos necesarios:** Visitar la sección Historial.
**Dependencias:** Requerido para la experiencia de usuario y presentación de datos.

---

### Cuadro de Ejecución y Checklist de Despliegue (Smoke Test Matrix)

A continuación, se detalla la matriz tabular de comprobación rápida para los despliegues en los entornos de Staging y Producción:

| ID | COMPONENTE EVALUADO | ESCENARIO DE PRUEBA (HEALTHCHECK) | ESTADO | RESULTADO OBSERVADO |
| :---: | :--- | :--- | :---: | :--- |
| **SH-01** | Frontend (SPA) | Renderizado inicial del DOM (Render Cloud) | ✅ PASSED | La SPA carga sin errores `500` ni pantallas blancas de React. |
| **SH-02** | Backend API | `/health` endpoint HTTP GET | ✅ PASSED | Retorna `HTTP 200 OK` demostrando que FastAPI está activo. |
| **SH-03** | Scraping Engine | Binarios e inicialización de Playwright | ✅ PASSED | Instancia de Chromium sube a memoria sin arrojar `Executable Missing`. |
| **SH-04** | Base de Datos | Conexión del cliente Supabase a PostgreSQL | ✅ PASSED | El SDK inicia sesión vía Token JWT local sin arrojar error `AuthApiError`. |
| **SH-05** | Red de Origen | Accesibilidad a la URL objetivo (DNS) | ✅ PASSED | El servidor no tiene políticas restrictivas en puertos externos (TCP 80/443). |
| **SH-06** | Seguridad (CORS) | Peticiones Preflight (`OPTIONS`) Front-to-Back | ✅ PASSED | Middleware aprueba requests desde el dominio oficial configurado. |
| **SH-07** | Núcleo Matemático | Evaluador de métricas ISO 25010 | ✅ PASSED | Importación de `BeautifulSoup` y librerías completada sin fallos de compilación. |
| **SH-08** | Interfaz de Usuario | Renderizado de `Recharts` en Historial | ✅ PASSED | Gráficos visuales se pintan adecuadamente sin valores `undefined`. |

---

### Listado técnico:

**Archivos Involucrados:**
- Archivos de configuración de despliegue (`render.yaml`, `Dockerfile`).
- Archivos de inicialización (`main.py`, `Capture.jsx`).
- Variables de Entorno (`.env`).

**Sistemas y Bibliotecas:**
- Render Cloud Platform (Hosting).
- CORS Middleware.
- Navegadores Edge/Chrome/Safari.
- Supabase Core (PostgreSQL).

**Errores Esperados y Mitigados en Smoke Testing:**
- Error 502 Bad Gateway (Backend aún arrancando tras un despliegue).
- CORS Preflight bloqueado (Solucionado al forzar el dominio exacto en el backend).
- Playwright Browser Type missing (Solucionado al incluir la descarga de binarios de Chromium en el Dockerfile).

**Notas:**
- Superadas estas pruebas, se certifica que la plataforma "enciende" correctamente y se puede proseguir a evaluar la precisión matemática de sus modelos mediante Pruebas de Caja Negra.
