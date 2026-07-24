import pytest
from unittest.mock import patch, MagicMock
from agents.capture_agent import CaptureAgent
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

@patch("agents.capture_agent.take_screenshots")
def test_run_capture_flow_fallback(mock_take_screenshots):
    """Test AG-CAP-01: Ejecuta el pipeline completo y ante un fallo de red dispara el mecanismo de fallback de manera controlada."""
    agent = CaptureAgent()
    
    # Simulate a network/playwright timeout exception during the screenshot/auth process
    mock_take_screenshots.side_effect = PlaywrightTimeoutError("Navigation timeout exceeded")
    
    # Run the agent
    result = agent.run("https://example.com", auth={"mode": "form", "username": "test"})
    
    # Verify the fallback mechanism was triggered gracefully
    assert result["agent"] == "CaptureAgent"
    assert result["status"] == "error"
    assert "Navigation timeout exceeded" in result["message"]
    assert result["total_interfaces"] == 0
    assert result["total_captures"] == 0
