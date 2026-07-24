import pytest
from services.iso_service import (
    clamp,
    parse_hex_color,
    get_contrast_ratio,
    evaluate_iso_25010
)

def test_clamp_limits_values():
    """Test ST-ISO-01: Validación de clamp()"""
    assert clamp(-0.5) == 0
    assert clamp(50) == 50
    assert clamp(150) == 100

def test_parse_hex_color():
    """Test ST-ISO-02: Validación de parse_hex_color()"""
    # Test valid hex colors
    assert parse_hex_color("#fff") == (255, 255, 255)
    assert parse_hex_color("#000000") == (0, 0, 0)
    assert parse_hex_color("#ff0000") == (255, 0, 0)
    
    # Test named colors
    assert parse_hex_color("red") == (255, 0, 0)
    
    # Test invalid hex
    assert parse_hex_color("#invalid") is None

def test_get_contrast_ratio():
    """Test ST-ISO-03: Validación de get_contrast_ratio()"""
    # White to black should be exactly 21.0
    assert round(get_contrast_ratio("#ffffff", "#000000"), 1) == 21.0
    
    # Same color should be 1.0
    assert round(get_contrast_ratio("#ffffff", "#ffffff"), 1) == 1.0

def test_evaluate_iso_25010_empty_html():
    """Test ST-ISO-04: Validación de evaluate_iso_25010() con HTML vacío o incompleto."""
    # Test completely empty HTML
    empty_result = evaluate_iso_25010("")
    assert empty_result["global_score"] == 0
    assert "strict_mode" in empty_result
    assert any("insuficiente para realizar una evaluaci" in f["finding"] for f in empty_result["findings"])
    
    # Test HTML without main
    html_without_main = "<html><body><h1>Title</h1><p>This is a long enough paragraph to bypass the length check</p></body></html>"
    no_main_result = evaluate_iso_25010(html_without_main)
    assert any("etiqueta <main>" in f["finding"] for f in no_main_result["findings"])
