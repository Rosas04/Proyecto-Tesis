import pytest
from agents.report_agent import ReportAgent

def test_build_severity_summary():
    """Test AG-REP-01: Agrupa y cuenta correctamente las severidades."""
    agent = ReportAgent()
    
    findings = [
        {"severity": "Crítica"},
        {"severity": "Crítica"},
        {"severity": "Alta"},
        {"severity": "Media"},
        {"severity": "Baja"},
        {"severity": "Baja"},
        {"severity": "Baja"},
        # A finding without severity should default to "Media" according to code
        {},
        {"severity": "Desconocida"}
    ]
    
    summary = agent.build_severity_summary(findings)
    
    assert summary["Crítica"] == 2
    assert summary["Alta"] == 1
    assert summary["Media"] == 2  # 1 explicit + 1 default
    assert summary["Baja"] == 3
    assert summary["Desconocida"] == 1

def test_build_conclusion():
    """Test AG-REP-02: Genera una conclusión correcta si los scores superan el umbral mínimo definido."""
    agent = ReportAgent()
    
    # Test "Aprobado" / Excelente case
    # global_score >= 90 and total_findings <= 3
    severity_summary = {"Crítica": 0, "Alta": 0, "Media": 1, "Baja": 2}
    conclusion = agent.build_conclusion(
        global_score=95,
        total_findings=3,
        severity_summary=severity_summary
    )
    
    # The actual text from report_agent.py
    assert "nivel de calidad excelente" in conclusion
    assert "no comprometen de forma significativa" in conclusion
