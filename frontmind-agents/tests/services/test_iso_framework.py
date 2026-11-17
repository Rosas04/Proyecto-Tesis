"""Operacionalización de ISO/IEC 25010:2023 (modelo, escalas y consolidación)."""
import pytest

from agents.iso_evaluation_agent import ISOEvaluationAgent
from agents.report_agent import ReportAgent
from services.iso_framework import (
    CORE_CHARACTERISTICS,
    QUALITY_MODEL,
    compliance_of,
    decision_criterion,
    grade_from_compliance,
    normalize_selection,
    severity_grade,
)
from services.iso_service import evaluate_iso_25010

HTML = (
    "<!doctype html><html lang='es'><head><meta name='viewport' content='width=device-width'>"
    "<title>t</title></head><body><nav><a href='/'>Inicio</a></nav><main><h1>Hola</h1>"
    "<img src='a.png' alt='a'><img src='b.png'>"
    "<form><label for='e'>Correo</label><input id='e' type='email' required><input name='n'>"
    "<button>Enviar</button></form><div role='alert'></div></main></body></html>"
)

EVIDENCE = {
    "navigation": {"status": 200, "final_url": "https://x.test/", "https": True},
    "headers": {"csp": "default-src 'self'; frame-ancestors 'self'", "hsts": "max-age=31536000",
                "x_frame_options": "", "x_content_type_options": "nosniff", "referrer_policy": "no-referrer"},
    "tls": {"valid": True}, "http_redirects_to_https": True,
    "cookies": {"total": 2, "secure": 2, "insecure_samples": []},
    "page": {"password_forms": {"total": 0, "insecure": 0}, "images": {"total": 2, "broken": 0},
             "storage_credentials": {"count": 0, "keys": []},
             "third_party_scripts": {"total": 0, "with_sri": 0}, "globals": {"count": 3}, "manifest": False,
             "meta_csp": ""},
    "links": {"checked": 4, "broken": 0},
    "layout": {"desktop": {"overflow": False, "height": 900}, "tablet": {"overflow": False},
               "mobile": {"overflow": False, "targets": 10, "small_targets": 0, "text_elements": 20, "small_text": 0},
               "reflow_320": {"overflow": False}},
    "requests": {"total": 20, "failed": 0, "api_total": 2, "api_failed": 0},
    "mixed_content": {"count": 0}, "js_errors": {"count": 0}, "console_errors": {"count": 0},
    "cross_browser": {"chromium": {"available": True, "loaded": True, "js_errors": 0, "height": 900},
                      "firefox": {"available": True, "loaded": True, "js_errors": 0, "height": 950},
                      "webkit": {"available": True, "loaded": True, "js_errors": 0, "height": 880}},
}


@pytest.mark.parametrize("score, category", [
    (100, "Alta calidad"), (90, "Alta calidad"), (89, "Buena calidad"), (61, "Buena calidad"),
    (60, "Regular calidad"), (21, "Regular calidad"), (20, "Mala calidad"), (0, "Mala calidad"),
])
def test_decision_criterion(score, category):
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


@pytest.mark.parametrize("kind, x, target, expected", [
    ("ratio", 0.45, 0.9, 0.5), ("ratio", 1.0, 0.9, 1.0), ("binary", 0, 1, 0.0),
    ("count", 3, 0, 0.25), ("max", 5000, 2500, 0.5), ("max", 100, 2500, 1.0),
])
def test_compliance_functions(kind, x, target, expected):
    assert compliance_of(kind, x, target) == pytest.approx(expected)


def test_default_selection_excludes_maintainability_and_efficiency():
    assert normalize_selection(None) == CORE_CHARACTERISTICS
    assert "mantenibilidad" not in CORE_CHARACTERISTICS
    assert "eficiencia_desempeno" not in CORE_CHARACTERISTICS
    assert normalize_selection(["usabilidad", "portabilidad"]) == ["capacidad_interaccion", "flexibilidad"]
    assert normalize_selection(["mantenibilidad"]) == CORE_CHARACTERISTICS


