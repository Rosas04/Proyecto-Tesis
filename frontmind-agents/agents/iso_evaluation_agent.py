from services.iso_service import evaluate_iso_25010


class ISOEvaluationAgent:
    def run(self, html: str):
        evaluation = evaluate_iso_25010(html)

        return {
            "agent": "ISOEvaluationAgent",
            "status": "completed",
            "standard": "ISO/IEC 25010",
            "scope": "Frontend",
            "evaluation": evaluation,
        }