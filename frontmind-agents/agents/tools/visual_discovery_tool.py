import os
import json
from typing import List
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

SESSION_DIR = "sessions"

@tool
def rastrear_interfaces_visualmente(task_id: str, url_inicial: str, max_links: int = 5) -> str:
    """
    Simula a un humano navegando por la aplicación web para descubrir rutas internas.
    Inyecta el estado de sesión previamente guardado para evitar el login.
    Filtra automáticamente botones destructivos (logout, delete, etc.).
    """
    session_file = os.path.join(SESSION_DIR, f"{task_id}_state.json")
    
    if not os.path.exists(session_file):
        return "❌ Error: No hay sesión activa. Llama a 'autenticar_sistema' primero."

    try:
        discovered_urls = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=session_file)
            page = context.new_page()

            page.goto(url_inicial, wait_until="networkidle")
            discovered_urls.add(page.url)

            # Extraemos todos los enlaces iterables como lo haría un humano mirando el DOM visual
            links = page.locator("a, button[role='link']").all()
            
            # Palabras clave prohibidas (Regla 4.4 de AGENTS.md)
            forbidden_terms = ["logout", "signout", "logoff", "cerrar-sesion", "delete", "remove", "destroy", "eliminar"]

            for link in links:
                if len(discovered_urls) >= max_links:
                    break
                    
                href = link.get_attribute("href")
                text = link.text_content() or ""
                
                # Filtrar destructivos
                is_forbidden = any(term in href.lower() or term in text.lower() for term in forbidden_terms if href)
                
                if href and href.startswith("/") and not is_forbidden:
                    full_url = f"{url_inicial.rstrip('/')}{href}"
                    discovered_urls.add(full_url)
                    
            browser.close()
            
            # Retornar en JSON para que LangChain lo entienda
            return json.dumps({
                "status": "success",
                "message": "Rastreo visual simulado completado.",
                "rutas_descubiertas": list(discovered_urls)
            })
            
    except Exception as e:
        return f"❌ Error durante el rastreo visual: {str(e)}"