def test_efficiency_is_scored_only_on_request():
    rt = {"lcp_ms": 5200}
    assert "eficiencia_desempeno" not in evaluate_iso_25010(HTML, rt)["scores"]
    chosen = evaluate_iso_25010(HTML, rt, characteristics=CORE_CHARACTERISTICS + ["eficiencia_desempeno"])
    assert chosen["scores"]["eficiencia_desempeno"] == 48   # 2500 / 5200


def test_ratio_metrics_follow_x_equals_a_over_b():
    metrics = {m["id"]: m for m in evaluate_iso_25010(HTML)["metrics"]}
    alt = metrics["CI-01"]
    assert (alt["A"], alt["B"], alt["X"]) == (1, 2, 0.5)
    labeled = metrics["CI-02"]
    assert (labeled["A"], labeled["B"]) == (1, 2)


def test_scores_derive_from_metrics_and_every_finding_traces_to_one():
    result = evaluate_iso_25010(HTML, evidence=EVIDENCE)
    ids = {m["id"] for m in result["metrics"] if m["meets"] is False and m["scored"]}
    assert {f["metric_id"] for f in result["findings"]} == ids
    assert all("severity_grade" in f and "severity_grade_label" in f for f in result["findings"])
    assert set(result["scores"]) == set(CORE_CHARACTERISTICS)


def test_characteristics_without_evidence_are_not_evaluated():
    result = evaluate_iso_25010(HTML)
    assert set(result["not_evaluated"]) == {"adecuacion_funcional", "compatibilidad", "seguridad", "fiabilidad"}
    assert set(result["scores"]) == {"capacidad_interaccion", "flexibilidad"}


def test_characteristic_subset_limits_global_score():
    result = evaluate_iso_25010(HTML, characteristics=["capacidad_interaccion"])
    assert list(result["scores"]) == ["capacidad_interaccion"]
    assert result["global_score"] == result["scores"]["capacidad_interaccion"]


def test_scope_declares_non_automatable_attributes_and_exclusions():
    manual = [i["sub"] for i in QUALITY_MODEL if i["automation"] == "no automatizable"]
    assert "Aprendibilidad" in manual and "Recuperabilidad" in manual
    scope = evaluate_iso_25010(HTML)["evaluation_scope"]
    out = [o["characteristic"] for o in scope["out_of_scope"]]
    assert "Mantenibilidad" in out
    assert any(o.startswith("Eficiencia de desempeño") for o in out)


def test_evaluation_conditions_are_declared():
    types = {r["type"] for r in evaluate_iso_25010(HTML)["restrictions"]}
    assert {"Herramientas y metodología", "Entorno de prueba", "Tiempo y recursos"} <= types


def test_report_consolidates_metrics_as_sum_a_over_sum_b():
    agent = ISOEvaluationAgent()
    e1 = agent.run("<html lang='es'><body><main><h1>A</h1><img src='x'></main></body></html>")
    e2 = agent.run("<html lang='es'><body><main><h1>B</h1><img src='y' alt='y'><img src='z' alt='z'></main></body></html>")
    report = ReportAgent().run({"evaluation": [e1, e2]})
    alt = {m["id"]: m for m in report["metrics"]}["CI-01"]
    assert (alt["A"], alt["B"]) == (2, 3)
    assert report["quality_decision"]["score_10"] == round(report["summary"]["global_score"] / 10, 1)


def test_report_averages_each_characteristic_only_where_evaluated():
    agent = ISOEvaluationAgent()
    with_ev = agent.run(HTML, evidence=EVIDENCE)
    static = agent.run(HTML)
    report = ReportAgent().run({"evaluation": [with_ev, static]})
    assert report["scores"]["seguridad"] == with_ev["evaluation"]["scores"]["seguridad"]


def test_report_accepts_wrapped_single_evaluation():
    wrapped = ISOEvaluationAgent().run(HTML)
    report = ReportAgent().run({"evaluation": wrapped})
    assert report["summary"]["global_score"] == wrapped["evaluation"]["global_score"]
