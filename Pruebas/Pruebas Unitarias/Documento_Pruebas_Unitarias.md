# Anexo: Documento de Pruebas Unitarias

## 1. Información General

- **Proyecto:** FrontMind AI (Backend)
- **Framework de Pruebas:** `pytest`
- **Librerías de Mocking:** `unittest.mock` (nativo de Python) / `pytest-mock`
- **Objetivo:** Analizar, diseñar y estructurar la suite completa de pruebas unitarias asegurando cobertura sobre agentes, servicios, cálculos matemáticos, validaciones del estándar ISO/IEC 25010 y flujos de control de errores sin dependencia de agentes externos (Base de Datos, Red o Navegador).

## 2. Estrategia de Pruebas y Aislamiento (Mocks)

Para garantizar pruebas unitarias puras, rápidas y deterministas, aislaremos el código de factores externos mediante las siguientes técnicas:

- **Entrada/Salida (I/O):** Se utilizará `unittest.mock.mock_open` y mocks para `json.load`/`json.dump` para simular la persistencia de datos local (JSON).
- **Servicios Externos (Playwright):** Se creará un Mock de la clase `Page` y del navegador de Playwright para simular `goto()`, `fill()`, `click()` y llamadas DOM sin levantar una instancia real.
- **Sistema de Archivos:** Mockeo del módulo nativo `zipfile` y de métodos de manipulación de archivos (`os.path`, `shutil`).

## 3. Estructura del Directorio de Pruebas

La suite de pruebas se organizará en una carpeta independiente en la raíz de `frontmind-agents` para mantener el orden arquitectónico:

```
frontmind-agents/
├── agents/                  # Código fuente de Agentes
├── services/                # Código fuente de Servicios
└── tests/                   # Directorio de Pruebas Unitarias
    ├── conftest.py          # Fixtures globales de pytest
    ├── agents/              # Pruebas de Agentes
    │   ├── test_report_agent.py
    │   ├── test_iso_evaluation_agent.py
    │   ├── test_html_replication_agent.py
    │   └── test_capture_agent.py
    └── services/            # Pruebas de Servicios
        ├── test_iso_service.py
        ├── test_history_service.py
        ├── test_auth_service.py
        ├── test_route_discovery_service.py
        └── test_zip_service.py
```

## 4. Casos de Prueba Detallados

### Bloque A: Pruebas para Servicios (`services/`)

| **ID Caso** | **Módulo / Servicio** | **Función a Probar** | **Tipo de Prueba** | **Mock Aplicado** | **Comportamiento Esperado** |
| --- | --- | --- | --- | --- | --- |
| **ST-ISO-01** | `iso_service.py` | `clamp()` | Lógica / Frontera | Ninguno | Limita valores correctamente fuera de rango [0, 1]. |
| **ST-ISO-02** | `iso_service.py` | `parse_hex_color()` | Lógica / Datos | Ninguno | Transforma formatos Hex (3 y 6 chars) a tuplas RGB correctas. |
| **ST-ISO-03** | `iso_service.py` | `get_contrast_ratio()` | Lógica / Cálculo | Ninguno | Calcula correctamente el ratio de contraste relativo (ej. 21:1 para Blanco/Negro). |
| **ST-ISO-04** | `iso_service.py` | `evaluate_iso_25010()` | Estructura HTML | Ninguno | Retorna score de 0 o advertencia si el HTML está vacío o no contiene `<main>`. |
| **ST-HIST-01** | `history_service.py` | `load_history()` | Control de Errores | `mock_open`, `json.load` | Retorna lista vacía ante un archivo JSON corrupto o inexistente. |
| **ST-AUTH-01** | `auth_service.py` | `execute_login()` | Integración Mock | Playwright `Page` | El flujo lógico de autenticación culmina exitosamente tras llenar formularios simulados. |
| **ST-ZIP-01** | `zip_service.py` | `extract_and_filter()` | Sistema de Archivos | `zipfile.ZipFile`, `os.walk` | Extrae recursos ignorando carpetas `.git` y `node_modules`. |

### Bloque B: Pruebas para Agentes (`agents/`)

| **ID Caso** | **Módulo / Agente** | **Función a Probar** | **Tipo de Prueba** | **Mock Aplicado** | **Comportamiento Esperado** |
| --- | --- | --- | --- | --- | --- |
| **AG-REP-01** | `report_agent.py` | `build_severity_summary` | Estructura de Datos | Ninguno | Agrupa y cuenta correctamente las severidades (Crítica, Mayor, Menor). |
| **AG-REP-02** | `report_agent.py` | `build_conclusion` | Lógica Condicional | Ninguno | Genera una conclusión "Aprobado" si los scores superan el umbral mínimo definido. |
| **AG-ISO-01** | `iso_evaluation_agent.py` | `orchestrate_evaluation` | Orquestación | `evaluate_iso_25010` | Ejecuta la lógica del agente llamando al servicio con el payload adecuado. |
| **AG-HTML-01** | `html_replication_agent.py` | `cleanup_html` | Procesamiento Text | Ninguno | Elimina scripts sospechosos e inyecta correctamente las etiquetas de CSSOM. |
| **AG-CAP-01** | `capture_agent.py` | `run_capture_flow` | Integración Mock | `auth_service`, Playwright | Ejecuta el pipeline completo y ante un fallo de red dispara el mecanismo de fallback de manera controlada. |

## 5. Plan de Ejecución y Verificación

### Ejecución de Pruebas Unitarias (Local)

Para ejecutar la suite de pruebas completa en modo detallado (`verbose`):

```bash
pytest -v tests/
```

### Reporte de Cobertura de Código

Para analizar qué porcentaje de nuestras líneas de código del backend están cubiertas efectivamente por pruebas unitarias:

```bash
pytest --cov=agents --cov=services --cov-report=term-missing tests/
```

## 6. Métricas y Criterios de Aceptación (QA)

- **Cobertura Mínima Requerida (Coverage):** **> 80%** en la carpeta `services/` e `agents/`.
- **Tiempo de Ejecución Total:** < 10 segundos para toda la suite (gracias al aislamiento estricto con mocks).
- **Manejo de Errores (Resiliencia):** 100% de los flujos alternativos de lectura de archivos y fallos de Playwright deben estar cubiertos con aserciones controladas.
