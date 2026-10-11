"""
services/iso_framework.py — Operacionalización de ISO/IEC 25010 para frontend.

La norma es un modelo conceptual: no prescribe algoritmos de medición
(restricción 1). Este módulo hace explícito el mapeo característica →
subcaracterística → métrica medible, define la escala de severidad 0–4, el criterio de decisión 0–10, la
selección de características y las condiciones de la evaluación y declara qué NO puede medirse
de forma automática (restricciones 2–5).

Las métricas siguen la forma X = A / B, adaptadas al
artefacto que audita FrontMind: el DOM renderizado de una interfaz y las
métricas de ejecución registradas por Playwright.
"""
from __future__ import annotations

import re
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Características (claves internas usadas en los puntajes)
# ─────────────────────────────────────────────────────────────────────────────

CHARACTERISTICS = {
    "adecuacion_funcional": "Adecuación funcional",
    "eficiencia_desempeno": "Eficiencia de desempeño",
    "usabilidad": "Usabilidad (capacidad de interacción)",
    "accesibilidad": "Accesibilidad (subcaracterística de usabilidad, tratada aparte)",
    "mantenibilidad": "Mantenibilidad",
    "compatibilidad": "Compatibilidad",
    "seguridad": "Seguridad",
    "portabilidad": "Portabilidad (flexibilidad en ISO/IEC 25010:2023)",
}

# ─────────────────────────────────────────────────────────────────────────────
# Escala de severidad (0–4) y criterio de decisión (0–10)
# ─────────────────────────────────────────────────────────────────────────────

SEVERITY_GRADES = {
    0: {"label": "No", "criterion": "Cumplimiento satisfactorio (> 90 %)"},
    1: {"label": "Cosmético", "criterion": "Defecto menor que no impide la operación (51 % – 89 %)"},
    2: {"label": "Menor", "criterion": "Inconveniente local que afecta la fluidez (11 % – 50 %)"},
    3: {"label": "Mayor", "criterion": "Fallo grave que dificulta completar tareas clave (1 % – 10 %)"},
    4: {"label": "Catastrófico", "criterion": "Bloqueo crítico o incumplimiento total (< 1 %)"},
}

# Severidad cualitativa usada por las reglas → grado 0–4
_SEVERITY_TO_GRADE = {"Crítica": 4, "Alta": 3, "Media": 2, "Baja": 1}


def severity_grade(severity: str) -> dict:
    grade = _SEVERITY_TO_GRADE.get(severity, 2)
    return {"grade": grade, "label": SEVERITY_GRADES[grade]["label"]}


def grade_from_compliance(ratio: Optional[float]) -> Optional[int]:
    """Grado 0–4 a partir del porcentaje de cumplimiento de una métrica X = A/B."""
    if ratio is None:
        return None
    pct = ratio * 100
    if pct >= 90:
        return 0
    if pct >= 51:
        return 1
    if pct >= 11:
        return 2
    if pct >= 1:
        return 3
    return 4


def decision_criterion(global_score_100: float) -> dict:
    """
    Criterio de decisión sobre escala 0–10:
      [9.0 – 10.0] Alta · ]6.0 – 9.0[ Buena · ]2.0 – 6.0] Regular · [0.0 – 2.0] Mala
    (9.0 se asigna a "Alta" para resolver el solapamiento de los intervalos.)
    """
    score_10 = round(max(0.0, min(100.0, float(global_score_100))) / 10, 1)
    if score_10 >= 9.0:
        category, meaning = "Alta calidad", "El sistema cumple holgadamente con los estándares."
    elif score_10 > 6.0:
        category, meaning = "Buena calidad", "Cumplimiento adecuado con observaciones menores."
    elif score_10 > 2.0:
        category, meaning = "Regular calidad", "Presencia de deuda técnica o barreras moderadas."
    else:
        category, meaning = "Mala calidad", "Deficiencias críticas que requieren reestructuración."
    return {"score_10": score_10, "category": category, "meaning": meaning}


# ─────────────────────────────────────────────────────────────────────────────
# Alcance: qué se mide, cómo y qué queda fuera (restricciones 3, 4 y 5)
# ─────────────────────────────────────────────────────────────────────────────

AUTOMATED, PARTIAL, MANUAL = "automatizada", "parcial (indicador aproximado)", "no automatizable"

