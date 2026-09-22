import os
import time
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

@tool
def autenticar_sistema(task_id: str, url_login: str, usuario: str, contrasena: str, user_sel: str = "input[type='email'], input[name='username']", pass_sel: str = "input[type='password']", submit_sel: str = "button[type='submit'], input[type='submit']") -> str:
    """
    Inicia sesión en el sistema objetivo y guarda el estado de la sesión (cookies y tokens).
    Úsala AL INICIO del proceso si el archivo de sesión no existe o expiró.
    """
    session_file = os.path.join(SESSION_DIR, f"{task_id}_state.json")
    
    try:
        with sync_playwright() as p:
            # Ejecutar headless=True para producción
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url_login)
            page.fill(user_sel, usuario)
            page.fill(pass_sel, contrasena)
            page.click(submit_sel)

            # Esperar estabilización de red para asegurar redirección
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # Guardar contexto
            context.storage_state(path=session_file)
            browser.close()
            
            return f"🔒 Autenticación exitosa. Estado guardado en {session_file}"
    except Exception as e:
        return f"❌ Error durante la autenticación: {str(e)}"
