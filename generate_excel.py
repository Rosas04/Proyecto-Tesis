import pandas as pd

data = [
    {
        "ID": "PU-01",
        "Tipo": "Unitaria",
        "Nombre del Escenario": "Persistencia del estado de almacenamiento",
        "Datos de Entrada": "test_storage.py",
        "Entorno": "Módulo de Pytest, serialización de cookies y tokens desde BrowserContext a JSON.",
        "Condiciones Iniciales": "Credenciales válidas, acceso de escritura en playwright/.auth",
        "Resultados Esperados": "Código de salida 0, archivo temporal de sesión generado.",
        "Comando de Ejecución": "pytest frontmind-agents/test_storage.py -v"
    },
    {
        "ID": "PU-02",
        "Tipo": "Unitaria",
        "Nombre del Escenario": "Interacción de login y validación de campos",
        "Datos de Entrada": "test_frontmind_login.py con correos/contraseñas válidos e inválidos.",
        "Entorno": "Ambiente controlado, inyección de parámetros en DOM.",
        "Condiciones Iniciales": "Servicio FrontMind local corriendo, conexión de red estable.",
        "Resultados Esperados": "Captura de selectores de error (inválidos) o captura de nueva URL (válidos).",
        "Comando de Ejecución": "pytest frontmind-agents/test_frontmind_login.py"
    },
    {
        "ID": "PH-01",
        "Tipo": "Humo",
        "Nombre del Escenario": "Carga inicial de la aplicación cliente (Frontend)",
        "Datos de Entrada": "Carga de URL principal de la aplicación.",
        "Entorno": "Renderizado del componente principal App.jsx, estado de sesión Supabase.",
        "Condiciones Iniciales": "Despliegue completado, navegador sin sesión activa.",
        "Resultados Esperados": "UI carga sin errores de CORS o red, mostrando diseño principal.",
        "Comando de Ejecución": "Ingreso manual desde navegador web."
    },
    {
        "ID": "PH-02",
        "Tipo": "Humo",
        "Nombre del Escenario": "Verificación del estado de salud (Health Check) del Backend",
        "Datos de Entrada": "Petición HTTP GET al endpoint /health",
        "Entorno": "Controlador principal FastAPI.",
        "Condiciones Iniciales": "Contenedor Backend desplegado.",
        "Resultados Esperados": "Código HTTP 200 OK, JSON status: ok.",
        "Comando de Ejecución": "curl -X GET http://localhost:8000/health"
    },
    {
        "ID": "PH-03",
        "Tipo": "Humo",
        "Nombre del Escenario": "Ejecución de un flujo de captura pública básico",
        "Datos de Entrada": "URL sin credenciales (https://frontmind-frontend.onrender.com).",
        "Entorno": "BrowserContext Playwright instanciado, endpoint /api/analyze.",
        "Condiciones Iniciales": "CORS configurado, Frontend y Backend operativos.",
        "Resultados Esperados": "No excepciones fatales, retorna captura generada y datos de estructura (DOM).",
        "Comando de Ejecución": "Prueba manual desde la UI: ingresar URL y click en Evaluar."
    }
]

df = pd.DataFrame(data)
df.to_excel("Plan_de_Pruebas_FrontMind_AI.xlsx", index=False)
print("Archivo Plan_de_Pruebas_FrontMind_AI.xlsx generado correctamente.")
