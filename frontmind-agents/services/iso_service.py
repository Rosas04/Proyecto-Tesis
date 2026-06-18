from bs4 import BeautifulSoup
import re


def clamp(value):
    return max(0, min(100, value))


def detect_colors(html):
    hex_colors = re.findall(r"#[0-9a-fA-F]{3,6}", html)
    rgb_colors = re.findall(r"rgb[a]?\([^)]+\)", html)
    named_colors = re.findall(r"(?:color|background-color)\s*:\s*([a-zA-Z]+)", html)
    return list(set(hex_colors + rgb_colors + named_colors))


def get_level(score):
    if score >= 90:
        return "Excelente"
    if score >= 80:
        return "Alto"
    if score >= 60:
        return "Medio"
    if score >= 40:
        return "Bajo"
    return "Crítico"


def evaluate_iso_25010(html: str):
    soup = BeautifulSoup(html or "", "html.parser")

    findings = []
    tips = []

    scores = {
        "adecuacion_funcional": 100,
        "eficiencia_desempeno": 100,
        "usabilidad": 100,
        "accesibilidad": 100,
        "mantenibilidad": 100,
        "compatibilidad": 100,
        "seguridad": 100,
        "portabilidad": 100,
    }

    def add_finding(dimension, subdimension, severity, finding, recommendation, penalties):
        findings.append(
            {
                "dimension": dimension,
                "subdimension": subdimension,
                "severity": severity,
                "finding": finding,
                "recommendation": recommendation,
            }
        )

        for key, value in penalties.items():
            if key in scores:
                scores[key] -= value

    if not html or len(html.strip()) < 50:
        add_finding(
            "Adecuación funcional",
            "Artefacto evaluable",
            "Crítica",
            "El contenido HTML recibido es insuficiente para realizar una evaluación técnica.",
            "Verificar que la interfaz capture o proporcione un HTML completo antes de ejecutar la evaluación.",
            {
                "adecuacion_funcional": 60,
                "eficiencia_desempeno": 40,
                "usabilidad": 40,
                "accesibilidad": 40,
                "mantenibilidad": 40,
                "compatibilidad": 40,
                "portabilidad": 40,
            },
        )

    # ADECUACIÓN FUNCIONAL
    if not soup.find("main"):
        add_finding(
            "Adecuación funcional",
            "Completitud funcional",
            "Alta",
            "No se detectó la etiqueta <main> para delimitar el contenido principal.",
            "Agregar una etiqueta <main> para estructurar el contenido principal de la interfaz.",
            {"adecuacion_funcional": 25, "usabilidad": 10},
        )

    if not soup.find("nav"):
        add_finding(
            "Adecuación funcional",
            "Pertinencia funcional",
            "Media",
            "No se detectó una estructura de navegación principal.",
            "Incorporar una etiqueta <nav> o una estructura equivalente para mejorar la orientación del usuario.",
            {"adecuacion_funcional": 15, "usabilidad": 10},
        )

    h1_tags = soup.find_all("h1")

    if len(h1_tags) == 0:
        add_finding(
            "Adecuación funcional",
            "Comprensibilidad",
            "Alta",
            "No se detectó un encabezado principal <h1>.",
            "Agregar un <h1> claro y único que indique el propósito principal de la interfaz.",
            {"adecuacion_funcional": 20, "usabilidad": 20},
        )

    if len(h1_tags) > 1:
        add_finding(
            "Adecuación funcional",
            "Jerarquía de información",
            "Media",
            f"Se detectaron {len(h1_tags)} encabezados <h1> en la interfaz.",
            "Mantener un solo encabezado <h1> principal y organizar el resto con <h2>, <h3> y niveles posteriores.",
            {"adecuacion_funcional": 10, "usabilidad": 10},
        )

    interactive = soup.find_all(["button", "a", "input", "select", "textarea"])

    if len(interactive) == 0:
        add_finding(
            "Adecuación funcional",
            "Pertinencia funcional",
            "Alta",
            "No se detectaron elementos interactivos en la interfaz.",
            "Agregar controles interactivos cuando la interfaz requiera navegación, acciones o entrada de datos.",
            {"adecuacion_funcional": 25, "usabilidad": 20},
        )

    # ACCESIBILIDAD
    images = soup.find_all("img")
    images_without_alt = [img for img in images if not img.get("alt")]

    if images_without_alt:
        total = len(images_without_alt)
        add_finding(
            "Accesibilidad",
            "Texto alternativo",
            "Alta",
            f"Se detectaron {total} imágenes sin atributo alt.",
            "Agregar texto alternativo descriptivo en imágenes informativas y alt vacío en imágenes decorativas.",
            {
                "accesibilidad": min(50, total * 8),
                "usabilidad": min(20, total * 3),
            },
        )

    buttons = soup.find_all("button")
    buttons_without_text = [
        btn
        for btn in buttons
        if not btn.get_text(strip=True)
        and not btn.get("aria-label")
        and not btn.get("title")
    ]

    if buttons_without_text:
        total = len(buttons_without_text)
        add_finding(
            "Accesibilidad",
            "Nombre accesible de controles",
            "Alta",
            f"Se detectaron {total} botones sin texto visible ni nombre accesible.",
            "Agregar texto visible, title o aria-label a cada botón.",
            {
                "accesibilidad": min(60, total * 12),
                "usabilidad": min(30, total * 5),
            },
        )

    links = soup.find_all("a")
    links_without_text = [
        a
        for a in links
        if not a.get_text(strip=True)
        and not a.get("aria-label")
        and not a.get("title")
        and not a.find("img", alt=True)
    ]

    if links_without_text:
        total = len(links_without_text)
        add_finding(
            "Accesibilidad",
            "Nombre accesible de enlaces",
            "Alta",
            f"Se detectaron {total} enlaces sin texto visible ni nombre accesible.",
            "Agregar texto descriptivo, aria-label o title a los enlaces.",
            {
                "accesibilidad": min(70, total * 5),
                "usabilidad": min(40, total * 3),
            },
        )

    inputs = soup.find_all(["input", "textarea", "select"])
    invalid_inputs = []

    for input_tag in inputs:
        input_id = input_tag.get("id")
        has_label = False

        if input_id and soup.find("label", attrs={"for": input_id}):
            has_label = True

        if input_tag.get("aria-label"):
            has_label = True

        if input_tag.get("placeholder"):
            has_label = True

        if not has_label:
            invalid_inputs.append(input_tag)

    if invalid_inputs:
        total = len(invalid_inputs)
        add_finding(
            "Accesibilidad",
            "Identificación de formularios",
            "Alta",
            f"Se detectaron {total} campos de formulario sin etiqueta accesible.",
            "Asociar cada campo con <label>, aria-label o placeholder descriptivo.",
            {
                "accesibilidad": min(50, total * 10),
                "usabilidad": min(25, total * 5),
            },
        )

    html_lower = html.lower()

    low_contrast_patterns = [
        "color:#fff",
        "color: #fff",
        "color:#ffffff",
        "color: #ffffff",
        "color:white",
        "color: white",
        "background:#fff",
        "background: #fff",
        "background:#ffffff",
        "background: #ffffff",
    ]

    contrast_hits = sum(1 for pattern in low_contrast_patterns if pattern in html_lower)

    if contrast_hits >= 3:
        add_finding(
            "Accesibilidad",
            "Contraste mínimo",
            "Media",
            "Se detectaron patrones que podrían generar bajo contraste visual.",
            "Verificar contraste mínimo WCAG AA de 4.5:1 para texto normal y 3:1 para texto grande.",
            {"accesibilidad": 20, "usabilidad": 10},
        )

    # USABILIDAD
    paragraphs = soup.find_all("p")
    long_paragraphs = [p for p in paragraphs if len(p.get_text(strip=True)) > 350]

    if long_paragraphs:
        total = len(long_paragraphs)
        add_finding(
            "Usabilidad",
            "Legibilidad",
            "Media",
            f"Se detectaron {total} párrafos extensos que pueden afectar la lectura web.",
            "Dividir textos largos en bloques más cortos, listas o secciones con subtítulos.",
            {"usabilidad": min(20, total * 5)},
        )

    colors = detect_colors(html)

    if len(colors) > 14:
        add_finding(
            "Usabilidad",
            "Consistencia estética",
            "Media",
            f"Se detectó una paleta visual extensa de {len(colors)} colores.",
            "Reducir la cantidad de colores y usar una paleta visual consistente.",
            {"usabilidad": 15},
        )
        tips.append("Usar una paleta cromática controlada para mejorar consistencia visual.")

    # EFICIENCIA
    scripts = soup.find_all("script")
    stylesheets = soup.find_all("link", rel="stylesheet")
    videos = soup.find_all("video")

    if len(scripts) > 10:
        add_finding(
            "Eficiencia de desempeño",
            "Comportamiento temporal",
            "Media",
            f"Se detectaron {len(scripts)} scripts en la interfaz.",
            "Reducir scripts innecesarios, dividir bundles y aplicar carga diferida cuando corresponda.",
            {"eficiencia_desempeno": min(35, len(scripts) * 3)},
        )

    if len(stylesheets) > 6:
        add_finding(
            "Eficiencia de desempeño",
            "Utilización de recursos",
            "Media",
            f"Se detectaron {len(stylesheets)} hojas de estilo externas.",
            "Unificar estilos, aplicar CSS crítico y evitar dependencias innecesarias.",
            {"eficiencia_desempeno": min(25, len(stylesheets) * 3)},
        )

    if len(images) > 12:
        add_finding(
            "Eficiencia de desempeño",
            "Recursos visuales",
            "Media",
            f"Se detectaron {len(images)} imágenes en la interfaz.",
            "Optimizar imágenes, aplicar lazy loading y usar formatos modernos como WebP o AVIF.",
            {"eficiencia_desempeno": min(35, len(images) * 3)},
        )

    if len(videos) > 1:
        add_finding(
            "Eficiencia de desempeño",
            "Recursos multimedia",
            "Media",
            f"Se detectaron {len(videos)} videos.",
            "Aplicar carga diferida, compresión multimedia o reproducción bajo demanda.",
            {"eficiencia_desempeno": 20},
        )

    if len(html) > 80000:
        add_finding(
            "Eficiencia de desempeño",
            "Tamaño del documento",
            "Media",
            "El documento HTML presenta una longitud elevada.",
            "Reducir HTML innecesario, dividir componentes y evitar contenido duplicado.",
            {"eficiencia_desempeno": 20, "mantenibilidad": 20},
        )

    # MANTENIBILIDAD
    div_count = len(soup.find_all("div"))
    semantic_count = len(
        soup.find_all(["main", "section", "article", "header", "footer", "nav", "aside"])
    )

    if div_count > 25 and semantic_count < 5:
        add_finding(
            "Mantenibilidad",
            "Modularidad y semántica",
            "Media",
            f"Se detectó uso elevado de etiquetas <div> ({div_count}) con baja presencia semántica.",
            "Reestructurar componentes usando etiquetas semánticas HTML5.",
            {"mantenibilidad": 30, "adecuacion_funcional": 10},
        )

    inline_styles = soup.find_all(style=True)

    if len(inline_styles) > 20:
        add_finding(
            "Mantenibilidad",
            "Modificabilidad",
            "Media",
            f"Se detectaron {len(inline_styles)} elementos con estilos inline.",
            "Mover estilos inline hacia clases CSS reutilizables.",
            {"mantenibilidad": min(30, len(inline_styles))},
        )

    duplicated_ids = []
    seen_ids = set()

    for tag in soup.find_all(attrs={"id": True}):
        tag_id = tag.get("id")

        if tag_id in seen_ids:
            duplicated_ids.append(tag_id)

        seen_ids.add(tag_id)

    if duplicated_ids:
        add_finding(
            "Mantenibilidad",
            "Analizabilidad",
            "Media",
            f"Se detectaron identificadores HTML duplicados: {len(set(duplicated_ids))}.",
            "Asegurar que cada id sea único dentro del documento HTML.",
            {"mantenibilidad": 15, "accesibilidad": 10},
        )

    # COMPATIBILIDAD
    if not soup.find("meta", attrs={"name": "viewport"}):
        add_finding(
            "Compatibilidad",
            "Adaptabilidad responsive",
            "Alta",
            "No se detectó meta viewport para diseño responsive.",
            "Agregar <meta name='viewport' content='width=device-width, initial-scale=1.0'>.",
            {"compatibilidad": 35, "portabilidad": 30},
        )

    # SEGURIDAD FRONTEND
    inline_events = []

    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.lower().startswith("on"):
                inline_events.append(attr)

    if inline_events:
        add_finding(
            "Seguridad",
            "Ejecución insegura",
            "Media",
            f"Se detectaron {len(inline_events)} eventos JavaScript inline.",
            "Separar la lógica JavaScript del marcado HTML y evitar eventos inline.",
            {"seguridad": min(35, len(inline_events) * 5)},
        )

    iframes = soup.find_all("iframe")
    unsafe_iframes = [iframe for iframe in iframes if not iframe.get("sandbox")]

    if unsafe_iframes:
        add_finding(
            "Seguridad",
            "Contenido embebido",
            "Media",
            f"Se detectaron {len(unsafe_iframes)} iframes sin atributo sandbox.",
            "Agregar sandbox a iframes para limitar riesgos de ejecución externa.",
            {"seguridad": 20},
        )

    # PORTABILIDAD
    if not soup.find("html") or not soup.find("body"):
        add_finding(
            "Portabilidad",
            "Estructura base",
            "Media",
            "La estructura HTML base está incompleta.",
            "Asegurar el uso correcto de etiquetas html, head y body.",
            {"portabilidad": 20},
        )

    if not soup.find("head"):
        add_finding(
            "Portabilidad",
            "Metadatos",
            "Media",
            "No se detectó la sección <head> del documento.",
            "Agregar la sección <head> con metadatos básicos del documento.",
            {"portabilidad": 15},
        )

    # AJUSTE FINAL POR SEVERIDAD
    high = len([f for f in findings if f["severity"] == "Alta"])
    critical = len([f for f in findings if f["severity"] == "Crítica"])
    medium = len([f for f in findings if f["severity"] == "Media"])

    general_penalty = critical * 8 + high * 4 + medium * 2

    for key in scores:
        scores[key] = clamp(scores[key] - general_penalty)

    global_score = round(sum(scores.values()) / len(scores))

    if len(findings) >= 25:
        global_score -= 30
    elif len(findings) >= 15:
        global_score -= 20
    elif len(findings) >= 8:
        global_score -= 12
    elif len(findings) >= 4:
        global_score -= 6

    global_score = clamp(global_score)

    return {
        "global_score": global_score,
        "quality_level": get_level(global_score),
        "scores": {key: clamp(value) for key, value in scores.items()},
        "total_findings": len(findings),
        "findings": findings,
        "engineering_tips": list(set(tips)),
        "strict_mode": True,
    }