from services.iso_service import evaluate_iso_25010


class ISOEvaluationAgent:
    def run(self, html: str, runtime_metrics: dict | None = None, characteristics: list | None = None,
            evidence: dict | None = None, expected_functions: list | None = None):
        evaluation = evaluate_iso_25010(
            html,
            runtime_metrics=runtime_metrics,
            characteristics=characteristics,
            evidence=evidence,
            expected_functions=expected_functions,
        )

        return {
            "agent": "ISOEvaluationAgent",
            "status": "completed",
            "standard": "ISO/IEC 25010:2023",
            "scope": "Frontend",
            "evaluation": evaluation,
        }