QUALITY_MODEL: list[dict[str, Any]] = [
    # Adecuación funcional
    {"characteristic": "adecuacion_funcional", "sub": "Completitud funcional", "automation": PARTIAL,
     "method": "Presencia de estructura principal (<main>, <h1>, controles, estados de carga/error).",
     "limit": "Sin la especificación de requisitos no puede verificarse que se cubran todas las tareas del usuario."},
    {"characteristic": "adecuacion_funcional", "sub": "Exactitud funcional", "automation": MANUAL,
     "method": "Pruebas funcionales con casos y resultados esperados.",
     "limit": "Requiere oráculos de prueba y datos esperados; no se infiere del DOM."},
    {"characteristic": "adecuacion_funcional", "sub": "Pertinencia funcional", "automation": PARTIAL,
     "method": "Navegación (<nav>) y controles interactivos disponibles.",
     "limit": "Contar los pasos necesarios para una tarea requiere escenarios de uso definidos."},
    # Eficiencia de desempeño
    {"characteristic": "eficiencia_desempeno", "sub": "Comportamiento temporal", "automation": AUTOMATED,
     "method": "TTFB, LCP y carga medidos con Playwright (Chromium) sobre la página original.",
     "limit": "Medido desde el servidor de evaluación: depende de su red y hardware, no del dispositivo del usuario."},
    {"characteristic": "eficiencia_desempeno", "sub": "Utilización de recursos", "automation": AUTOMATED,
     "method": "Bytes transferidos, número de peticiones y memoria JS del cliente (Playwright).",
     "limit": "transferSize es 0 para recursos de otro origen sin Timing-Allow-Origin; la CPU no se mide."},
    {"characteristic": "eficiencia_desempeno", "sub": "Capacidad", "automation": MANUAL,
     "method": "Pruebas de carga y concurrencia (p. ej. Locust).",
     "limit": "Requiere generar carga sobre el sistema auditado, fuera del alcance de una auditoría pasiva."},
    # Usabilidad / capacidad de interacción
    {"characteristic": "usabilidad", "sub": "Inteligibilidad (reconocimiento de adecuación)", "automation": MANUAL,
     "method": "Cuestionarios o juicio de expertos.",
     "limit": "Depende de la percepción del usuario sobre sus propias necesidades."},
    {"characteristic": "usabilidad", "sub": "Capacidad de aprendizaje", "automation": MANUAL,
     "method": "Tiempo para completar la tarea correctamente en pruebas con usuarios.",
     "limit": "Requiere participantes reales y cronometraje de tareas."},
    {"characteristic": "usabilidad", "sub": "Operabilidad", "automation": PARTIAL,
     "method": "Controles operables, foco de teclado y adaptación a 3 resoluciones.",
     "limit": "Los pasos por unidad de tiempo requieren observar tareas reales."},
    {"characteristic": "usabilidad", "sub": "Protección contra errores del usuario", "automation": AUTOMATED,
     "method": "Proporción de campos con validación declarativa y mensajes de estado (aria-live/role=alert).",
     "limit": "No mide la tasa real de recuperación ante entradas inválidas."},
    {"characteristic": "usabilidad", "sub": "Estética de la interfaz", "automation": PARTIAL,
     "method": "Inspección objetiva: uniformidad de paleta, variables CSS, longitud de párrafos.",
     "limit": "El agrado visual es subjetivo: requiere cuestionarios (p. ej. SUS) o juicio experto."},
    {"characteristic": "accesibilidad", "sub": "Accesibilidad técnica (WCAG: perceptible, operable, comprensible, robusto)",
     "automation": AUTOMATED,
     "method": "Texto alternativo, etiquetas, nombres accesibles, idioma, contraste, orden de foco.",
     "limit": "Las pruebas automáticas detectan sólo una parte de los criterios WCAG; se recomienda revisión con lector de pantalla."},
    # Mantenibilidad
    {"characteristic": "mantenibilidad", "sub": "Modularidad", "automation": PARTIAL,
     "method": "Proporción de elementos semánticos y estilos desacoplados en el DOM.",
     "limit": "MS1M1/MS1M2 (independencia y acoplamiento de componentes) requieren el código fuente y su grafo de dependencias."},
    {"characteristic": "mantenibilidad", "sub": "Reusabilidad", "automation": MANUAL,
     "method": "MS2M1: elementos reutilizados / elementos de la biblioteca.",
     "limit": "Requiere el repositorio y la biblioteca de componentes del proyecto."},
    {"characteristic": "mantenibilidad", "sub": "Analizabilidad", "automation": PARTIAL,
     "method": "Unicidad de identificadores y estructura del DOM.",
     "limit": "MS3M1/MS3M2 (pistas de auditoría y diagnóstico) requieren acceso a logs y especificación."},
    {"characteristic": "mantenibilidad", "sub": "Capacidad de ser modificado", "automation": PARTIAL,
     "method": "MS4M1: complejidad ciclomática aproximada de los scripts embebidos (X = A + 1).",
     "limit": "En apps empaquetadas el JS está minificado; MS4M3 requiere historial de defectos."},
    {"characteristic": "mantenibilidad", "sub": "Capacidad de ser probado", "automation": MANUAL,
     "method": "MS5M1/MS5M2: cobertura y autonomía de las pruebas.",
     "limit": "Requiere el código fuente y la suite de pruebas."},
    # Compatibilidad
    {"characteristic": "compatibilidad", "sub": "Coexistencia e interoperabilidad", "automation": PARTIAL,
     "method": "Estilos globales, polución de window, viewport responsive.",
     "limit": "No se ejecuta en varios navegadores; sólo Chromium."},
    # Seguridad
    {"characteristic": "seguridad", "sub": "Confidencialidad e integridad (cliente)", "automation": PARTIAL,
     "method": "Patrones inseguros en el HTML (innerHTML sin sanitizar, datos sensibles en storage).",
     "limit": "No es una prueba de penetración; no evalúa el backend ni la autenticación del sistema auditado."},
    # Portabilidad
    {"characteristic": "portabilidad", "sub": "Adaptabilidad", "automation": AUTOMATED,
     "method": "Estructura base, meta viewport y anchos rígidos; capturas en 1366, 768 y 390 px.",
     "limit": "Instalabilidad y reemplazabilidad no aplican a una interfaz web desplegada."},
]

