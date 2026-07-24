import pytest
from agents.html_replication_agent import HtmlReplicationAgent

def test_cleanup_html():
    """Test AG-HTML-01: Elimina scripts sospechosos e inyecta correctamente las etiquetas de CSSOM."""
    agent = HtmlReplicationAgent()
    
    html_input = '''
    <html>
        <head>
            <title>Test Page</title>
            <script>alert("malicious!");</script>
            <script src="bad.js"></script>
            <noscript>No scripts allowed</noscript>
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
    </html>
    '''
    
    url = "https://example.com"
    cssom_styles = [".dynamic-style { color: red; }"]
    
    # build_full_html acts as the cleanup_html function according to the current implementation
    result_html = agent.build_full_html(html_input, url, css_cache={}, cssom_styles=cssom_styles)
    
    # Verify scripts are removed
    assert "<script>alert" not in result_html
    assert "bad.js" not in result_html
    assert "<noscript>" not in result_html
    
    # Verify CSSOM is injected
    assert "/* Estilos dinamicos CSSOM #1 */" in result_html
    assert ".dynamic-style { color: red; }" in result_html
