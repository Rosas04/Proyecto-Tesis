# Anexo: Documento de Pruebas de Caja Blanca

**Descripción del Caso de Prueba:**
**Tipo de prueba a realizar:** Pruebas de Caja Blanca (White-box Testing / Structural Testing)
**Descripción general:**
Evaluación de la lógica interna, el flujo de datos y la cobertura de sentencias (statement coverage) de los módulos core de FrontMind AI escritos en Python (FastAPI y Playwright). A diferencia de las pruebas de caja negra, estas pruebas verifican el comportamiento de las estructuras de control internas (bucles `for/while`, manejo de excepciones `try/except`) y la integridad algorítmica.

---

### Escenarios de Prueba:

#### Escenario 1: Validación de condición de parada en el descubrimiento recursivo de rutas
**Datos de Entrada:** Array mockeado de URLs extraídas del DOM que contiene enlaces circulares (A -> B -> A).
**Entorno:** Método interno `extract_links()` o rutina de crawling de la clase `CaptureAgent`.
**Parámetros:** 
- `current_url`: Ruta en evaluación.
- `visited_urls`: Set de memoria en Python (`set()`).
**Respuesta de otros módulos:** N/A. Prueba aislada de lógica algorítmica.
**Condiciones iniciales:** El set `visited_urls` ya contiene la URL 'A'.
**Datos de Salida / Resultados entregados:** El bloque condicional `if link not in visited_urls:` es evaluado. La función se salta la adición al stack de procesamiento.
**Estado final de las variables:** Prevención exitosa de un bucle infinito (StackOverflow). `routes_discovered` mantiene un conteo exacto sin duplicados.
*Ilustración: Proceso de descubrimiento asíncrono.*
![Captura de estado inicial](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/debug_before_wait.png)
**Método de prueba:** Path Testing (Prueba de ruta de control).
**Módulos:** Agente de Captura (`capture_agent.py`).