# Características de la norma no contempladas o fuera de alcance (restricción 4)
OUT_OF_SCOPE = [
    {"characteristic": "Fiabilidad", "reason": "Madurez, disponibilidad y tolerancia a fallos requieren monitoreo en el tiempo, no una captura puntual."},
    {"characteristic": "Seguridad física (Safety, ISO/IEC 25010:2023)", "reason": "No aplica a interfaces web sin riesgo físico para personas o entorno."},
    {"characteristic": "Calidad en uso (efectividad, eficiencia, satisfacción)", "reason": "Requiere usuarios reales, cuestionarios y tareas observadas."},
    {"characteristic": "Calidad de la información producida", "reason": "La norma no la contempla directamente y depende del dominio de los datos."},
]


def evaluation_scope(selected: list[str]) -> dict:
    items = [
        {**item, "characteristic_label": CHARACTERISTICS[item["characteristic"]]}
        for item in QUALITY_MODEL
        if item["characteristic"] in selected
    ]
    return {
        "selected_characteristics": [CHARACTERISTICS[c] for c in selected],
        "subcharacteristics": items,
        "coverage": {
            "automatizada": sum(1 for i in items if i["automation"] == AUTOMATED),
            "parcial": sum(1 for i in items if i["automation"] == PARTIAL),
            "no_automatizable": sum(1 for i in items if i["automation"] == MANUAL),
            "total": len(items),
        },
        "out_of_scope": OUT_OF_SCOPE,
    }


