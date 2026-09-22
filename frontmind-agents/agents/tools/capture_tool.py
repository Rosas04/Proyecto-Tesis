import os
import json
import time
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

SESSION_DIR = "sessions"
CAPTURES_DIR = "captures"

os.makedirs(CAPTURES_DIR, exist_ok=True)

@tool
def capturar_interfaz(task_id: str, url_interfaz: str, interface_id: str) -> str:
    """
    Toma capturas responsivas (Desktop, Tablet, Mobile) y extrae el HTML de una interfaz específica.
    Usa el contexto de sesión autenticado.
    """
    session_file = os.path.join(SESSION_DIR, f"{task_id}_state.json")
    
    if not os.path.exists(session_file):
        return "❌ Error: No hay sesión activa. Llama a 'autenticar_sistema' primero."

    try:
        results = {
            "interface_id": interface_id,
            "url": url_interfaz,
            "html_length": 0,
            "captures": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=session_file)
            page = context.new_page()

            page.goto(url_interfaz, wait_until="networkidle")
            
            # Esperar a que rendericen SPAs
            time.sleep(1.5)
            
            # Extraer HTML aislado
            html_content = page.content()
            results["html_length"] = len(html_content)
            
            # Guardar el HTML localmente
            html_path = os.path.join(CAPTURES_DIR, f"{task_id}_{interface_id}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Viewports a simular
            viewports = [
                {"device": "desktop", "width": 1920, "height": 1080},
                {"device": "tablet", "width": 768, "height": 1024},
                {"device": "mobile", "width": 375, "height": 812}
            ]

            for vp in viewports:
                page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                time.sleep(0.5) # Esperar a que se re-ajuste el responsive
                
                shot_path = os.path.join(CAPTURES_DIR, f"{task_id}_{interface_id}_{vp['device']}.png")
                page.screenshot(path=shot_path, full_page=True)
                
                results["captures"].append({
                    "device": vp["device"],
                    "path": shot_path
                })
                
            browser.close()
            
            return json.dumps(results)
            
    except Exception as e:
        return f"❌ Error al capturar interfaz {url_interfaz}: {str(e)}"
