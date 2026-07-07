from bs4 import BeautifulSoup
import re


def clamp(value):
    return max(0, min(100, value))


def detect_colors(html):
    hex_colors = re.findall(r"#[0-9a-fA-F]{3,6}", html)
    rgb_colors = re.findall(r"rgb[a]?\([^)]+\)", html)
    named_colors = re.findall(r"(?:color|background-color)\s*:\s*([a-zA-Z]+)", html)
    return list(set(hex_colors + rgb_colors + named_colors))


def parse_hex_color(color_str):
    color_str = color_str.strip().lower()
    if color_str.startswith("#"):
        hex_val = color_str[1:]
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        if len(hex_val) == 6:
            try:
                return (
                    int(hex_val[0:2], 16),
                    int(hex_val[2:4], 16),
                    int(hex_val[4:6], 16),
                )
            except ValueError:
                return None
    names = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (128, 128, 128),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
    }
    return names.get(color_str)


def get_luminance(r, g, b):
    a = []
    for v in (r, g, b):
        v /= 255.0
        if v <= 0.03928:
            a.append(v / 12.92)
        else:
            a.append(((v + 0.055) / 1.055) ** 2.4)
    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722


def get_contrast_ratio(c1, c2):
    rgb1 = parse_hex_color(c1)
    rgb2 = parse_hex_color(c2)
    if not rgb1 or not rgb2:
        return None
    l1 = get_luminance(*rgb1)
    l2 = get_luminance(*rgb2)
    if l1 > l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)


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



def get_element_snippet(el):
    if not hasattr(el, 'name') or not el.name:
        if isinstance(el, str): return el
        return ""
    attrs = []
    if el.get('id'):
        attrs.append(f'id="{el.get("id")}"')
    if el.get('class'):
        cl = el.get("class")
        cl_str = " ".join(cl) if isinstance(cl, list) else cl
        attrs.append(f'class="{cl_str}"')
    if el.get('src'):
        attrs.append(f'src="{el.get("src")[:50]}"')
    if el.get('href'):
        attrs.append(f'href="{el.get("href")[:50]}"')
    attr_str = " " + " ".join(attrs) if attrs else ""
    return f"<{el.name}{attr_str}>"

