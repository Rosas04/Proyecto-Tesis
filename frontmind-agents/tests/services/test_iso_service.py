"""Métricas de la evaluación ISO/IEC 25010 por característica."""
import copy

from services.iso_service import evaluate_iso_25010
from tests.services.test_iso_framework import EVIDENCE, HTML


def metric(result, mid):
    return {m["id"]: m for m in result["metrics"]}[mid]


def test_empty_html_is_rejected():
    result = evaluate_iso_25010("")
    assert result["global_score"] == 0
    assert any("insuficiente" in f["finding"] for f in result["findings"])


def test_correct_page_has_no_false_positives():
    """`required`, max-width y un `body{}` global no son defectos."""
    html = HTML.replace("<input name='n'>", "<label for='n'>Nombre</label><input id='n' name='n' required "
                                           "autocomplete='name'>").replace("<img src='b.png'>", "")
    html = html.replace("<title>", "<style>.w{max-width:1200px} body{margin:0}</style><title>")
    result = evaluate_iso_25010(html.replace("type='email' required", "type='email' required autocomplete='email'"),
                                evidence=EVIDENCE)
    assert result["findings"] == []
    assert result["global_score"] == 100


def test_security_detects_insecure_transport_and_login():
    ev = copy.deepcopy(EVIDENCE)
    ev["navigation"]["https"] = False
    ev["headers"] = {k: "" for k in ev["headers"]}
    ev["page"]["password_forms"] = {"total": 1, "insecure": 1}
    ev["page"]["storage_credentials"] = {"count": 1, "keys": ["auth-token"]}
    result = evaluate_iso_25010(HTML, evidence=ev)
    failed = {f["metric_id"] for f in result["findings"]}
    assert {"SE-01", "SE-05", "SE-08", "SE-09", "SE-10", "SE-11"} <= failed
    assert result["scores"]["seguridad"] < 40


def test_reliability_counts_runtime_failures():
    ev = copy.deepcopy(EVIDENCE)
    ev["js_errors"] = {"count": 3, "samples": ["TypeError: x is undefined"]}
    ev["requests"] = {"total": 10, "failed": 5, "api_total": 0, "api_failed": 0}
    result = evaluate_iso_25010(HTML, evidence=ev)
    assert metric(result, "FI-02")["compliance"] == 0.25
    assert metric(result, "FI-04")["X"] == 0.5
    assert result["scores"]["fiabilidad"] < 70


def test_flexibility_uses_measured_overflow_and_reflow():
    ev = copy.deepcopy(EVIDENCE)
    ev["layout"]["mobile"].update({"overflow": True, "scroll_width": 600, "width": 390})
    ev["layout"]["reflow_320"] = {"overflow": True, "scroll_width": 600}
    result = evaluate_iso_25010(HTML, evidence=ev)
    assert metric(result, "FL-02")["X"] == round(2 / 3, 3)
    assert metric(result, "FL-03")["X"] == 0
    assert metric(result, "FL-04")["status"] == "informativo"


def test_compatibility_flags_engine_with_new_errors():
    ev = copy.deepcopy(EVIDENCE)
    ev["cross_browser"]["webkit"].update({"js_errors": 2, "js_error_samples": ["ReferenceError"]})
    result = evaluate_iso_25010(HTML, evidence=ev)
    co02 = metric(result, "CO-02")
    assert (co02["A"], co02["B"]) == (2, 3)
    assert "webkit" in next(f["finding"] for f in result["findings"] if f["metric_id"] == "CO-02")


def test_functional_suitability_with_expected_functions_and_broken_links():
    ev = copy.deepcopy(EVIDENCE)
    ev["links"] = {"checked": 4, "broken": 1, "samples": ["404 · https://x.test/old"]}
    result = evaluate_iso_25010(HTML, evidence=ev, expected_functions=["Enviar", "Correo", "Pagar"])
    assert (metric(result, "AF-01")["A"], metric(result, "AF-01")["B"]) == (2, 3)
    assert metric(result, "AF-04")["A"] == 2      # "Enviar" (botón) y "Correo" (campo etiquetado)
    assert metric(result, "AF-02")["X"] == 0.75


def test_functional_suitability_without_specification_is_not_invented():
    result = evaluate_iso_25010(HTML, evidence=EVIDENCE)
    assert metric(result, "AF-01")["status"].startswith("no evaluado")
    assert metric(result, "AF-02")["status"] == "medido"
