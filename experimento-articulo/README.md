# Experimento del artículo: fidelidad de captura del DOM de FrontMind AI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Rosas04/Proyecto-Tesis/blob/main/experimento-articulo/FrontMind_DOM_fidelity.ipynb)

Evidencia reproducible del artículo *Structural fidelity of Document Object Model capture for automated web
interface assessment: An empirical evaluation of FrontMind AI* (Universidad Privada Antenor Orrego).

## Cómo ejecutarlo

1. Abre el notebook con el botón **Open in Colab**.
2. En Colab, elige **Entorno de ejecución → Ejecutar todas**.
3. Las partes A–F (datos, estadística, figuras) tardan unos segundos. La parte G instala Playwright y Chromium y
   vuelve a medir los sistemas desplegados A11–A13 (unos 3 minutos).
4. Opcional: con `RUN_BUILDS = True` (celda G.2) también recompila A14 y A15 desde su código fuente y los mide
   (unos 10 minutos).

## Contenido

| Archivo | Descripción |
|---|---|
| `FrontMind_DOM_fidelity.ipynb` | Notebook de Colab: datos, Tablas 4–7, intervalos bootstrap BCa y Hodges–Lehmann, correlaciones, Figuras 2–3 y nueva medición en vivo |
| `FrontMind_DOM_fidelity_ejecutado_colab.ipynb` | Copia ejecutada en Google Colab el 23/11/2026 (Python 3.13, SciPy 1.16.3), con todos los resultados y la nueva medición en vivo de A11–A13 |
| `measure_fidelity.py` | Procedimiento de medición: Chromium sin interfaz, viewport 1366 × 768, espera de red inactiva, desplazamiento completo y réplica con `HtmlReplicationAgent` de `frontmind-agents`; clasifica los nodos removidos por etiqueta |
| `spa_server.py` | Servidor estático con *fallback* SPA para servir las compilaciones de A14 y A15 |
| `data/fidelity_by_system.csv` | Conteos de nodos y tiempos de captura por sistema y corrida (A01–A15) |
| `data/live_A11_A13_23nov2026.json` | Registros por corrida, ruta y etiqueta de A11–A13 (despliegues públicos) |
| `data/live_A14_A15_23nov2026.json` | Registros por corrida, ruta y etiqueta de A14–A15 (compilación de producción local) |
| `data/runs_A14_A15_23nov2026.json` | Registros originales de A14–A15 usados en el artículo |

A01–A10 se midieron dentro del framework FrontMind AI (registros de ejecución); sus conteos se reportan tal como se
registraron. No se incluyen credenciales ni datos personales de los sistemas evaluados.

## Parámetros fijos de la medición

| Parámetro | Valor |
|---|---|
| Navegador | Chromium sin interfaz (Playwright para Python 1.60.0) |
| Viewport | 1366 × 768 px |
| Navegación | `wait_until="domcontentloaded"`, límite de 60 s |
| Espera de red | `networkidle`, límite de 20 s |
| Desplazamiento | hasta el final y de vuelta al inicio, pausas de 300 ms |
| Réplica | `HtmlReplicationAgent.run()`; espera de 500 ms tras renderizarla |
| Conteo de nodos | `document.querySelectorAll('*').length` en la página original y en la réplica |
| Corridas | 3 por sistema |
