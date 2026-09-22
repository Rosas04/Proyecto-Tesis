import json
from agents.capture_agent import CaptureAgent

def main():
    print("Iniciando captura con autenticación para: https://gen-ova.vercel.app")
    agent = CaptureAgent()
    auth_config = {
        "mode": "form",
        "login_url": "https://gen-ova.vercel.app/login",
        "username": "estudiante@genova.ai",  # From the image we can see 'estudiante@genova.ai' in the input
        "password": "password123", # I'll use a dummy password to see if it fills it
    }
    
    result = agent.run(url="https://gen-ova.vercel.app/", auth=auth_config, max_pages=10)
    
    with open("resultado_genova.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Status: {result.get('status')}")
    print(f"Interfaces: {len(result.get('interfaces', []))}")
        
if __name__ == "__main__":
    main()
