import json
from agents.iso_evaluation_agent import ISOEvaluationAgent
from agents.capture_agent import CaptureAgent

def main():
    print("Capturando la URL con mayor tiempo de espera...")
    capture_agent = CaptureAgent()
    capture_result = capture_agent.run(url="https://mvp-mobile.vercel.app", max_pages=1)
    
    html = ""
    if capture_result.get("interfaces"):
        html = capture_result["interfaces"][0].get("html_content", "")
    
    if not html:
        print("No se pudo obtener el HTML de la página.")
        return

    print(f"HTML capturado, longitud: {len(html)} caracteres. Iniciando evaluación ISO/IEC 25010...")
    iso_agent = ISOEvaluationAgent()
    evaluation = iso_agent.run(html)
    
    with open("resultado_iso_mvp.json", "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)
        
    print(f"Evaluación finalizada. Puntaje Global: {evaluation.get('overall_score', 'N/A')}")
    print("Resultados guardados en resultado_iso_mvp.json")

if __name__ == "__main__":
    main()
