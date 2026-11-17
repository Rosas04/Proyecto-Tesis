from datetime import datetime

from services.iso_framework import (
    CHARACTERISTICS,
    SEVERITY_GRADES,
    compliance_of,
    decision_criterion,
    evaluation_restrictions,
    evaluation_scope,
    grade_from_compliance,
    normalize_selection,
)


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
            
            dimension_values: dict[str, list] = {}

            for eval_item in evaluation_data:
                # the item might be the direct result from ISOEvaluationAgent
                inner_eval = eval_item.get("evaluation", eval_item)
                score = inner_eval.get("global_score", 0)
                findings = inner_eval.get("findings", [])

                # Cada característica se promedia sólo entre las interfaces donde se evaluó
                for k, v in (inner_eval.get("scores") or {}).items():
                    if isinstance(v, (int, float)):
                        dimension_values.setdefault(k, []).append(v)

                total_score += score
                total_findings += len(findings)
                name = eval_item.get("name", inner_eval.get("name", "Desconocida"))
                all_findings.extend({**f, "interface": name} for f in findings)

                if score > best_score:
                    best_score = score
                    best_iface = name
                if score < worst_score:
                    worst_score = score
                    worst_iface = name

            avg_score = round(total_score / total_interfaces) if total_interfaces > 0 else 0
            avg_scores = {k: round(sum(v) / len(v)) for k, v in dimension_values.items()}
            quality_level = decision_criterion(avg_score)["category"]

            severity_summary = self.build_severity_summary(all_findings)
            dimension_summary = self.build_dimension_summary(all_findings)
            main_recommendations = self.build_recommendations(all_findings)

            return {
                "agent": "ReportAgent",
                "status": "completed",
                "standard": "ISO/IEC 25010:2023",
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
                "scores": avg_scores,
                "findings": all_findings,
                "main_recommendations": main_recommendations,
                "technical_conclusion": self.build_conclusion(
                    avg_score,
                    total_findings,
                    severity_summary,
                ),
                **self.build_normative_section(
                    avg_score,
                    all_findings,
                    [e.get("evaluation", e) for e in evaluation_data],
                ),
            }
        else:
            # Single evaluation (acepta también el envoltorio de ISOEvaluationAgent)
            evaluation = evaluation_data
            if isinstance(evaluation, dict) and isinstance(evaluation.get("evaluation"), dict):
                evaluation = evaluation["evaluation"]
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
                "standard": "ISO/IEC 25010:2023",
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
                **self.build_normative_section(global_score, findings, [evaluation]),
                "technical_conclusion": self.build_conclusion(
                    global_score,
                    total_findings,
                    severity_summary,
                ),
            }

    # ── Sección normativa (ISO/IEC 25010) ───────────────────────────────────────

    def build_normative_section(self, global_score, findings, evaluations):
        evaluations = [e for e in evaluations if isinstance(e, dict)]
        union: list[str] = []
        for e in evaluations:
            for key in e.get("evaluated_characteristics") or []:
                if key not in union:
                    union.append(key)
        selected = normalize_selection(union or None)
        has_runtime = any(e.get("evidence_received") or e.get("runtime_metrics") for e in evaluations)
        evaluated = {k for e in evaluations for k in (e.get("scores") or {})}
        return {
            "quality_decision": decision_criterion(global_score),
            "severity_grade_summary": self.build_severity_grade_summary(findings),
            "metrics": self.aggregate_metrics(evaluations),
            "evaluated_characteristics": selected,
            "characteristic_labels": {k: CHARACTERISTICS[k] for k in selected},
            "not_evaluated": [k for k in selected if k not in evaluated],
            "evaluation_scope": evaluation_scope(selected),
            "restrictions": evaluation_restrictions(has_runtime),
        }

    def build_severity_grade_summary(self, findings):
        summary = {f"{g} - {info['label']}": 0 for g, info in SEVERITY_GRADES.items() if g > 0}
        for finding in findings:
            grade = finding.get("severity_grade")
            if grade in SEVERITY_GRADES and grade > 0:
                summary[f"{grade} - {SEVERITY_GRADES[grade]['label']}"] += 1
        return summary

    def aggregate_metrics(self, evaluations):
        """
        Consolida las métricas de varias interfaces:
          - proporciones y binarias → X = ΣA / ΣB (sobre el total del sistema)
          - conteos                 → suma de ocurrencias
          - valores máximos         → promedio de las interfaces medidas
        """
        merged: dict[str, dict] = {}
        for evaluation in evaluations:
            for metric in evaluation.get("metrics") or []:
                entry = merged.setdefault(metric["id"], {**metric, "_A": 0, "_B": 0, "_values": [], "interfaces": 0})
                if metric.get("X") is None:
                    continue
                entry["interfaces"] += 1
                if metric.get("kind") == "ratio":
                    entry["_A"] += metric.get("A") or 0
                    entry["_B"] += metric.get("B") or 0
                elif metric.get("kind") == "binary":
                    entry["_A"] += metric["X"]
                    entry["_B"] += 1
                else:
                    entry["_values"].append(metric["X"])

        result = []
        for entry in merged.values():
            a, b, values = entry.pop("_A"), entry.pop("_B"), entry.pop("_values")
            kind, target = entry.get("kind"), entry.get("target_value") or 1
            if not entry["interfaces"]:
                result.append(entry)
                continue
            if kind in ("ratio", "binary"):
                x = round(a / b, 3) if b else None
                if kind == "binary":
                    entry["formula"] = "X = interfaces que cumplen / interfaces medidas"
                entry.update({"A": a, "B": b, "X": x})
                c = compliance_of("ratio", x, target if kind == "ratio" else 1.0)
            elif kind == "count":
                x = sum(values)
                entry["X"] = x
                c = compliance_of("count", x, 0)
            else:
                x = round(sum(values) / len(values), 3)
                entry["X"] = x
                c = compliance_of("max", x, target)
            entry.update({
                "compliance": round(c, 3) if c is not None else None,
                "meets": (c >= 0.999) if c is not None else None,
                "severity_grade": grade_from_compliance(c),
                "status": "medido" if entry.get("scored", True) else "informativo",
            })
            result.append(entry)
        return result

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
                "significativa su funcionalidad, seguridad, compatibilidad ni capacidad de interacción."
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
                "la interacción, la seguridad y la fiabilidad de la interfaz."
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