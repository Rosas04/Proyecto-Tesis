import pytest
import json
from unittest.mock import patch, mock_open
from services.history_service import load_history

@patch("services.history_service.open", new_callable=mock_open, read_data="corrupt{json[")
@patch("services.history_service._ensure_history_file")
def test_load_history_corrupted(mock_ensure, mock_file):
    """Test ST-HIST-01: Validación de load_history() ante un archivo JSON corrupto."""
    # La función debe capturar json.JSONDecodeError y retornar una lista vacía
    result = load_history()
    
    assert result == []
    mock_file.assert_called_once()
