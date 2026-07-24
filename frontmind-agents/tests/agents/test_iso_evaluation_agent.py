import pytest
from unittest.mock import patch
from agents.iso_evaluation_agent import ISOEvaluationAgent

@patch("agents.iso_evaluation_agent.evaluate_iso_25010")
def test_orchestrate_evaluation(mock_evaluate_iso_25010):
    """Test AG-ISO-01: Ejecuta la lógica del agente llamando al servicio con el payload adecuado."""
    # Setup mock return
    mock_evaluation_result = {
        "global_score": 85,
        "quality_level": "Alto",
        "findings": [{"severity": "Media", "recommendation": "Fix contrast"}]
    }
    mock_evaluate_iso_25010.return_value = mock_evaluation_result
    
    agent = ISOEvaluationAgent()
    
    # Run the agent
    html_payload = "<html><body><h1>Test</h1></body></html>"
    result = agent.run(html_payload)
    
    # Assert service was called correctly
    mock_evaluate_iso_25010.assert_called_once_with(html_payload)
    
    # Assert result structure
    assert result["agent"] == "ISOEvaluationAgent"
    assert result["status"] == "completed"
    assert result["standard"] == "ISO/IEC 25010"
    assert result["evaluation"] == mock_evaluation_result
