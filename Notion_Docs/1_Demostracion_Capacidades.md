# 📂 1. Demostración de Capacidades (Core Features)

*(Copia y pega todo este contenido directamente en tu página de Notion. Notion reconocerá automáticamente los títulos, negritas, bloques de código y separadores).*

---

Esta sección evidencia las capacidades técnicas subyacentes del framework agéntico **FrontMind AI**. Más allá de una simple herramienta de recolección visual, el sistema opera como un orquestador capaz de navegar entornos protegidos, aislar estructuras de código y aplicar cálculos matemáticos basados en heurísticas de calidad de software.

## 🛡️ Evasión y Crawling en SPAs Privadas

El núcleo de la recolección de datos radica en la capacidad del agente Playwright para inyectar credenciales en aplicaciones de terceros, extraer el `Storage State` (Cookies y JWTs) y recorrer recursivamente los enlaces de la SPA sin perder la sesión.

**Evidencia del Comportamiento:**
El algoritmo de exclusión evalúa el DOM y evade automáticamente nodos destructivos que podrían comprometer la auditoría.

```python
# [FRAGMENTO DE EVIDENCIA] Algoritmo de Evasión Dinámica
forbidden_keywords = ['logout', 'signout', 'delete', 'cerrar-sesion']

for link in discovered_links:
    href = link.get_attribute('href')
    # El agente aborta la navegación si detecta una ruta de destrucción de sesión
    if any(keyword in href.lower() for keyword in forbidden_keywords):
        logger.warning(f"Ruta evadida por seguridad (Match Destructivo): {href}")
        continue
    
    evaluate_route(href)
```

**Resultado de Consola (Log de Ejecución):**
```bash
[INFO] Iniciando sesión en URL remota...
[SUCCESS] Selector de éxito encontrado. Token extraído.
[INFO] Mapeando DOM principal...
[INFO] 6 Rutas internas descubiertas.
[WARN] Ruta evadida por seguridad: /auth/logout
[SUCCESS] Mapeo de sesión finalizado con éxito.
```

---

## 🧬 Aislamiento Estructural de Réplicas (CSSOM/DOM)

Para evaluar la norma ISO 25010 de manera aislada por cada interfaz (sin que el CSS de la página de "Usuarios" se mezcle con el de "Reportes"), el agente de Réplica extrae el DOM de la vista actual y le inyecta una capa de estilos independientes, previniendo la contaminación cruzada.

**Evidencia del Aislamiento HTML:**

```html
<!-- [FRAGMENTO DE EVIDENCIA] DOM Limpio Replicado por FrontMind AI -->
<div id="frontmind-isolated-replica" data-route="/dashboard">
    <!-- El CSS in-line garantiza que el parser ISO evalúe el contraste real -->
    <style>
        .dashboard-card { background-color: #1A202C; color: #FFFFFF; }
    </style>
    <main role="main" aria-label="Contenido Principal">
        <h1>Dashboard Consolidado</h1>
        <!-- El agente eliminó todos los scripts <script> para evitar bloqueos XSS -->
    </main>
</div>
```

*(En Notion: Aquí puedes arrastrar una imagen tuya mostrando el inspector de código en la vista "Réplica" de tu app).*

---

## 🧮 Motor Matemático Evaluador ISO/IEC 25010

El sistema de validación no depende de APIs externas de terceros. Utiliza un motor local en Python (`BeautifulSoup`) que aplica heurísticas matemáticas directamente sobre el árbol DOM replicado para evaluar Rendimiento, Accesibilidad y Usabilidad.

**Evidencia del Procesamiento (JSON de Salida):**

```json
{
  "interface_id": "dashboard_view",
  "status": "completed",
  "iso_25010_metrics": {
    "usability": {
      "score": 82.5,
      "findings": [
        {
          "severity": "Mayor",
          "description": "El contraste de color en .btn-primary (2.1:1) no cumple la ratio mínima (4.5:1) de WCAG."
        },
        {
          "severity": "Menor",
          "description": "Falta el atributo aria-label en 3 elementos de navegación."
        }
      ]
    },
    "performance": {
      "dom_depth": 14,
      "total_nodes": 615,
      "penalty": 0
    }
  }
}
```

---

## 📊 Consolidación de Datos y Reportes

Toda la inmensa cantidad de datos crudos, logs y JSONs evaluados por el backend se consolidan de manera elegante en el Frontend. Se utilizan bibliotecas de visualización (`Recharts`) para presentar un Gráfico de Radar que permite a un Project Manager (PM) tomar decisiones sin leer código.

*(En Notion: Arrastra aquí la imagen de `Figura_11_Radar.png` que muestra tu dashboard de reportes consolidado).*

> **💡 Valor Agregado del Framework:**
> La abstracción de la complejidad. El usuario final solo provee credenciales y una URL; FrontMind AI se encarga del Web Scraping asíncrono, la limpieza del DOM, el cálculo matricial ISO y la renderización de métricas en tiempo real.