#### Escenario 2: Captura de excepciones en la inyección de evaluación asíncrona de DOM
**Datos de Entrada:** Forzar una desconexión de contexto (`Target closed`) mientras Playwright evalúa el script del navegador.
**Entorno:** Manejador asíncrono de Playwright ejecutando `page.evaluate(js_script)`.
**Parámetros:** Promesa inyectada en el motor V8.
**Respuesta de otros módulos:** El bloque `try/except Exception as e:` captura el Timeout o desconexión del cliente.
**Condiciones iniciales:** El DOM está corrupto o la red se interrumpe intencionalmente.
**Datos de Salida / Resultados entregados:** El error no derriba la API de FastAPI. El except bloquea el fallo y devuelve un objeto JSON estandarizado: `{"error": "Context disconnected", "status": "failed"}`.
**Estado final de las variables:** La interfaz que falló se marca como `failed` pero el bucle general de la aplicación continúa evaluando otras interfaces.
*Ilustración: Estado posterior a la reconexión.*
![Captura de reconexión asíncrona](file:///c:/Users/Home/Desktop/Proyecto-Tesis/frontmind-agents/debug_after_wait.png)
**Método de prueba:** Pruebas de Inyección de Fallos / Manejo de Excepciones.

#### Escenario 3: Integridad de la lógica matemática en el algoritmo de evaluación ISO 25010
**Datos de Entrada:** JSON estático de métricas DOM procesadas (ej. 3000 nodos, 5 iframes vacíos, 0 botones).
**Entorno:** Módulo de parser en Python (`evaluate_iso.py`).
**Parámetros:** `total_nodes`, `empty_src_count`, `deep_tree_level`.
**Respuesta de otros módulos:** El script evalúa los pesos de penalización en sus condicionales matemáticos.
**Condiciones iniciales:** Los datos de entrada sobrepasan los límites máximos permitidos por el modelo de calidad.
**Datos de Salida / Resultados entregados:** El coeficiente base no baja de 0 (manejo de límites inferiores como `max(0, puntaje)`). El resultado arrojado es el mínimo lógico esperado y la penalización no corrompe el puntaje general.
**Estado final de las variables:** `final_score = 0` o un número positivo válido sin desbordamiento.
**Método de prueba:** Boundary Value Analysis de Caja Blanca (Prueba de valores límite a nivel de código).

#### Escenario 4: Verificación del Middleware CORS en el Framework FastAPI
**Datos de Entrada:** Petición HTTP OPTIONS (Pre-flight request) originada desde un dominio no autorizado (ej. `http://malicious-site.com`).
**Entorno:** Capa de red del Web Service Backend.
**Parámetros:** Headers de la petición (`Origin`, `Access-Control-Request-Method`).
**Respuesta de otros módulos:** El middleware `CORSMiddleware` intercepta la petición antes de llegar al router de captura.
**Condiciones iniciales:** Las variables de entorno de `ALLOWED_ORIGINS` están configuradas estrictamente para la IP local y Render.
**Datos de Salida / Resultados entregados:** El servidor responde con HTTP 403 o no incluye `Access-Control-Allow-Origin`, abortando el request.
**Estado final de las variables:** Solicitud rechazada. El endpoint de procesamiento principal jamás se ejecuta.
**Método de prueba:** Statement Coverage (Cobertura de middleware).

#### Escenario 5: Cobertura de la serialización JSON de respuestas asíncronas
**Datos de Entrada:** Finalización de la recolección de las 6 interfaces descubiertas y el reporte de promedios.
**Entorno:** Controlador HTTP principal (endpoint de FastAPI).
**Parámetros:** El gran diccionario de Python (`dict`) con anidaciones de arrays para interfaces y capturas.
**Respuesta de otros módulos:** `JSONResponse()` de Starlette/FastAPI serializa el objeto.
**Condiciones iniciales:** Existen campos `Datetime` no nativos de JSON.
**Datos de Salida / Resultados entregados:** La serialización lanza excepción o se soluciona usando un encoder personalizado para devolver strings ISO 8601 al frontend de React.
**Estado final de las variables:** Payload entregado exitosamente al cliente mediante HTTP 200.

---
### Listado técnico y Cuadro de Cobertura:

**Matriz de Evaluación Estructural (Caja Blanca):**

| ID | ESCENARIO (Ruta de Ejecución) | TIPO DE PRUEBA | COMPONENTE | ESTADO | RESULTADO OBSERVADO |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CB-01 | Algoritmo DFS `if link not in visited` | Path Testing | `capture_agent.py` | PASSED | Previene StackOverflow y descarta bucles infinitos en SPAs. |
| CB-02 | Captura de Timeout con `try/except` | Branch Coverage | `Playwright Engine` | PASSED | La excepción asíncrona es capturada sin colgar el hilo del backend. |
| CB-03 | Límite inferior `max(0, puntaje)` en métricas | Boundary Value | `evaluate_iso.py` | PASSED | La fórmula matemática bloquea valores negativos en el coeficiente ISO. |
| CB-04 | Intercepción de OPTIONS origin | Statement Cov. | `FastAPI CORS` | PASSED | El middleware bloquea solicitudes de orígenes desconocidos (`403 Forbidden`). |
| CB-05 | Serialización de tipos `Datetime` a JSON | Data Flow | `main.py` | PASSED | El serializador convierte automáticamente objetos en strings ISO-8601. |

**Archivos Involucrados:**
- `frontmind-agents/main.py`
- `frontmind-agents/agents/capture_agent.py`
- `frontmind-agents/evaluate_iso.py`
- `frontmind-agents/test_macmillan_full.py`

**Sistemas y Bibliotecas:**
- FastAPI / Starlette
- AST (Abstract Syntax Tree, para parseos de código)
- Pytest (Suite de pruebas internas de código)
- JSONEncoder 

**Errores previstos a nivel de código:**
- Recursión Infinita al escanear rutas SPA (Solucionado usando una estructura de grafos).
- Desbordamiento de memoria por variables instanciadas pero no recolectadas (El `browser_context.close()` en el bloque `finally` garantiza la liberación).

**Notas:**
- Esta documentación es fundamental para el equipo de desarrollo (DevOps/Backend) al asegurar que la plataforma base no es frágil ante aserciones inesperadas de la web pública.