def format_snippets(elements, max_items=3):
    if not elements:
        return ""
    snippets = []
    for el in elements[:max_items]:
        snippet = get_element_snippet(el)
        if snippet:
            snippets.append(snippet)
    if not snippets:
        return ""
    suffix = "..." if len(elements) > max_items else ""
    return f" (Ejemplo: {', '.join(snippets)}{suffix})"

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

    def add_finding(
        dimension, subdimension, severity, finding, recommendation, penalties
    ):
        findings.append(
            {
                "dimension": dimension,
                "subdimension": subdimension,
                "severity": severity,
                "finding": f"[VIOLACIÓN] {finding}",
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
        return {
            "global_score": 0,
            "quality_level": "Crítico",
            "scores": {key: 0 for key in scores},
            "total_findings": len(findings),
            "findings": findings,
            "engineering_tips": ["Proporcionar un HTML válido para iniciar la auditoría."],
            "strict_mode": True,
        }

    # 1. ADECUACIÓN FUNCIONAL
    # 1.1 Elemento main
    if not soup.find("main"):
        add_finding(
            "Adecuación funcional",
            "Completitud funcional",
            "Alta",
            "No se detectó la etiqueta <main> para delimitar el contenido principal.",
            "Agregar una etiqueta <main> para estructurar el contenido principal de la interfaz.",
            {"adecuacion_funcional": 10, "usabilidad": 5},
        )

    # 1.2 Elemento nav
    if not soup.find("nav"):
        add_finding(
            "Adecuación funcional",
            "Pertinencia funcional",
            "Media",
            "No se detectó una estructura de navegación principal (<nav>).",
            "Incorporar una etiqueta <nav> o una estructura equivalente para mejorar la orientación del usuario.",
            {"adecuacion_funcional": 5, "usabilidad": 5},
        )

    # 1.3 Elemento h1 principal
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 0:
        add_finding(
            "Adecuación funcional",
            "Comprensibilidad",
            "Alta",
            "No se detectó un encabezado principal <h1>.",
            "Agregar un <h1> claro y único que indique el propósito principal de la interfaz.",
            {"adecuacion_funcional": 10, "usabilidad": 10},
        )
    elif len(h1_tags) > 1:
        add_finding(
            "Adecuación funcional",
            "Jerarquía de información",
            "Media",
            f"Se detectaron {len(h1_tags)} encabezados <h1> en la interfaz." + format_snippets(h1_tags),
            "Mantener un solo encabezado <h1> principal y organizar el resto con <h2>, <h3> y niveles posteriores.",
            {"adecuacion_funcional": 5, "usabilidad": 5},
        )

    # 1.4 Elementos interactivos
    interactive = soup.find_all(["button", "a", "input", "select", "textarea"])
    if len(interactive) == 0:
        add_finding(
            "Adecuación funcional",
            "Pertinencia funcional",
            "Alta",
            "No se detectaron elementos interactivos en la interfaz.",
            "Agregar controles interactivos cuando la interfaz requiera navegación, acciones o entrada de datos.",
            {"adecuacion_funcional": 15, "usabilidad": 10},
        )

    # 1.5 Estados asíncronos (Carga, Error, Vacío)
    if len(interactive) > 0:
        html_lower = html.lower()
        has_loading = any(
            x in html_lower
            for x in ["loading", "cargando", "spinner", "skeleton", "status"]
        ) or soup.find(attrs={"role": "status"})
        has_error = any(
            x in html_lower for x in ["error", "falló", "alert"]
        ) or soup.find(attrs={"role": "alert"})
        has_empty = any(
            x in html_lower for x in ["empty", "vacío", "no data", "no hay datos"]
        )

        if not (has_loading or has_error or has_empty):
            add_finding(
                "Adecuación funcional",
                "Completitud funcional",
                "Alta",
                "No se detectaron elementos visuales para el manejo de estados de carga (spinners/skeletons), errores o estados vacíos.",
                "Implementar estados visuales de carga, control de excepciones (Error Boundaries/alertas) y estados vacíos en el ciclo de vida asíncrono.",
                {"adecuacion_funcional": 10},
            )

    # 2. ACCESIBILIDAD
    # 2.1 Imágenes sin alt
    images = soup.find_all("img")
    images_without_alt = [img for img in images if not img.get("alt")]
    if images_without_alt:
        total = len(images_without_alt)
        add_finding(
            "Accesibilidad",
            "Texto alternativo",
            "Alta",
            f"Se detectaron {total} imágenes sin atributo alt." + format_snippets(images_without_alt),
            "Agregar texto alternativo descriptivo en imágenes informativas y alt vacío (alt='') en imágenes decorativas.",
            {
                "accesibilidad": min(15, total * 3),
                "usabilidad": min(10, total * 2),
            },
        )

    # 2.2 Botones sin texto o aria-label
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
            f"Se detectaron {total} botones sin texto visible ni nombre accesible." + format_snippets(buttons_without_text),
            "Agregar texto visible, atributo 'title' o 'aria-label' a cada botón para lectores de pantalla.",
            {
                "accesibilidad": min(20, total * 4),
                "usabilidad": min(10, total * 2),
            },
        )

    # 2.3 Enlaces sin texto ni accesibilidad
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
            f"Se detectaron {total} enlaces sin texto visible ni nombre accesible." + format_snippets(links_without_text),
            "Agregar texto descriptivo, aria-label o un elemento de imagen con 'alt' descriptivo dentro del enlace.",
            {
                "accesibilidad": min(15, total * 2),
                "usabilidad": min(10, total * 1),
            },
        )

    # 2.4 Inputs de formulario sin etiquetas (label/aria-label/placeholder)
    inputs = soup.find_all(["input", "textarea", "select"])
    inputs_without_label = []
    inputs_without_validation = []

    for input_tag in inputs:
        if input_tag.name == "input" and input_tag.get("type") in [
            "hidden",
            "submit",
            "button",
            "image",
        ]:
            continue

        input_id = input_tag.get("id")
        has_label = False

        if input_id and soup.find("label", attrs={"for": input_id}):
            has_label = True
        elif input_tag.get("aria-label") or input_tag.get("aria-labelledby"):
            has_label = True
        elif input_tag.get("placeholder"):
            has_label = True

        if not has_label:
            inputs_without_label.append(input_tag)

        if input_tag.name in ["textarea", "select"] or (
            input_tag.name == "input"
            and input_tag.get("type")
            in ["text", "email", "password", "search", "tel", "url", "number"]
        ):
            has_validation = any(
                input_tag.get(attr) for attr in ["required", "pattern", "min", "max"]
            )
            if not has_validation:
                inputs_without_validation.append(input_tag)

    if inputs_without_label:
        total = len(inputs_without_label)
        add_finding(
            "Accesibilidad",
            "Identificación de formularios",
            "Alta",
            f"Se detectaron {total} campos de formulario sin etiqueta accesible (label, aria-label o placeholder)." + format_snippets(inputs_without_label),
            "Asociar cada campo con una etiqueta <label> mediante el atributo 'for', o implementar atributos 'aria-label' / 'placeholder'.",
            {
                "accesibilidad": min(15, total * 3),
                "usabilidad": min(10, total * 2),
            },
        )

    if inputs_without_validation:
        total = len(inputs_without_validation)
        add_finding(
            "Usabilidad",
            "Protección contra errores de usuario",
            "Media",
            f"Se detectaron {total} campos de entrada de datos sin atributos de validación nativos (required, pattern, etc.)." + format_snippets(inputs_without_validation),
            "Agregar validación nativa del navegador mediante atributos como 'required', 'pattern' o tipos específicos (type='email').",
            {"usabilidad": min(10, total * 2)},
        )

    # 2.5 Relación de contraste de color bajo
    styled_elements = soup.find_all(style=True)
    low_contrast_count = 0
    low_contrast_elements = []
    for el in styled_elements:
        style_attr = el.get("style", "")
        color_match = re.search(r"color\s*:\s*([^;]+)", style_attr)
        bg_match = re.search(
            r"background(?:-color)?\s*:\s*([^;]+)", style_attr
        )

        if color_match and bg_match:
            c1 = color_match.group(1).strip()
            c2 = bg_match.group(1).strip()
            ratio = get_contrast_ratio(c1, c2)
            if ratio and ratio < 4.5:
                low_contrast_count += 1
                low_contrast_elements.append(el)

    if low_contrast_count > 0:
        add_finding(
            "Accesibilidad",
            "Contraste mínimo",
            "Media",
            f"Se detectaron {low_contrast_count} elementos con contraste de color bajo (< 4.5:1), dificultando la legibilidad." + format_snippets(low_contrast_elements),
            "Asegurar una relación de contraste mínima de 4.5:1 para texto normal y de 3:1 para texto grande según la WCAG AA.",
            {"accesibilidad": 10, "usabilidad": 5},
        )

    # 2.6 Orden de enfoque TabIndex > 0
    tabindex_tags = [
        t
        for t in soup.find_all(attrs={"tabindex": True})
        if t.get("tabindex").isdigit() and int(t.get("tabindex")) > 0
    ]
    if tabindex_tags:
        add_finding(
            "Accesibilidad",
            "Flujo de enfoque",
            "Alta",
            f"Se detectaron {len(tabindex_tags)} elementos con 'tabindex' mayor a 0, alterando la navegación natural." + format_snippets(tabindex_tags),
            "Evitar el uso de tabindex > 0. Utilizar tabindex='0' para elementos interactivos personalizados y estructurar el DOM lógicamente.",
            {"accesibilidad": 10, "usabilidad": 5},
        )

    # 2.7 Pistas de subtítulos en videos/audios
    media_tags = soup.find_all(["video", "audio"])
    missing_tracks = 0
    media_without_tracks = []
    for media in media_tags:
        tracks = media.find_all("track")
        has_subtitles = any(
            t.get("kind") in ["subtitles", "captions"] for t in tracks
        )
        if not has_subtitles:
            missing_tracks += 1
            media_without_tracks.append(media)

    if missing_tracks > 0:
        add_finding(
            "Accesibilidad",
            "Soporte multimedia",
            "Alta",
            f"Se detectaron {missing_tracks} elementos multimedia (video/audio) sin pistas de subtítulos o transcripciones." + format_snippets(media_without_tracks),
            "Agregar elementos <track kind='subtitles' srclang='es' src='subtítulos.vtt'> a todos los videos y audios.",
            {"accesibilidad": 10, "usabilidad": 5},
        )

    # 3. USABILIDAD
    # 3.1 Párrafos demasiado largos (> 350 caracteres)
    paragraphs = soup.find_all("p")
    long_paragraphs = [p for p in paragraphs if len(p.get_text(strip=True)) > 350]
    if long_paragraphs:
        total = len(long_paragraphs)
        add_finding(
            "Usabilidad",
            "Legibilidad",
            "Media",
            f"Se detectaron {total} párrafos extensos que pueden sobrecargar la lectura." + format_snippets(long_paragraphs),
            "Dividir bloques de texto largos en secciones más pequeñas, listas o agregar subtítulos organizadores.",
            {"usabilidad": min(10, total * 2)},
        )

    # 3.2 Consistencia de la paleta de colores (> 14 colores)
    colors = detect_colors(html)
    if len(colors) > 14:
        add_finding(
            "Usabilidad",
            "Consistencia estética",
            "Media",
            f"Se detectó una paleta de colores demasiado amplia ({len(colors)} colores), afectando la sobriedad estética.",
            "Establecer una paleta de colores unificada y consistente en el archivo de diseño global.",
            {"usabilidad": 10},
        )

    # 3.3 Estabilidad Visual (CLS) - Imágenes/Iframes sin dimensiones
    media_files = soup.find_all(["img", "iframe"])
    cls_violations = 0
    elements_cls = []
    for med in media_files:
        has_dims = med.get("width") and med.get("height")
        style = med.get("style", "")
        has_style_dims = "width" in style and "height" in style
        if not (has_dims or has_style_dims):
            cls_violations += 1
            elements_cls.append(med)

    if cls_violations > 0:
        add_finding(
            "Usabilidad",
            "Estética de la interfaz",
            "Media",
            f"Se detectaron {cls_violations} elementos multimedia (imágenes/iframes) sin dimensiones explícitas, propiciando saltos de diseño (CLS)." + format_snippets(elements_cls),
            "Definir siempre atributos width/height en etiquetas de imágenes o configurar relaciones de aspecto en CSS (aspect-ratio).",
            {"usabilidad": 8, "eficiencia_desempeno": 8},
        )

    # 3.4 Coherencia visual con Variables CSS
    css_inline_text = "".join(el.get("style", "") for el in styled_elements)
    style_tags = soup.find_all("style")
    css_tag_text = "".join(tag.get_text() for tag in style_tags)
    total_css = css_inline_text + css_tag_text
    if len(total_css) > 500 and "--" not in total_css:
        add_finding(
            "Usabilidad",
            "Estética de la interfaz",
            "Baja",
            "Se detectó código CSS/estilos inline que no consumen variables CSS globales del sistema de diseño (Design System).",
            "Declarar valores comunes de color, tipografía y espaciado como variables CSS (--font-primary, --color-main) para asegurar la coherencia.",
            {"usabilidad": 5},
        )

    # 4. EFICIENCIA DE DESEMPEÑO
    # 4.1 Script y Hojas de estilo excesivas
    scripts = soup.find_all("script")
    stylesheets = soup.find_all("link", rel="stylesheet")
    if len(scripts) > 10:
        add_finding(
            "Eficiencia de desempeño",
            "Comportamiento temporal",
            "Media",
            f"Se detectó un exceso de scripts en el documento ({len(scripts)} scripts)." + format_snippets(scripts, 2),
            "Unificar scripts, utilizar bundles y aplicar técnicas de carga diferida (defer/async).",
            {"eficiencia_desempeno": 10},
        )

    if len(stylesheets) > 6:
        add_finding(
            "Eficiencia de desempeño",
            "Utilización de recursos",
            "Media",
            f"Se detectaron {len(stylesheets)} hojas de estilo externas." + format_snippets(stylesheets, 2),
            "Minificar y concatenar archivos CSS, o implementar CSS crítico para mejorar el renderizado inicial.",
            {"eficiencia_desempeno": 8},
        )

    if len(images) > 12:
        add_finding(
            "Eficiencia de desempeño",
            "Utilización de recursos",
            "Media",
            f"Se detectaron {len(images)} imágenes en el marcado inicial." + format_snippets(images, 2),
            "Implementar lazy loading nativo (loading='lazy') en imágenes secundarias y optimizar formatos a WebP/AVIF.",
            {"eficiencia_desempeno": 8},
        )

    videos = soup.find_all("video")
    if len(videos) > 1:
        add_finding(
            "Eficiencia de desempeño",
            "Recursos multimedia",
            "Media",
            f"Se detectaron {len(videos)} etiquetas de video integradas de forma síncrona." + format_snippets(videos, 2),
            "Cargar elementos multimedia de forma diferida o mediante reproducción a demanda para no penalizar la red.",
            {"eficiencia_desempeno": 10},
        )

    if len(html) > 80000:
        add_finding(
            "Eficiencia de desempeño",
            "Tamaño del documento",
            "Media",
            "El tamaño del archivo HTML supera los 80KB.",
            "Dividir el HTML, remover scripts embebidos pesados e implementar renderizado dinámico o compresión Gzip/Brotli.",
            {"eficiencia_desempeno": 10, "mantenibilidad": 10},
        )

    # 4.2 LCP
    head_tag = soup.find("head")
    head_scripts_blocking = [
        s
        for s in head_tag.find_all("script")
        if s.get("src") and not s.get("defer") and not s.get("async")
    ] if head_tag else []

    hero_image = soup.find("img")
    has_lcp_violation = len(head_scripts_blocking) > 3 or (
        hero_image and hero_image.get("loading") == "lazy"
    )
    if has_lcp_violation:
        add_finding(
            "Eficiencia de desempeño",
            "Comportamiento temporal",
            "Alta",
            "Se detectaron bloqueos potenciales al Largest Contentful Paint (LCP) (ej. scripts síncronos en el <head> o imagen hero cargada diferida)." + format_snippets(head_scripts_blocking, 2),
            "Remover el atributo loading='lazy' de la imagen de portada/hero, y asegurar que los scripts del head utilicen defer o async.",
            {"eficiencia_desempeno": 10},
        )

    # 4.3 INP
    inline_events = []
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.lower().startswith("on"):
                inline_events.append(tag)

    if len(inline_events) > 5:
        add_finding(
            "Eficiencia de desempeño",
            "Comportamiento temporal",
            "Media",
            f"Se detectaron {len(inline_events)} manejadores de eventos JavaScript inline, lo que puede degradar la interacción al usuario (INP)." + format_snippets(inline_events, 2),
            "Mudar los manejadores de eventos inline (onclick) hacia listeners en archivos JS externos (.addEventListener).",
            {"eficiencia_desempeno": 10},
        )

    # 4.4 Tree Shaking
    cdn_scripts = [
        s.get("src", "")
        for s in scripts
        if "cdn" in s.get("src", "") or "cdnjs" in s.get("src", "")
    ]
    heavy_libs_detected = [
        lib
        for lib in ["lodash", "moment", "jquery", "bootstrap"]
        for src in cdn_scripts
        if lib in src.lower()
    ]
    if heavy_libs_detected:
        add_finding(
            "Eficiencia de desempeño",
            "Utilización de recursos",
            "Media",
            f"Se detectaron scripts CDN para librerías pesadas completas ({', '.join(set(heavy_libs_detected))}) sin Tree Shaking.",
            "Migrar a módulos ES6 importados de forma selectiva o utilizar empaquetadores como Vite/Webpack para agrupar únicamente el código en uso.",
            {"eficiencia_desempeno": 8},
        )

    # 5. COMPATIBILIDAD
    # 5.1 Fuga de estilos CSS
    global_selectors = []
    for tag in style_tags:
        css_text = tag.get_text()
        found_tags = re.findall(
            r"(?:^|[\s,])(body|div|p|span|button|a|input|h1|h2|h3)\s*\{",
            css_text,
        )
        global_selectors.extend(found_tags)

    if global_selectors:
        add_finding(
            "Compatibilidad",
            "Coexistencia",
            "Alta",
            f"Se detectaron estilos globales directos sobre etiquetas HTML ({', '.join(set(global_selectors))}) en el bloque <style>.",
            "Utilizar CSS encapsulado (CSS Modules, BEM o scoped styles) para evitar colisión de estilos con otros componentes del DOM.",
            {"compatibilidad": 10},
        )

    # 5.2 Polución del objeto global window
    script_texts = "".join(s.get_text() for s in scripts)
    if "window." in script_texts:
        assignments = re.findall(r"window\.[a-zA-Z0-9_]+\s*=", script_texts)
        if len(assignments) > 0:
            add_finding(
                "Compatibilidad",
                "Coexistencia",
                "Alta",
                "Se detectó polución del objeto global 'window' mediante scripts inline.",
                "Encapsular las variables en funciones autoejecutables (IIFE) o variables locales dentro de módulos JavaScript.",
                {"compatibilidad": 10},
            )

    # 5.3 Validación de esquemas API
    has_fetch = "fetch(" in script_texts or "axios" in script_texts
    has_schema_validation = any(
        kw in script_texts.lower()
        for kw in ["zod", "z.object", "validate", "yup", "schema", "joi"]
    )
    if has_fetch and not has_schema_validation:
        add_finding(
            "Compatibilidad",
            "Interoperabilidad",
            "Media",
            "Se detectaron peticiones de red (fetch/axios) pero no se encuentra código de validación de esquemas (Zod/TypeScript).",
            "Implementar validadores de esquemas como Zod para asegurar que los datos de entrada de la API cumplan con la estructura requerida.",
            {"compatibilidad": 10},
        )

    # 6. FIABILIDAD
    # 6.1 React SPA Error Boundaries
    is_spa = any("react" in s.lower() for s in cdn_scripts) or soup.find(
        id=["root", "app"]
    )
    has_error_handler = any(
        kw in script_texts.lower()
        for kw in ["onerror", "unhandledrejection", "errorboundary", "catch"]
    )
    if is_spa and not has_error_handler:
        add_finding(
            "Fiabilidad",
            "Tolerancia a fallos",
            "Alta",
            "No se detectaron Error Boundaries ni manejadores de excepciones globales en el frontend de tipo Single Page Application (SPA).",
            "Incorporar Error Boundaries en componentes jerárquicos clave de React para aislar y recuperar errores visuales.",
            {"fiabilidad": 10},
        )

    # 6.2 Retry policies y timeouts en llamadas HTTP
    if has_fetch:
        has_timeout = "timeout" in script_texts.lower() or "abortcontroller" in script_texts.lower()
        has_retry = "retry" in script_texts.lower()
        if not (has_timeout or has_retry):
            add_finding(
                "Fiabilidad",
                "Tolerancia a fallos",
                "Media",
                "Se detectaron llamadas HTTP sin políticas de reintento ni configuración de timeouts.",
                "Configurar un tiempo límite de expiración (timeout) y reintentos automáticos para evitar llamadas colgadas por latencia de red.",
                {"fiabilidad": 10},
            )

    # 7. SEGURIDAD FRONTEND
    # 7.1 XSS vía innerHTML o dangerouslySetInnerHTML sin DOMPurify
    has_unsafe_html = "innerhtml" in script_texts.lower() or "dangerouslysetinnerhtml" in script_texts.lower()
    has_purify = "dompurify" in script_texts.lower() or "purify" in script_texts.lower()
    if has_unsafe_html and not has_purify:
        add_finding(
            "Seguridad",
            "Confidencialidad e integridad",
            "Alta",
            "Se detectó el uso de inserción directa de HTML dinámico (innerHTML) sin uso de librerías de sanitización como DOMPurify.",
            "Sanitizar siempre los fragmentos de HTML dinámico con DOMPurify antes de cargarlos en el DOM para mitigar ataques XSS.",
            {"seguridad": 15},
        )

    # 7.2 Almacenamiento sensible en localStorage/sessionStorage
    has_storage = "localstorage" in script_texts.lower() or "sessionstorage" in script_texts.lower()
    has_sensitive_keys = any(
        k in script_texts.lower()
        for k in ["jwt", "token", "password", "session", "cred"]
    )
    if has_storage and has_sensitive_keys:
        add_finding(
            "Seguridad",
            "Confidencialidad",
            "Alta",
            "Se detectó el almacenamiento de información potencialmente sensible (tokens/jwt) en localStorage o sessionStorage.",
            "Mudar el almacenamiento de tokens de sesión a cookies seguras con atributos HttpOnly, Secure y SameSite=Strict.",
            {"seguridad": 15},
        )

    # 8. MANTENIBILIDAD
    # 8.1 Modularidad
    dom_signatures = []
    for parent in soup.find_all(True):
        children = parent.find_all(recursive=False)
        if len(children) > 3:
            sig = "-".join(c.name for c in children)
            if sig not in ["li-li-li-li", "tr-tr-tr-tr", "option-option-option-option"]:
                dom_signatures.append(sig)

    duplicated_sigs = [s for s in set(dom_signatures) if dom_signatures.count(s) > 3]
    if len(duplicated_sigs) > 0:
        add_finding(
            "Mantenibilidad",
            "Modularidad y semántica",
            "Media",
            "Se detectó duplicación de estructuras complejas en el DOM que no están modularizadas.",
            "Identificar patrones repetitivos en el marcado y modularizarlos en componentes de UI reutilizables.",
            {"mantenibilidad": 10},
        )

    # 8.2 Acoplamiento excesivo de lógica HTTP en elementos visuales
    body_tag = soup.find("body")
    inline_body_scripts_with_fetch = []
    if body_tag:
        for s in body_tag.find_all("script"):
            if "fetch(" in s.get_text() or "axios" in s.get_text():
                inline_body_scripts_with_fetch.append(s)

    if inline_body_scripts_with_fetch:
        add_finding(
            "Mantenibilidad",
            "Modificabilidad",
            "Media",
            "Se detectaron scripts de comunicación HTTP directamente incrustados dentro de los contenedores visuales de la interfaz.",
            "Desacoplar la lógica de red de las vistas. Centralizar las peticiones HTTP en módulos de servicios o hooks dedicados.",
            {"mantenibilidad": 10},
        )

    # 8.3 Divitis y baja semántica
    div_count = len(soup.find_all("div"))
    semantic_count = len(
        soup.find_all(
            ["main", "section", "article", "header", "footer", "nav", "aside"]
        )
    )
    if div_count > 25 and semantic_count < 5:
        add_finding(
            "Mantenibilidad",
            "Modularidad y semántica",
            "Media",
            f"Se detectó un uso excesivo de etiquetas <div> ({div_count}) en relación a etiquetas semánticas ({semantic_count}).",
            "Reemplazar contenedores genéricos <div> por etiquetas semánticas de HTML5 (section, article, header, footer) para mejorar la legibilidad del DOM.",
            {"mantenibilidad": 10, "adecuacion_funcional": 5},
        )

    # 8.4 Estilos inline
    inline_styles = soup.find_all(style=True)
    if len(inline_styles) > 20:
        add_finding(
            "Mantenibilidad",
            "Modificabilidad",
            "Media",
            f"Se detectaron {len(inline_styles)} elementos con estilos inline directos." + format_snippets(inline_styles, 2),
            "Migrar estilos inline hacia clases en hojas de estilo CSS reutilizables para facilitar la mantenibilidad.",
            {"mantenibilidad": min(15, len(inline_styles))},
        )

    # 8.5 IDs duplicados
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
            f"Se detectaron identificadores (id) duplicados en el DOM: {len(set(duplicated_ids))}." + " (Ejemplo: " + ", ".join(list(set(duplicated_ids))[:3]) + ")",
            "Asegurar la unicidad de cada atributo 'id' en el documento HTML para cumplir con los estándares DOM y accesibilidad.",
            {"mantenibilidad": 10, "accesibilidad": 5},
        )

    # 9. PORTABILIDAD Y ADAPTABILIDAD
    # 9.1 Estructura base
    if not soup.find("html") or not soup.find("body"):
        add_finding(
            "Portabilidad",
            "Estructura base",
            "Media",
            "El documento HTML está incompleto y carece de las etiquetas base estándar (html, body).",
            "Completar la estructura básica del documento incluyendo las etiquetas html, head y body válidas.",
            {"portabilidad": 10},
        )

    if not soup.find("head"):
        add_finding(
            "Portabilidad",
            "Metadatos",
            "Media",
            "No se detectó la sección <head> en el HTML.",
            "Agregar el elemento <head> para contener los metadatos globales, título y recursos necesarios.",
            {"portabilidad": 5},
        )

    # 9.2 Meta viewport
    if not soup.find("meta", attrs={"name": "viewport"}):
        add_finding(
            "Compatibilidad",
            "Adaptabilidad responsive",
            "Alta",
            "No se detectó la etiqueta <meta name='viewport'> para diseño responsive.",
            "Agregar <meta name='viewport' content='width=device-width, initial-scale=1.0'> para habilitar el escalamiento responsive.",
            {"compatibilidad": 15, "portabilidad": 10},
        )

    # 9.3 Diseños rígidos con ancho fijo en px
    rigid_layouts = 0
    for w in re.findall(r"width\s*:\s*(\d+)px", total_css):
        if int(w) > 400:
            rigid_layouts += 1

    if rigid_layouts > 0:
        add_finding(
            "Portabilidad",
            "Adaptabilidad",
            "Alta",
            f"Se detectaron {rigid_layouts} reglas de ancho rígido en píxeles (width: >400px) en la estructura.",
            "Reemplazar anchos fijos en píxeles por unidades de diseño flexible (%, vw, rem, flex) para facilitar la portabilidad en diversos dispositivos.",
            {"portabilidad": 10},
        )

    # CALCULO DE PUNTAJES FINAL POR PROMEDIO REAL
    clamped_scores = {key: clamp(value) for key, value in scores.items()}
    global_score = round(sum(clamped_scores.values()) / len(clamped_scores))

    return {
        "global_score": global_score,
        "quality_level": get_level(global_score),
        "scores": clamped_scores,
        "total_findings": len(findings),
        "findings": findings,
        "engineering_tips": ["Optimizar el marcado HTML y refactorizar dependencias para lograr la conformidad."],
        "strict_mode": True,
    }