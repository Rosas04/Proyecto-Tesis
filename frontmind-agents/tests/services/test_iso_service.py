import pytest
from services.iso_service import clamp, parse_hex_color, get_contrast_ratio, evaluate_iso_25010

def test_clamp_st_iso_01():
    # Descripción del escenario: ST-ISO-01 Lógica / Frontera
    # Comportamiento esperado: Limita valores correctamente fuera de rango [0, 100].
    
    assert clamp(50) == 50
    assert clamp(-10) == 0
    assert clamp(150) == 100
    assert clamp(0) == 0
    assert clamp(100) == 100

def test_parse_hex_color_st_iso_02():
    # Descripción del escenario: ST-ISO-02 Lógica / Datos
    # Comportamiento esperado: Transforma formatos Hex (3 y 6 chars) a tuplas RGB correctas.
    
    # 6 characters
    assert parse_hex_color("#FFFFFF") == (255, 255, 255)
    assert parse_hex_color("#000000") == (0, 0, 0)
    assert parse_hex_color("#ff0000") == (255, 0, 0)
    
    # 3 characters
    assert parse_hex_color("#FFF") == (255, 255, 255)
    assert parse_hex_color("#000") == (0, 0, 0)
    assert parse_hex_color("#f00") == (255, 0, 0)
    
    # Named colors
    assert parse_hex_color("white") == (255, 255, 255)
    assert parse_hex_color("red") == (255, 0, 0)
    
    # Invalid
    assert parse_hex_color("#ZZZ") is None

def test_get_contrast_ratio_st_iso_03():
    # Descripción del escenario: ST-ISO-03 Lógica / Cálculo
    # Comportamiento esperado: Calcula correctamente el ratio de contraste relativo (ej. 21:1 para Blanco/Negro).
    
    # White vs Black should be 21.0
    ratio_wb = get_contrast_ratio("#FFFFFF", "#000000")
    assert round(ratio_wb, 2) == 21.0
    
    # Same colors should be 1.0
    ratio_ww = get_contrast_ratio("#FFFFFF", "#FFFFFF")
    assert round(ratio_ww, 2) == 1.0
    
    # Invalid colors should return None
    assert get_contrast_ratio("invalid", "#000000") is None

def test_evaluate_iso_25010_empty_html_st_iso_04():
    # Descripción del escenario: ST-ISO-04 Estructura HTML
    # Comportamiento esperado: Retorna score de 0 o advertencia si el HTML está vacío o no contiene <main>.
    
    # Caso 1: HTML vacío
    empty_html_result = evaluate_iso_25010("")
    assert empty_html_result["global_score"] == 0
    assert empty_html_result["quality_level"] == "Crítico"
    assert len(empty_html_result["findings"]) == 1
    assert empty_html_result["findings"][0]["finding"] == "El contenido HTML recibido es insuficiente para realizar una evaluación técnica."
    
    # Caso 2: HTML válido pero sin <main>
    html_without_main = "<html><body><h1>Hello World</h1><nav>Menu</nav></body></html>"
    # Añadiendo padding para sobrepasar la validación len(html.strip()) < 50
    html_without_main += " " * 50
    result_without_main = evaluate_iso_25010(html_without_main)
    
    # Debe tener una penalización por no tener <main>
    findings = result_without_main["findings"]
    has_main_finding = any(f["finding"] == "No se detectó la etiqueta <main> para delimitar el contenido principal." for f in findings)
    assert has_main_finding is True