def evaluation_restrictions(has_runtime_metrics: bool) -> list[dict]:
    """Condiciones y límites bajo los que se realizó la evaluación."""
    return [
        {"type": "Herramientas y metodología",
         "detail": "Análisis estático del DOM (BeautifulSoup) y ejecución en Chromium headless (Playwright). "
                   "Las reglas son una operacionalización propia de la norma, que no prescribe algoritmos."},
        {"type": "Artefacto evaluado",
         "detail": "HTML renderizado de cada interfaz (o su réplica). No se analiza el repositorio fuente, "
                   "por lo que las métricas de modularidad, reusabilidad y testabilidad son parciales o no medibles."},
        {"type": "Entorno de prueba",
         "detail": "Resoluciones 1366×768, 768×1024 y 390×844 en un único navegador (Chromium). "
                   + ("Las métricas de desempeño se midieron una vez desde el servidor de evaluación."
                      if has_runtime_metrics else
                      "No se recibieron métricas de ejecución: el comportamiento temporal se estima con indicadores estáticos.")},
        {"type": "Tiempo y recursos",
         "detail": "Máximo de interfaces configurable (por defecto 10), tiempo límite por página y hasta 2 capturas simultáneas."},
        {"type": "Atributos subjetivos",
         "detail": "Estética, satisfacción y facilidad de aprendizaje se reportan como indicadores aproximados; "
                   "su validación requiere cuestionarios o juicio de expertos."},
        {"type": "Selección de características",
         "detail": "Se evalúa un subconjunto priorizado de características; las no seleccionadas o fuera de alcance "
                   "no influyen en el puntaje global."},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Métricas X = A / B
# ─────────────────────────────────────────────────────────────────────────────

_NON_LABELED_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
_VALIDATION_TYPES = {"email", "number", "url", "tel", "date", "datetime-local", "month", "week", "time"}
_SEMANTIC_TAGS = ["main", "nav", "header", "footer", "section", "article", "aside"]
_JS_TYPES = {"", "text/javascript", "application/javascript", "module"}
_DECISION_RE = re.compile(r"\bif\b|\bfor\b|\bwhile\b|\bcase\b|\bcatch\b|&&|\|\||\?\?|\?(?![.?])")
_FUNCTION_RE = re.compile(r"\bfunction\b|=>")


def _ratio_metric(mid, characteristic, sub, name, a, b, a_desc, b_desc, target=0.9, reference="Operacionalización ISO/IEC 25010"):
    x = (a / b) if b else None
    return {
        "id": mid, "characteristic": characteristic, "subcharacteristic": sub, "name": name,
        "formula": "X = A / B", "A": a, "B": b, "A_description": a_desc, "B_description": b_desc,
        "X": round(x, 3) if x is not None else None,
        "target": f"X ≥ {target}",
        "meets": (x >= target) if x is not None else None,
        # Grado 0–4 según el cumplimiento relativo a la meta (X / meta, máx. 1)
        "severity_grade": grade_from_compliance(min(1.0, x / target)) if x is not None and target else None,
        "status": "medido" if x is not None else "no aplica (B = 0)",
        "reference": reference,
    }


def _value_metric(mid, characteristic, sub, name, value, unit, target_text, meets, reference, formula="X = valor medido"):
    return {
        "id": mid, "characteristic": characteristic, "subcharacteristic": sub, "name": name,
        "formula": formula, "X": value, "unit": unit, "target": target_text,
        "meets": meets if value is not None else None,
        "severity_grade": (0 if meets else 3) if value is not None else None,
        "status": "medido" if value is not None else "no medido",
        "reference": reference,
    }


def _has_accessible_name(el) -> bool:
    return bool(el.get_text(strip=True) or el.get("aria-label") or el.get("aria-labelledby") or el.get("title")
                or (el.find("img") and el.find("img").get("alt")))


def _cyclomatic_complexity(soup) -> tuple[Optional[int], int]:
    """MS4M1 aproximada: (máxima complejidad por bloque de script, nº de funciones)."""
    worst = None
    functions = 0
    for script in soup.find_all("script"):
        if script.get("src") or (script.get("type") or "").lower() not in _JS_TYPES:
            continue
        code = script.string or script.get_text() or ""
        if not code.strip():
            continue
        decisions = len(_DECISION_RE.findall(code))
        n_funcs = max(1, len(_FUNCTION_RE.findall(code)))
        functions += n_funcs
        complexity = round(decisions / n_funcs) + 1   # X = A + 1 por función (promedio del bloque)
        worst = complexity if worst is None else max(worst, complexity)
    return worst, functions


def compute_metrics(soup, html: str, runtime: Optional[dict] = None) -> list[dict]:
    metrics: list[dict] = []

    # ── Accesibilidad (WCAG) ────────────────────────────────────────────────
    images = soup.find_all("img")
    metrics.append(_ratio_metric(
        "ACC-01", "accesibilidad", "Perceptible", "Imágenes con texto alternativo",
        sum(1 for i in images if i.has_attr("alt")), len(images),
        "imágenes con atributo alt", "imágenes totales", reference="WCAG 2.2 · 1.1.1"))

    labeled_ids = {lbl.get("for") for lbl in soup.find_all("label") if lbl.get("for")}
    controls = [c for c in soup.find_all(["input", "select", "textarea"])
                if (c.get("type") or "").lower() not in _NON_LABELED_INPUT_TYPES]
    metrics.append(_ratio_metric(
        "ACC-02", "accesibilidad", "Comprensible", "Controles de formulario etiquetados",
        sum(1 for c in controls if (c.get("id") in labeled_ids) or c.find_parent("label")
            or c.get("aria-label") or c.get("aria-labelledby") or c.get("title")),
        len(controls), "controles con etiqueta o nombre accesible", "controles de formulario",
        reference="WCAG 2.2 · 1.3.1 / 3.3.2"))

    buttons = soup.find_all("button") + soup.find_all(attrs={"role": "button"})
    metrics.append(_ratio_metric(
        "ACC-03", "accesibilidad", "Operable", "Botones con nombre accesible",
        sum(1 for b in buttons if _has_accessible_name(b)), len(buttons),
        "botones con texto/aria-label", "botones", reference="WCAG 2.2 · 4.1.2"))

    links = soup.find_all("a", href=True)
    metrics.append(_ratio_metric(
        "ACC-04", "accesibilidad", "Operable", "Enlaces con texto accesible",
        sum(1 for a in links if _has_accessible_name(a)), len(links),
        "enlaces con texto/aria-label", "enlaces", reference="WCAG 2.2 · 2.4.4"))

    html_tag = soup.find("html")
    metrics.append(_ratio_metric(
        "ACC-05", "accesibilidad", "Comprensible", "Idioma del documento declarado",
        1 if (html_tag and html_tag.get("lang")) else 0, 1,
        "documento con atributo lang", "documento", target=1.0, reference="WCAG 2.2 · 3.1.1"))

    # ── Usabilidad: protección contra errores del usuario ───────────────────
    inputs = [c for c in controls]
    metrics.append(_ratio_metric(
        "USA-01", "usabilidad", "Protección contra errores del usuario", "Campos con validación declarativa",
        sum(1 for c in inputs if c.has_attr("required") or c.has_attr("pattern") or c.has_attr("min")
            or c.has_attr("max") or c.has_attr("maxlength")
            or (c.get("type") or "").lower() in _VALIDATION_TYPES),
        len(inputs), "campos con required/pattern/tipo validado", "campos de entrada", target=0.5))

    has_status = bool(soup.find(attrs={"aria-live": True}) or soup.find(attrs={"role": re.compile("^(alert|status)$")}))
    metrics.append(_ratio_metric(
        "USA-02", "usabilidad", "Protección contra errores del usuario", "Mecanismo de mensajes de estado",
        1 if has_status else 0, 1 if inputs else 0,
        "región aria-live o role=alert/status", "interfaz con formularios", target=1.0))

    # ── Mantenibilidad ─────────────────────────────────────────────────────
    semantic = sum(len(soup.find_all(t)) for t in _SEMANTIC_TAGS)
    divs = len(soup.find_all("div"))
    metrics.append(_ratio_metric(
        "MAN-01", "mantenibilidad", "Modularidad", "Proporción de contenedores semánticos",
        semantic, semantic + divs, "contenedores semánticos HTML5", "contenedores totales (semánticos + div)",
        target=0.1))

    ids = [el.get("id") for el in soup.find_all(attrs={"id": True})]
    metrics.append(_ratio_metric(
        "MAN-02", "mantenibilidad", "Analizabilidad", "Unicidad de identificadores",
        len(set(ids)), len(ids), "identificadores únicos", "identificadores declarados", target=1.0))

    all_elements = soup.find_all(True)
    metrics.append(_ratio_metric(
        "MAN-03", "mantenibilidad", "Capacidad de ser modificado", "Elementos sin estilos inline",
        sum(1 for el in all_elements if not el.get("style")), len(all_elements),
        "elementos sin atributo style", "elementos del DOM", target=0.9))

    complexity, n_functions = _cyclomatic_complexity(soup)
    cc = _value_metric(
        "MS4M1", "mantenibilidad", "Capacidad de ser modificado", "Complejidad ciclomática (aprox.)",
        complexity, "", "1 ≤ X < 15", (complexity is not None and 1 <= complexity < 15),
        "Operacionalización ISO/IEC 25010", formula="X = A + 1 (A = ramificaciones por función)")
    cc["functions_analyzed"] = n_functions
    if complexity is None:
        cc["status"] = "no aplica (sin scripts embebidos)"
    metrics.append(cc)

    # ── Compatibilidad / portabilidad ──────────────────────────────────────
    metrics.append(_ratio_metric(
        "POR-01", "portabilidad", "Adaptabilidad", "Viewport responsive declarado",
        1 if soup.find("meta", attrs={"name": "viewport"}) else 0, 1,
        "meta viewport presente", "documento", target=1.0))

    # ── Eficiencia de desempeño (medida en ejecución) ──────────────────────
    rt = runtime or {}

    def num(key):
        v = rt.get(key)
        return v if isinstance(v, (int, float)) else None

    ttfb, lcp, cls = num("ttfb_ms"), num("lcp_ms"), num("cls")
    transfer, requests, heap = num("transfer_bytes"), num("requests"), num("js_heap_mb")
    ref = "Core Web Vitals (umbral 'bueno')"
    metrics += [
        _value_metric("EFI-01", "eficiencia_desempeno", "Comportamiento temporal", "Tiempo hasta el primer byte (TTFB)",
                      round(ttfb) if ttfb is not None else None, "ms", "X ≤ 800 ms",
                      ttfb is not None and ttfb <= 800, ref),
        _value_metric("EFI-02", "eficiencia_desempeno", "Comportamiento temporal", "Largest Contentful Paint (LCP)",
                      round(lcp) if lcp is not None else None, "ms", "X ≤ 2500 ms",
                      lcp is not None and lcp <= 2500, ref),
        _value_metric("EFI-03", "eficiencia_desempeno", "Comportamiento temporal", "Cumulative Layout Shift (CLS)",
                      cls, "", "X ≤ 0.1", cls is not None and cls <= 0.1, ref),
        _value_metric("EFI-04", "eficiencia_desempeno", "Utilización de recursos", "Datos transferidos",
                      round(transfer / 1024) if transfer is not None else None, "KB", "X ≤ 3000 KB",
                      transfer is not None and transfer <= 3_000 * 1024, "Referencia práctica de peso de página"),
        _value_metric("EFI-05", "eficiencia_desempeno", "Utilización de recursos", "Peticiones de red",
                      requests, "", "X ≤ 100", requests is not None and requests <= 100, "Referencia práctica"),
        _value_metric("EFI-06", "eficiencia_desempeno", "Utilización de recursos", "Memoria JS del cliente",
                      heap, "MB", "X ≤ 50 MB", heap is not None and heap <= 50, "Referencia práctica"),
    ]
    return metrics


def runtime_findings(runtime: Optional[dict]) -> list[tuple[str, str, str, str, str, dict]]:
    """Hallazgos basados en mediciones reales (sólo si se recibieron métricas de ejecución)."""
    if not runtime:
        return []
    out = []

    def num(key):
        v = runtime.get(key)
        return v if isinstance(v, (int, float)) else None

    ttfb, lcp, cls, transfer = num("ttfb_ms"), num("lcp_ms"), num("cls"), num("transfer_bytes")
    if lcp is not None and lcp > 2500:
        sev, pen = ("Alta", 15) if lcp > 4000 else ("Media", 8)
        out.append(("Eficiencia de desempeño", "Comportamiento temporal", sev,
                     f"LCP medido de {lcp / 1000:.1f} s (umbral recomendado ≤ 2.5 s).",
                     "Optimizar la imagen o bloque principal (tamaño, formato, preload) y reducir el JS que bloquea el render.",
                     {"eficiencia_desempeno": pen}))
    if ttfb is not None and ttfb > 800:
        sev, pen = ("Alta", 10) if ttfb > 1800 else ("Media", 5)
        out.append(("Eficiencia de desempeño", "Comportamiento temporal", sev,
                    f"TTFB medido de {round(ttfb)} ms (umbral recomendado ≤ 800 ms).",
                    "Revisar el tiempo de respuesta del servidor, aplicar caché o CDN.",
                    {"eficiencia_desempeno": pen}))
    if cls is not None and cls > 0.1:
        sev, pen = ("Alta", 10) if cls > 0.25 else ("Media", 5)
        out.append(("Usabilidad", "Estabilidad visual", sev,
                    f"CLS medido de {cls} (umbral recomendado ≤ 0.1).",
                    "Reservar espacio para imágenes, anuncios y contenido dinámico (width/height o aspect-ratio).",
                    {"usabilidad": pen, "eficiencia_desempeno": 3}))
    if transfer is not None and transfer > 3_000 * 1024:
        out.append(("Eficiencia de desempeño", "Utilización de recursos", "Media",
                    f"La página transfiere {round(transfer / 1024 / 1024, 1)} MB.",
                    "Comprimir imágenes, dividir el bundle y cargar recursos bajo demanda.",
                    {"eficiencia_desempeno": 8}))
    return out


def normalize_selection(characteristics: Optional[list[str]]) -> list[str]:
    """Subconjunto priorizado de características (restricción 5). Vacío/None = todas."""
    if not characteristics:
        return list(CHARACTERISTICS)
    selected = [c for c in characteristics if c in CHARACTERISTICS]
    return selected or list(CHARACTERISTICS)
