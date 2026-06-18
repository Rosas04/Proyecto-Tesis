from datetime import datetime


class ReportAgent:
    def run(self, data: dict):
        evaluation = data.get("evaluation", {})

        global_score = evaluation.get("global_score", 0)
        quality_level = evaluation.get("quality_level", "No calculado")
        scores = evaluation.get("scores", {})
        findings = evaluation.get("findings", [])
        total_findings = evaluation.get("total_findings", len(findings))

        severity_summary = self.build_severity_summary(findings)
        dimension_summary = self.build_dimension_summary(findings)
        main_recommendations = self.build_recommendations(findings)

        return {
            "agent": "ReportAgent",
            "status": "completed",
            "standard": "ISO/IEC 25010",
            "scope": "Frontend",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "global_score": global_score,
                "quality_level": quality_level,
                "total_findings": total_findings,
                "severity_summary": severity_summary,
                "dimension_summary": dimension_summary,
            },
            "scores": scores,
            "findings": findings,
            "main_recommendations": main_recommendations,
            "technical_conclusion": self.build_conclusion(
                global_score,
                total_findings,
                severity_summary,
            ),
        }

    def build_severity_summary(self, findings):
        summary = {
            "Crítica": 0,
            "Alta": 0,
            "Media": 0,
            "Baja": 0,
        }

        for finding in findings:
            severity = finding.get("severity", "Media")

            if severity not in summary:
                summary[severity] = 0

            summary[severity] += 1

        return summary

    def build_dimension_summary(self, findings):
        summary = {}

        for finding in findings:
            dimension = finding.get("dimension", "No especificada")

            if dimension not in summary:
                summary[dimension] = 0

            summary[dimension] += 1

        return summary

    def build_recommendations(self, findings):
        recommendations = []

        for finding in findings:
            recommendation = finding.get("recommendation")

            if recommendation and recommendation not in recommendations:
                recommendations.append(recommendation)

        return recommendations[:10]

    def build_conclusion(self, global_score, total_findings, severity_summary):
        critical = severity_summary.get("Crítica", 0)
        high = severity_summary.get("Alta", 0)

        if global_score >= 90 and total_findings <= 3:
            return (
                "La interfaz frontend presenta un nivel de calidad excelente. "
                "Los hallazgos detectados son mínimos y no comprometen de forma "
                "significativa la eficiencia, accesibilidad o mantenibilidad del artefacto evaluado."
            )

        if global_score >= 80:
            return (
                "La interfaz frontend presenta un nivel de calidad alto. "
                "Se recomienda atender los hallazgos identificados para fortalecer "
                "el cumplimiento de las características de calidad de la norma ISO/IEC 25010."
            )

        if global_score >= 60:
            return (
                "La interfaz frontend presenta un nivel de calidad medio. "
                "Se identificaron deficiencias técnicas que deben corregirse para mejorar "
                "la experiencia del usuario, la accesibilidad y la sostenibilidad del código."
            )

        if global_score >= 40:
            return (
                "La interfaz frontend presenta un nivel de calidad bajo. "
                "La cantidad de hallazgos y su severidad evidencian la necesidad de una "
                "intervención técnica antes de su despliegue en un entorno profesional."
            )

        if critical > 0 or high > 0:
            return (
                "La interfaz frontend presenta un nivel de calidad crítico. "
                "Se detectaron hallazgos de alta severidad que comprometen la calidad técnica "
                "del producto, por lo que se recomienda una revisión integral del frontend."
            )

        return (
            "La interfaz frontend requiere mejoras técnicas importantes para cumplir "
            "con criterios mínimos de calidad establecidos por ISO/IEC 25010."
        )