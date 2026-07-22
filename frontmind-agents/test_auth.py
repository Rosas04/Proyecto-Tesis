import json
from agents.capture_agent import CaptureAgent
from agents.iso_evaluation_agent import ISOEvaluationAgent
from services.screenshot_service import take_screenshots_from_html

def main():
    print("Iniciando captura con autenticación para: https://feedback-web-d776c.web.app/login")
    agent = CaptureAgent()
    auth_config = {
        "mode": "form",
        "login_url": "https://feedback-web-d776c.web.app/login",
        "username": "Liz",
        "password": "123456",
        # Selectores genéricos, si CaptureAgent tiene heurísticas las usará.
        "username_selector": "input[type='text'], input[type='email'], input[name='username']",
        "password_selector": "input[type='password']",
        "submit_selector": "button[type='submit'], button"
    }
    
    result = agent.run(url="https://feedback-web-d776c.web.app/", auth=auth_config, max_pages=10)
    
    with open("resultado_feedback_web.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    routes_discovered = result.get('routes_discovered', 0)
    print(f"Captura finalizada. Se encontraron {routes_discovered} rutas.")
    
    # Evaluate global or all routes
    if routes_discovered > 0:
        iso_agent = ISOEvaluationAgent()
        print("Realizando evaluación ISO sobre la primera interfaz extraída...")
        html_to_eval = result["interfaces"][0].get("html_content", "")
        if html_to_eval:
            eval_res = iso_agent.run(html_to_eval)
            with open("resultado_iso_feedback.json", "w", encoding="utf-8") as f:
                json.dump(eval_res, f, indent=2, ensure_ascii=False)
            print(f"Evaluación finalizada. Puntaje Global: {eval_res.get('global_score', 'N/A')}")
        else:
            print("No se extrajo HTML de la primera interfaz.")
    else:
        print("No se pudo extraer ninguna interfaz tras el login.")
        
if __name__ == "__main__":
    main()
