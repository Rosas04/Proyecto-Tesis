from datetime import datetime


class ReportAgent:
    def run(self, data: dict):
        evaluation_data = data.get("evaluation", {})

        if isinstance(evaluation_data, list):
            # Consolidate multiple evaluations
            total_interfaces = len(evaluation_data)
            total_findings = 0
            total_score = 0
            best_iface = "Ninguna"
            worst_iface = "Ninguna"
            best_score = -1
            worst_score = 101
            all_findings = []

            for eval_item in evaluation_data:
                # the item might be the direct result from ISOEvaluationAgent
                inner_eval = eval_item.get("evaluation", eval_item)
                score = inner_eval.get("global_score", 0)
                findings = inner_eval.get("findings", [])

                total_score += score
                total_findings += len(findings)
                all_findings.extend(findings)

                name = eval_item.get("name", inner_eval.get("name", "Desconocida"))

                if score > best_score:
                    best_score = score
                    best_iface = name
                if score < worst_score:
                    worst_score = score
                    worst_iface = name

            avg_score = round(total_score / total_interfaces) if total_interfaces > 0 else 0
            
            # Determine quality level based on avg_score
            if avg_score >= 90:
                quality_level = "Excelente"
            elif avg_score >= 80:
                quality_level = "Alto"
            elif avg_score >= 60:
                quality_level = "Medio"
            elif avg_score >= 40:
                quality_level = "Bajo"
            else:
                quality_level = "Crítico"

            severity_summary = self.build_severity_summary(all_findings)
            dimension_summary = self.build_dimension_summary(all_findings)
            main_recommendations = self.build_recommendations(all_findings)

            return {
                "agent": "ReportAgent",
                "status": "completed",
                "standard": "ISO/IEC 25010",
                "scope": "Frontend (Consolidado)",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "total_interfaces": total_interfaces,
                    "global_score": avg_score,
                    "quality_level": quality_level,
                    "total_findings": total_findings,
                    "best_interface": best_iface,
                    "worst_interface": worst_iface,
                    "severity_summary": severity_summary,
                    "dimension_summary": dimension_summary,
                },
                "scores": {},
                "findings": all_findings,
                "main_recommendations": main_recommendations,
                "technical_conclusion": self.build_conclusion(
                    avg_score,
                    total_findings,
                    severity_summary,
                ),
            }
        else:
            # Single evaluation
            evaluation = evaluation_data
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