import json
import logging
import sys
from agents.capture_agent import CaptureAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', stream=sys.stdout)

def main():
    print("Iniciando captura con autenticación para: FrontMind")
    agent = CaptureAgent()
    auth_config = {
        "mode": "form",
        "login_url": "https://frontmind-frontend.onrender.com/login",
        "username": "lrosasm@upao.edu.pe",
        "password": "302004*",
    }
    
    result = agent.run(url="https://frontmind-frontend.onrender.com/", auth=auth_config, max_pages=5)
    
    with open("resultado_frontmind.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Status: {result.get('status')}")
    print(f"Total captures: {result.get('total_captures')}")
    interfaces = result.get('interfaces', [])
    print(f"Interfaces: {len(interfaces)}")
    for i in interfaces:
        print(f"- {i['route']}")
        
if __name__ == "__main__":
    main()
