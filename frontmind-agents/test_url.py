import json
import asyncio
from agents.capture_agent import CaptureAgent

def main():
    agent = CaptureAgent()
    print("Iniciando captura de https://mvp-mobile.vercel.app...")
    result = agent.run(url="https://mvp-mobile.vercel.app", max_pages=10)
    
    with open("resultado_mvp_mobile.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Captura finalizada. Se encontraron {result.get('routes_discovered', 0)} rutas.")
    print("Resultados guardados en resultado_mvp_mobile.json")

if __name__ == "__main__":
    main()
