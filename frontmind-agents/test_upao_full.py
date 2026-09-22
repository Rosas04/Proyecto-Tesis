import logging
import json
from agents.capture_agent import CaptureAgent
from agents.iso_evaluation_agent import ISOEvaluationAgent

logging.basicConfig(level=logging.INFO)

def main():
    print("Iniciando captura COMPLETA con autenticación para: UPAO")
    agent = CaptureAgent()
    auth_config = {
        "mode": "form",
        "login_url": "https://upao.instructure.com/",
        "username": "000247856",
        "password": "302004Jk",
        "username_selector": "input[name='id_usuario']",
        "password_selector": "input[name='nip']",
        "submit_selector": "input[name='btn_valida']",
        "success_url_pattern": "upao\.instructure\.com"
    }
    
    try:
        # max_pages alto para obtener "todas las interfaces correspondientes"
        result = agent.run(url="https://upao.instructure.com/", auth=auth_config, max_pages=30)
        routes_discovered = result.get("routes_discovered", 0)
        interfaces = result.get("interfaces", [])
        
        print(f"Success! Routes discovered: {routes_discovered}")
        print(f"Interfaces capturadas: {len(interfaces)}")
        
        with open("resultado_upao_full.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Capturas guardadas en resultado_upao_full.json")
        
        # Flujo completo: Evaluación ISO
        if interfaces:
            print("Realizando evaluación ISO sobre la primera interfaz extraída...")
            iso_agent = ISOEvaluationAgent()
            html_to_eval = interfaces[0].get("html_content", "")
            if html_to_eval:
                eval_res = iso_agent.run(html_to_eval)
                with open("resultado_iso_upao.json", "w", encoding="utf-8") as f:
                    json.dump(eval_res, f, indent=2, ensure_ascii=False)
                print(f"Evaluación finalizada. Puntaje Global: {eval_res.get('global_score', 'N/A')}")
            else:
                print("No se extrajo HTML de la primera interfaz.")
        else:
            print("No se pudo extraer ninguna interfaz tras el login.")
            
    except Exception as e:
        print("Error durante el flujo:", e)

if __name__ == "__main__":
    main()
