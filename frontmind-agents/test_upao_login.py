import logging
import json
from agents.capture_agent import CaptureAgent

logging.basicConfig(level=logging.DEBUG)

def main():
    print("Iniciando captura con autenticación para: UPAO")
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
        result = agent.run(url="https://upao.instructure.com/", auth=auth_config, max_pages=10)
        print("Success! Routes discovered:", result.get("routes_discovered"))
        print("Interfaces:", len(result.get("interfaces", [])))
        with open("resultado_upao.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Guardado en resultado_upao.json")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
