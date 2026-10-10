"""Operacionalización de ISO/IEC 25010 y proceso ISO/IEC 25040."""
import pytest

from agents.iso_evaluation_agent import ISOEvaluationAgent
from agents.report_agent import ReportAgent
from services.iso_framework import (
    QUALITY_MODEL,
    decision_criterion,
    grade_from_compliance,
    severity_grade,
)
from services.iso_service import evaluate_iso_25010

HTML = (
    "<!doctype html><html lang='es'><head><meta name='viewport' content='width=device-width'>"
    "<title>t</title></head><body><nav><a href='/'>Inicio</a></nav><main><h1>Hola</h1>"
    "<img src='a.png' alt='a'><img src='b.png'>"
    "<form><label for='e'>Correo</label><input id='e' type='email' required><input name='n'>"
    "<button>Enviar</button></form><div role='alert'></div></main>"
    "<script>function f(a){if(a&&a>1){for(let i=0;i<a;i++){}}return a?1:0}</script></body></html>"
)


@pytest.mark.parametrize("score, category", [
    (100, "Alta calidad"), (90, "Alta calidad"), (89, "Buena calidad"), (61, "Buena calidad"),
    (60, "Regular calidad"), (21, "Regular calidad"), (20, "Mala calidad"), (0, "Mala calidad"),
])
def test_decision_criterion_iso25040(score, category):
    result = decision_criterion(score)
    assert result["category"] == category
    assert result["score_10"] == round(score / 10, 1)


@pytest.mark.parametrize("ratio, grade", [
    (1.0, 0), (0.9, 0), (0.89, 1), (0.51, 1), (0.5, 2), (0.11, 2), (0.1, 3), (0.01, 3), (0.0, 4),
])
def test_severity_scale_from_compliance(ratio, grade):
    assert grade_from_compliance(ratio) == grade


def test_qualitative_severity_maps_to_iso_grades():
    assert severity_grade("Crítica") == {"grade": 4, "label": "Catastrófico"}
    assert severity_grade("Alta")["label"] == "Mayor"
    assert severity_grade("Media")["label"] == "Menor"
    assert severity_grade("Baja")["label"] == "Cosmético"


def test_ratio_metrics_follow_x_equals_a_over_b():
    metrics = {m["id"]: m for m in evaluate_iso_25010(HTML)["metrics"]}
    alt = metrics["ACC-01"]
    assert (alt["A"], alt["B"], alt["X"]) == (1, 2, 0.5)
    labeled = metrics["ACC-02"]
    assert (labeled["A"], labeled["B"]) == (1, 2)
    assert metrics["MS4M1"]["X"] is not None and metrics["MS4M1"]["meets"] is True


def test_runtime_metrics_are_reported_and_penalize_only_when_measured():
    static = evaluate_iso_25010(HTML)
    efi_static = {m["id"]: m for m in static["metrics"]}["EFI-02"]
    assert efi_static["status"] == "no medido" and efi_static["X"] is None

    slow = evaluate_iso_25010(HTML, runtime_metrics={"lcp_ms": 5200, "ttfb_ms": 2000})
    assert slow["scores"]["eficiencia_desempeno"] < static["scores"]["eficiencia_desempeno"]
    assert any("LCP medido" in f["finding"] for f in slow["findings"])


def test_every_finding_has_iso_severity_grade():
    result = evaluate_iso_25010(HTML)
    assert all("severity_grade" in f and "severity_grade_label" in f for f in result["findings"])


def test_characteristic_subset_limits_global_score():
    result = evaluate_iso_25010(HTML, characteristics=["accesibilidad"])
    assert list(result["scores"]) == ["accesibilidad"]
    assert result["global_score"] == result["scores"]["accesibilidad"]
    assert result["evaluated_characteristics"] == ["accesibilidad"]


def test_scope_declares_non_automatable_attributes():
    manual = [i["sub"] for i in QUALITY_MODEL if i["automation"] == "no automatizable"]
    assert "Capacidad de aprendizaje" in manual
    assert "Exactitud funcional" in manual
    scope = evaluate_iso_25010(HTML)["evaluation_scope"]
    assert scope["coverage"]["no_automatizable"] >= 1
    assert any(o["characteristic"].startswith("Calidad en uso") for o in scope["out_of_scope"])


def test_restrictions_follow_iso25040():
    restrictions = evaluate_iso_25010(HTML)["restrictions"]
    types = {r["type"] for r in restrictions}
    assert {"Herramientas y metodología", "Entorno de prueba", "Tiempo y recursos"} <= types


def test_report_consolidates_metrics_as_sum_a_over_sum_b():
    agent = ISOEvaluationAgent()
    e1 = agent.run("<html lang='es'><body><main><h1>A</h1><img src='x'></main></body></html>")
    e2 = agent.run("<html lang='es'><body><main><h1>B</h1><img src='y' alt='y'><img src='z' alt='z'></main></body></html>")
    report = ReportAgent().run({"evaluation": [e1, e2]})
    alt = {m["id"]: m for m in report["metrics"]}["ACC-01"]
    assert (alt["A"], alt["B"]) == (2, 3)
    assert report["iso25040"]["score_10"] == round(report["summary"]["global_score"] / 10, 1)


def test_report_accepts_wrapped_single_evaluation():
    wrapped = ISOEvaluationAgent().run(HTML)
    report = ReportAgent().run({"evaluation": wrapped})
    assert report["summary"]["global_score"] == wrapped["evaluation"]["global_score"]
