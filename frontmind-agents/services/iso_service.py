"""
services/iso_service.py — Evaluación ISO/IEC 25010:2023 de una interfaz.

Entradas
  html               DOM original de la interfaz (no su réplica).
  runtime_metrics    métricas de desempeño y contraste medidas por Playwright.
  evidence           evidencias de ejecución (services/evidence_collector.py).
  characteristics    subconjunto a puntuar (por defecto las seis núcleo).
  expected_functions funciones que la interfaz debe ofrecer (completitud y
                     pertinencia funcional); opcional.

Cada puntaje se deriva de métricas trazables (services/iso_framework.py) y cada
hallazgo corresponde a una métrica que no alcanzó su meta.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from services.iso_framework import (
    CHARACTERISTICS,
    SEVERITY_GRADES,
    apply_impact,
    decision_criterion,
    evaluation_restrictions,
    evaluation_scope,
    findings_from_metrics,
    make_metric,
    normalize_selection,
    normalize_text,
    score_characteristics,
)

RUNTIME = "no medido (requiere captura en ejecución)"
WCAG = "WCAG 2.2"
OWASP = "OWASP Secure Headers / ASVS 4.0"

_NON_LABELED_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
_VALIDATION_TYPES = {"email", "number", "url", "tel", "date", "datetime-local", "month", "week", "time", "range"}
_NO_VALIDATION_NEEDED = {"checkbox", "radio", "color", "file", "range"}
_PERSONAL_TYPES = {"email", "tel", "password"}
_PERSONAL_NAME_RE = re.compile(
    r"(name|nombre|apellido|email|e-mail|correo|phone|telefono|teléfono|celular|tel\b|address|direcci|"
    r"user|usuario|login|zip|postal|cc-|birth|nacimiento|dni|city|ciudad|country|pais|país)", re.I)
_VALIDATION_ATTRS = ("required", "pattern", "min", "max", "minlength", "maxlength")


def get_element_snippet(el) -> str:
    if not getattr(el, "name", None):
        return ""
    attrs = []
    for attr in ("id", "class", "name", "type", "src", "href"):
        value = el.get(attr)
        if value:
            value = " ".join(value) if isinstance(value, list) else str(value)
            attrs.append(f'{attr}="{value[:50]}"')
    return f"<{el.name}{(' ' + ' '.join(attrs)) if attrs else ''}>"


def _snippets(elements, n=3) -> list[str]:
    return [s for s in (get_element_snippet(e) for e in elements[:n]) if s]


def _accessible_name(el, soup) -> bool:
    if el.get_text(strip=True) or el.get("aria-label", "").strip() or el.get("title", "").strip():
        return True
    labelledby = el.get("aria-labelledby", "")
    if labelledby and any(soup.find(id=i) for i in labelledby.split()):
        return True
    if el.name == "input" and el.get("value", "").strip():
        return True
    img = el.find("img")
    if img is not None and img.get("alt", "").strip():
        return True
    svg = el.find("svg")
    return bool(svg is not None and (svg.get("aria-label") or svg.find("title")))


def _is_hidden(el) -> bool:
    return (el.get("aria-hidden") == "true" or el.get("role") in ("presentation", "none")
            or el.has_attr("hidden"))


def _control_texts(soup) -> list[str]:
    """Nombres visibles o accesibles de los controles operables."""
    labels = {lbl.get("for"): lbl.get_text(" ", strip=True) for lbl in soup.find_all("label") if lbl.get("for")}
    texts = []
    selector = ["a", "button", "input", "select", "textarea", "summary"]
    for el in soup.find_all(selector) + soup.find_all(attrs={"role": re.compile("^(button|link|tab|menuitem)$")}):
        if el.name == "a" and not el.get("href"):
            continue
        parts = [el.get_text(" ", strip=True), el.get("aria-label", ""), el.get("title", ""),
                 el.get("placeholder", ""), el.get("value", "") if el.name == "input" else "",
                 labels.get(el.get("id"), "")]
        if el.find("img"):
            parts.append(el.find("img").get("alt", ""))
        parent_label = el.find_parent("label")
        if parent_label is not None:
            parts.append(parent_label.get_text(" ", strip=True))
        texts.append(normalize_text(" ".join(p for p in parts if p)))
    return texts


def _page_corpus(soup) -> str:
    parts = [soup.get_text(" ", strip=True)]
    for el in soup.find_all(attrs={"aria-label": True}):
        parts.append(el["aria-label"])
    for el in soup.find_all(["input", "img"]):
        parts.extend([el.get("placeholder", ""), el.get("alt", ""), el.get("value", "")])
    return normalize_text(" ".join(parts))


def _viewport_content(soup) -> Optional[str]:
    meta = soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)})
    return (meta.get("content") or "") if meta is not None else None


def _zoom_blocked(content: Optional[str]) -> bool:
    if not content:
        return False
    c = content.lower().replace(" ", "")
    if re.search(r"user-scalable=(no|0)\b", c):
        return True
    m = re.search(r"maximum-scale=([\d.]+)", c)
    return bool(m and float(m.group(1)) < 2)


# ─────────────────────────────────────────────────────────────────────────────
# Métricas por característica
# ─────────────────────────────────────────────────────────────────────────────

def _functional_suitability(soup, ev, expected) -> list[dict]:
    metrics = []
    expected = [normalize_text(e) for e in (expected or []) if normalize_text(e)]
    spec_missing = "no evaluado (requiere la lista de funciones esperadas)"
    if expected:
        corpus = _page_corpus(soup)
        controls = _control_texts(soup)
        found = [e for e in expected if e in corpus]
        operable = [e for e in expected if any(e in t for t in controls)]
        missing = [e for e in expected if e not in found]
        not_operable = [e for e in expected if e not in operable]
    else:
        found = operable = missing = not_operable = []
    n = len(expected) or None

    metrics.append(make_metric(
        "AF-01", "adecuacion_funcional", "Completitud funcional", "Funciones esperadas presentes",
        kind="ratio", a=len(found) if n else None, b=n, reference="ISO/IEC 25023 · cobertura funcional",
        not_measured=spec_missing,
        finding=f"{len(missing)} de {n} funciones esperadas no aparecen en la interfaz: {', '.join(missing[:5])}." if n else "",
        recommendation="Implementar o hacer visibles las funciones requeridas por la especificación."))
    metrics.append(make_metric(
        "AF-04", "adecuacion_funcional", "Pertinencia funcional", "Funciones esperadas disponibles como control operable",
        kind="ratio", a=len(operable) if n else None, b=n, reference="ISO/IEC 25023 · pertinencia funcional",
        not_measured=spec_missing,
        finding=(f"{len(not_operable)} de {n} funciones esperadas no tienen un enlace, botón o campo que permita "
                 f"ejecutarlas: {', '.join(not_operable[:5])}.") if n else "",
        recommendation="Ofrecer cada función principal mediante un control directo (botón, enlace o formulario) con nombre claro."))

    links = (ev or {}).get("links") or {}
    checked, broken = links.get("checked"), links.get("broken", 0)
    metrics.append(make_metric(
        "AF-02", "adecuacion_funcional", "Corrección funcional", "Enlaces internos que responden sin error",
        kind="ratio", a=(checked - broken) if checked else None, b=checked or None,
        reference="ISO/IEC 25023 · corrección funcional",
        not_measured=RUNTIME if not links else "no aplica (sin enlaces internos)",
        finding=f"{broken} de {checked} enlaces internos responden con error o no responden.",
        recommendation="Corregir o eliminar los enlaces rotos y configurar redirecciones para rutas movidas.",
        examples=links.get("samples")))

    images = ((ev or {}).get("page") or {}).get("images") or {}
    total, broken_img = images.get("total"), images.get("broken", 0)
    metrics.append(make_metric(
        "AF-03", "adecuacion_funcional", "Corrección funcional", "Imágenes de contenido que cargan",
        kind="ratio", a=(total - broken_img) if total else None, b=total or None,
        reference="ISO/IEC 25023 · corrección funcional",
        not_measured=RUNTIME if not images else "no aplica (sin imágenes)",
        finding=f"{broken_img} de {total} imágenes no cargan (recurso inexistente o inaccesible).",
        recommendation="Verificar las rutas de las imágenes y su disponibilidad en el servidor o CDN.",
        examples=images.get("samples")))
    return metrics


def _interaction_capability(soup, rt, ev) -> list[dict]:
    m = []
    char = "capacidad_interaccion"
    incl = "Inclusividad"

    images = [i for i in soup.find_all("img") if not _is_hidden(i)]
    no_alt = [i for i in images if not i.has_attr("alt")]
    m.append(make_metric("CI-01", char, incl, "Imágenes con texto alternativo", kind="ratio", target=0.9,
                         a=len(images) - len(no_alt), b=len(images) or None, reference=f"{WCAG} · 1.1.1",
                         not_measured="no aplica (sin imágenes)",
                         finding=f"{len(no_alt)} de {len(images)} imágenes no tienen atributo alt.",
                         recommendation="Agregar alt descriptivo a imágenes informativas y alt=\"\" a las decorativas.",
                         examples=_snippets(no_alt)))

    labeled_ids = {lbl.get("for") for lbl in soup.find_all("label") if lbl.get("for")}
    controls = [c for c in soup.find_all(["input", "select", "textarea"])
                if (c.get("type") or "").lower() not in _NON_LABELED_INPUT_TYPES and not _is_hidden(c)]
    unlabeled = [c for c in controls if not (
        (c.get("id") and c.get("id") in labeled_ids) or c.find_parent("label") is not None
        or c.get("aria-label", "").strip() or c.get("aria-labelledby") or c.get("title", "").strip())]
    m.append(make_metric("CI-02", char, incl, "Controles de formulario etiquetados", kind="ratio", target=0.9,
                         a=len(controls) - len(unlabeled), b=len(controls) or None,
                         reference=f"{WCAG} · 1.3.1 / 3.3.2 / 4.1.2", not_measured="no aplica (sin formularios)",
                         finding=f"{len(unlabeled)} de {len(controls)} campos no tienen etiqueta accesible "
                                 "(el placeholder no la sustituye).",
                         recommendation="Asociar cada campo a un <label for> o usar aria-label / aria-labelledby.",
                         examples=_snippets(unlabeled)))

    buttons = [b for b in soup.find_all("button") + soup.find_all(attrs={"role": "button"})
               + soup.find_all("input", attrs={"type": re.compile("^(submit|button|reset)$", re.I)})
               if not _is_hidden(b)]
    nameless = [b for b in buttons if not _accessible_name(b, soup)]
    m.append(make_metric("CI-03", char, incl, "Botones con nombre accesible", kind="ratio", target=0.9,
                         a=len(buttons) - len(nameless), b=len(buttons) or None, reference=f"{WCAG} · 4.1.2",
                         not_measured="no aplica (sin botones)",
                         finding=f"{len(nameless)} de {len(buttons)} botones no tienen nombre accesible.",
                         recommendation="Dar a cada botón texto visible, aria-label o un ícono con texto alternativo.",
                         examples=_snippets(nameless)))

    links = [a for a in soup.find_all("a", href=True) if not _is_hidden(a)]
    nameless_links = [a for a in links if not _accessible_name(a, soup)]
    m.append(make_metric("CI-04", char, incl, "Enlaces con nombre accesible", kind="ratio", target=0.9,
                         a=len(links) - len(nameless_links), b=len(links) or None, reference=f"{WCAG} · 2.4.4",
                         not_measured="no aplica (sin enlaces)",
                         finding=f"{len(nameless_links)} de {len(links)} enlaces no tienen texto ni nombre accesible.",
                         recommendation="Agregar texto descriptivo o aria-label a los enlaces (también a los de ícono).",
                         examples=_snippets(nameless_links)))

    html_tag = soup.find("html")
    m.append(make_metric("CI-05", char, incl, "Idioma del documento declarado", kind="binary",
                         x=1 if (html_tag is not None and html_tag.get("lang", "").strip()) else 0,
                         reference=f"{WCAG} · 3.1.1",
                         finding="El documento no declara su idioma (atributo lang en <html>).",
                         recommendation="Agregar lang=\"es\" (o el idioma correspondiente) al elemento <html>."))

    checked = (rt or {}).get("contrast_checked")
    failures = (rt or {}).get("contrast_failures") or 0
    m.append(make_metric("CI-06", char, incl, "Texto con contraste suficiente", kind="ratio", target=0.9,
                         a=(checked - failures) if checked else None, b=checked or None,
                         reference=f"{WCAG} · 1.4.3", not_measured=RUNTIME,
                         finding=f"{failures} de {checked} elementos de texto no alcanzan el contraste mínimo "
                                 "(4.5:1, o 3:1 en texto grande).",
                         recommendation="Oscurecer el texto o aclarar el fondo hasta cumplir 4.5:1 (3:1 en texto grande)."))

    viewport = _viewport_content(soup)
    m.append(make_metric("CI-07", char, incl, "Zoom del usuario permitido", kind="binary",
                         x=0 if _zoom_blocked(viewport) else 1, reference=f"{WCAG} · 1.4.4",
                         finding=f"El meta viewport impide ampliar la página ({viewport}).",
                         recommendation="Eliminar user-scalable=no y maximum-scale menor a 2 del meta viewport."))

    mobile = (((ev or {}).get("layout") or {}).get("mobile")) or {}
    targets, small = mobile.get("targets"), mobile.get("small_targets", 0)
    m.append(make_metric("CI-08", char, "Operabilidad", "Objetivos táctiles de al menos 24×24 px (móvil)",
                         kind="ratio", target=0.9, a=(targets - small) if targets else None, b=targets or None,
                         reference=f"{WCAG} · 2.5.8", not_measured=RUNTIME if not mobile else "no aplica (sin controles)",
                         finding=f"{small} de {targets} controles miden menos de 24×24 px en móvil (390 px).",
                         recommendation="Aumentar el área táctil (padding o min-width/min-height de 24 px; 44 px recomendado).",
                         examples=mobile.get("small_samples")))

    positive_tab = [t for t in soup.find_all(attrs={"tabindex": True})
                    if str(t.get("tabindex")).strip().isdigit() and int(t.get("tabindex")) > 0]
    m.append(make_metric("CI-09", char, "Operabilidad", "Orden de foco natural (sin tabindex positivo)",
                         kind="binary", x=0 if positive_tab else 1, reference=f"{WCAG} · 2.4.3",
                         finding=f"{len(positive_tab)} elementos usan tabindex mayor a 0 y alteran el orden de foco.",
                         recommendation="Usar tabindex=\"0\" o \"-1\" y ordenar el DOM según el orden lógico.",
                         examples=_snippets(positive_tab)))

    entry = [c for c in controls if (c.get("type") or "text").lower() not in _NO_VALIDATION_NEEDED]
    validated = [c for c in entry if any(c.has_attr(a) for a in _VALIDATION_ATTRS)
                 or (c.get("type") or "").lower() in _VALIDATION_TYPES or c.name == "select"]
    m.append(make_metric("CI-10", char, "Protección contra errores del usuario", "Campos con validación declarativa",
                         kind="ratio", target=0.5, a=len(validated), b=len(entry) or None,
                         reference="ISO/IEC 25023 · protección contra errores", not_measured="no aplica (sin campos)",
                         finding=f"Sólo {len(validated)} de {len(entry)} campos declaran validación "
                                 "(required, pattern, min/max, longitud o tipo).",
                         recommendation="Declarar required, pattern, minlength/maxlength o tipos como email/tel/number.",
                         examples=_snippets([c for c in entry if c not in validated])))

    personal = [c for c in controls if c.name == "input" and (
        (c.get("type") or "").lower() in _PERSONAL_TYPES
        or _PERSONAL_NAME_RE.search(f"{c.get('name', '')} {c.get('id', '')}"))]
    with_ac = [c for c in personal if (c.get("autocomplete") or "").strip().lower() not in ("", "off")]
    m.append(make_metric("CI-11", char, "Protección contra errores del usuario",
                         "Campos de datos personales con autocompletado", kind="ratio", target=0.9,
                         a=len(with_ac), b=len(personal) or None, reference=f"{WCAG} · 1.3.5",
                         not_measured="no aplica (sin campos de datos personales)",
                         finding=f"{len(personal) - len(with_ac)} de {len(personal)} campos de datos personales "
                                 "no declaran su propósito con autocomplete.",
                         recommendation="Agregar autocomplete (email, tel, name, username, current-password, new-password…).",
                         examples=_snippets([c for c in personal if c not in with_ac])))

    has_status = bool(soup.find(attrs={"aria-live": True}) or soup.find(attrs={"role": re.compile("^(alert|status)$")}))
    m.append(make_metric("CI-12", char, "Asistencia al usuario", "Región de mensajes de estado",
                         kind="binary", x=(1 if has_status else 0) if controls else None,
                         reference=f"{WCAG} · 4.1.3", not_measured="no aplica (sin formularios)",
                         finding="La interfaz tiene formularios pero ninguna región que anuncie mensajes de estado o error.",
                         recommendation="Mostrar errores y confirmaciones en un contenedor con role=\"alert\" o aria-live."))

    title = soup.find("title")
    m.append(make_metric("CI-13", char, "Autodescriptividad", "Título de página descriptivo", kind="binary",
                         x=1 if (title is not None and title.get_text(strip=True)) else 0, reference=f"{WCAG} · 2.4.2",
                         finding="La interfaz no tiene un <title> que describa su propósito.",
                         recommendation="Definir un <title> único por interfaz (p. ej. \"Pagos · Mi sistema\")."))

    has_h1 = bool(soup.find("h1") or soup.find(attrs={"role": "heading", "aria-level": "1"}))
    m.append(make_metric("CI-14", char, "Autodescriptividad", "Encabezado principal presente", kind="binary",
                         x=1 if has_h1 else 0, reference=f"{WCAG} · 1.3.1 / 2.4.6",
                         finding="No hay un encabezado principal (<h1>) que identifique el contenido.",
                         recommendation="Agregar un <h1> con el propósito de la interfaz y jerarquizar con <h2>, <h3>."))

    texts, tiny = mobile.get("text_elements"), mobile.get("small_text", 0)
    m.append(make_metric("CI-15", char, "Operabilidad", "Texto legible en móvil (≥ 12 px)", kind="ratio",
                         target=0.6, a=(texts - tiny) if texts else None, b=texts or None,
                         reference="Lighthouse · Legible font sizes", not_measured=RUNTIME if not mobile else "no aplica",
                         finding=f"{tiny} de {texts} bloques de texto miden menos de 12 px en móvil.",
                         recommendation="Usar un tamaño base de 16 px y no bajar de 12 px en textos secundarios."))
    return m


def _compatibility(ev) -> list[dict]:
    m = []
    char = "compatibilidad"
    req = (ev or {}).get("requests") or {}
    api_total, api_failed = req.get("api_total"), req.get("api_failed", 0)
    m.append(make_metric("CO-01", char, "Interoperabilidad", "Peticiones a API completadas sin error", kind="ratio",
                         target=0.95, a=(api_total - api_failed) if api_total else None, b=api_total or None,
                         reference="ISO/IEC 25023 · interoperabilidad",
                         not_measured=RUNTIME if not req else "no aplica (sin peticiones a API)",
                         finding=f"{api_failed} de {api_total} peticiones a API (fetch/XHR) fallaron o devolvieron error.",
                         recommendation="Revisar los endpoints, CORS y formatos de intercambio con los servicios externos.",
                         examples=req.get("failed_samples")))

    cb = (ev or {}).get("cross_browser") or {}
    chromium = cb.get("chromium") or {}
    others = {k: v for k, v in cb.items() if k != "chromium" and v.get("available") and not v.get("session_lost")}
    base_errors = chromium.get("js_errors", 0) or 0
    loads = [k for k, v in others.items() if v.get("loaded") and (v.get("js_errors", 0) or 0) <= base_errors]
    failing = [k for k in others if k not in loads]
    tested = (len(others) + 1) if (others and chromium.get("loaded")) else None
    m.append(make_metric("CO-02", char, "Interoperabilidad", "Navegadores donde la interfaz funciona sin errores nuevos",
                         kind="ratio", a=(len(loads) + 1) if tested else None, b=tested,
                         reference="ISO/IEC 25023 · compatibilidad entre plataformas",
                         not_measured="no medido (navegadores adicionales no disponibles)" if cb else RUNTIME,
                         finding="La interfaz no carga o genera errores JavaScript adicionales en: "
                                 + ", ".join(failing) + ".",
                         recommendation="Probar en Firefox y Safari (WebKit), revisar APIs no estándar y agregar polyfills.",
                         examples=[f"{k}: {(others[k].get('js_error_samples') or [others[k].get('error', '')])[0]}"
                                   for k in failing if others[k].get('js_error_samples') or others[k].get('error')]))

    def coherent(v):
        if not v.get("loaded"):
            return False
        if v.get("overflow_desktop") and not chromium.get("overflow_desktop"):
            return False
        if v.get("overflow_mobile") and not chromium.get("overflow_mobile"):
            return False
        h, h0 = v.get("height") or 0, chromium.get("height") or 0
        return not (h0 and abs(h - h0) / h0 > 0.25)

    loaded_others = {k: v for k, v in others.items() if v.get("loaded")}
    incoherent = [k for k, v in loaded_others.items() if not coherent(v)]
    m.append(make_metric("CO-03", char, "Interoperabilidad", "Diseño coherente con Chromium en otros motores",
                         kind="ratio", a=(len(loaded_others) - len(incoherent)) if loaded_others else None,
                         b=len(loaded_others) or None, reference="ISO/IEC 25023 · compatibilidad entre plataformas",
                         not_measured="no medido (navegadores adicionales no disponibles)" if cb else RUNTIME,
                         finding="El diseño cambia de forma significativa (desbordamiento o alto ±25 %) en: "
                                 + ", ".join(incoherent) + ".",
                         recommendation="Revisar propiedades CSS sin soporte uniforme y usar prefijos o alternativas."))

    globals_ = (((ev or {}).get("page") or {}).get("globals")) or {}
    count = globals_.get("count")
    m.append(make_metric("CO-04", char, "Coexistencia", "Variables globales añadidas al navegador", kind="max",
                         target=50, x=count, reference="Referencia práctica (aislamiento de módulos)", weight=0.5,
                         not_measured=RUNTIME,
                         finding=f"La interfaz añade {count} variables globales a window, que pueden colisionar con "
                                 "otros scripts del mismo entorno.",
                         recommendation="Encapsular el código en módulos ES y evitar asignaciones a window.",
                         examples=globals_.get("samples")))
    return m


def _flexibility(soup, ev) -> list[dict]:
    m = []
    char = "flexibilidad"
    m.append(make_metric("FL-01", char, "Adaptabilidad", "Meta viewport adaptable declarado", kind="binary",
                         x=1 if _viewport_content(soup) else 0, reference="HTML Living Standard · viewport",
                         finding="No se declara <meta name=\"viewport\">: los móviles muestran la versión de escritorio reducida.",
                         recommendation="Agregar <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">."))

    layout = (ev or {}).get("layout") or {}
    measured = {d: layout[d] for d in ("desktop", "tablet", "mobile") if layout.get(d)}
    overflowing = [d for d, v in measured.items() if v.get("overflow")]
    m.append(make_metric("FL-02", char, "Adaptabilidad", "Resoluciones sin desplazamiento horizontal", kind="ratio",
                         a=(len(measured) - len(overflowing)) if measured else None, b=len(measured) or None,
                         reference="ISO/IEC 25023 · adaptabilidad", not_measured=RUNTIME,
                         finding="La interfaz desborda horizontalmente en: " + ", ".join(
                             f"{d} ({measured[d].get('scroll_width')} px en {measured[d].get('width')} px)"
                             for d in overflowing) + ".",
                         recommendation="Usar unidades relativas, max-width: 100% y diseños flex/grid que se reacomoden."))

    reflow = layout.get("reflow_320")
    m.append(make_metric("FL-03", char, "Adaptabilidad", "Reflow a 320 px sin desplazamiento horizontal",
                         kind="binary", x=(0 if reflow.get("overflow") else 1) if reflow else None,
                         reference=f"{WCAG} · 1.4.10", not_measured=RUNTIME,
                         finding=f"A 320 px de ancho el contenido mide {(reflow or {}).get('scroll_width')} px "
                                 "y obliga a desplazarse en dos direcciones.",
                         recommendation="Permitir que tablas, imágenes y barras se reacomoden o desplacen dentro de su contenedor."))

    manifest = ((ev or {}).get("page") or {}).get("manifest")
    if manifest is None:
        manifest = bool(soup.find("link", attrs={"rel": "manifest"}))
    m.append(make_metric("FL-04", char, "Instalabilidad", "Manifiesto de aplicación web instalable", kind="binary",
                         x=1 if manifest else 0, scored=False, reference="W3C Web App Manifest",
                         finding="", recommendation=""))
    return m


def _security(soup, ev) -> list[dict]:
    m = []
    char = "seguridad"
    conf, integ = "Confidencialidad", "Integridad"
    ev = ev or {}
    nav = ev.get("navigation") or {}
    https = nav.get("https") if nav else None
    headers = ev.get("headers")
    page = ev.get("page") or {}
    no_https = "no aplica (la interfaz no usa HTTPS)"

    m.append(make_metric("SE-01", char, conf, "Conexión cifrada (HTTPS)", kind="binary",
                         x=None if https is None else int(https), reference=f"{OWASP} · V9.1", not_measured=RUNTIME,
                         finding="La interfaz se sirve por HTTP sin cifrar: los datos viajan legibles por la red.",
                         recommendation="Servir todo el sitio por HTTPS con un certificado válido."))

    tls = ev.get("tls") or {}
    m.append(make_metric("SE-02", char, conf, "Certificado TLS válido", kind="binary",
                         x=None if tls.get("valid") is None else int(tls["valid"]), reference=f"{OWASP} · V9.1",
                         not_measured=no_https if https is False else RUNTIME,
                         finding=f"El certificado TLS no es válido: {tls.get('error', '')}.",
                         recommendation="Renovar el certificado e incluir la cadena intermedia completa."))

    def header(name):
        return (headers or {}).get(name, "") if headers is not None else None

    hsts = header("hsts")
    m.append(make_metric("SE-03", char, conf, "HSTS (Strict-Transport-Security)", kind="binary",
                         x=None if (hsts is None or not https) else int(bool(hsts)), reference=f"{OWASP} · V14.4.5",
                         not_measured=no_https if https is False else RUNTIME,
                         finding="El servidor no envía Strict-Transport-Security; el primer acceso puede degradarse a HTTP.",
                         recommendation="Enviar Strict-Transport-Security: max-age=31536000; includeSubDomains."))

    redirect = ev.get("http_redirects_to_https")
    m.append(make_metric("SE-04", char, conf, "Redirección de HTTP a HTTPS", kind="binary",
                         x=None if redirect is None else int(redirect), reference=f"{OWASP} · V9.1",
                         not_measured=no_https if https is False else "no medido (puerto 80 sin respuesta)",
                         finding="La versión http:// del sitio responde sin redirigir a HTTPS.",
                         recommendation="Redirigir con 301 todo el tráfico HTTP a HTTPS."))

    forms = page.get("password_forms") or {}
    total_forms = forms.get("total") or 0
    insecure = total_forms if https is False else (forms.get("insecure") or 0)
    m.append(make_metric("SE-05", char, conf, "Formularios de contraseña enviados por HTTPS y POST", kind="ratio",
                         a=(total_forms - insecure) if total_forms else None, b=total_forms or None,
                         reference=f"{OWASP} · V8.3.1",
                         not_measured="no aplica (sin formularios de contraseña)" if forms else RUNTIME,
                         finding=f"{insecure} de {total_forms} formularios con contraseña se envían sin HTTPS o por GET "
                                 "(la contraseña queda expuesta en la red o en la URL).",
                         recommendation="Enviar las credenciales sólo por POST a un destino HTTPS."))

    mixed = ev.get("mixed_content") or {}
    m.append(make_metric("SE-06", char, conf, "Recursos sin contenido mixto", kind="count",
                         x=mixed.get("count") if (mixed and https) else None, reference="W3C Mixed Content",
                         not_measured=no_https if https is False else RUNTIME,
                         finding=f"La página HTTPS solicita {mixed.get('count')} recursos por HTTP sin cifrar.",
                         recommendation="Cargar todos los recursos por HTTPS (o agregar upgrade-insecure-requests a la CSP).",
                         examples=mixed.get("samples")))

    cookies = ev.get("cookies") or {}
    m.append(make_metric("SE-07", char, conf, "Cookies con atributo Secure", kind="ratio",
                         a=cookies.get("secure") if (https and cookies.get("total")) else None,
                         b=cookies.get("total") if https else None, reference=f"{OWASP} · V3.4.1",
                         not_measured=no_https if https is False else ("no aplica (sin cookies)" if cookies else RUNTIME),
                         finding=f"{cookies.get('total', 0) - cookies.get('secure', 0)} de {cookies.get('total')} cookies "
                                 "no tienen el atributo Secure.",
                         recommendation="Marcar las cookies como Secure (y HttpOnly/SameSite las de sesión).",
                         examples=cookies.get("insecure_samples")))

    creds = page.get("storage_credentials")
    m.append(make_metric("SE-08", char, conf, "Credenciales fuera de Web Storage", kind="binary",
                         x=None if creds is None else int(creds.get("count", 0) == 0), reference=f"{OWASP} · V3.2.3",
                         not_measured=RUNTIME,
                         finding=f"Se guardan {(creds or {}).get('count')} tokens o credenciales en localStorage/"
                                 "sessionStorage, accesibles para cualquier script (riesgo ante XSS).",
                         recommendation="Mantener los tokens de sesión en cookies HttpOnly, Secure y SameSite.",
                         examples=(creds or {}).get("keys")))

    csp = header("csp")
    meta_csp = page.get("meta_csp") or ""
    csp_value = (csp or "") or meta_csp
    m.append(make_metric("SE-09", char, integ, "Content-Security-Policy definida", kind="binary",
                         x=None if (headers is None and not meta_csp) else int(bool(csp_value)),
                         reference=f"{OWASP} · V14.4.3", not_measured=RUNTIME,
                         finding="No se define Content-Security-Policy: el navegador no limita el origen de scripts.",
                         recommendation="Definir una CSP (al menos default-src 'self'; script-src con orígenes explícitos)."))

    xfo = header("x_frame_options")
    m.append(make_metric("SE-10", char, integ, "Protección contra clickjacking", kind="binary",
                         x=None if headers is None else int(bool(xfo) or "frame-ancestors" in (csp or "")),
                         reference=f"{OWASP} · V14.4.7", not_measured=RUNTIME,
                         finding="La interfaz puede incrustarse en sitios ajenos (sin X-Frame-Options ni frame-ancestors).",
                         recommendation="Enviar X-Frame-Options: DENY o CSP frame-ancestors 'self'."))

    nosniff = header("x_content_type_options")
    m.append(make_metric("SE-11", char, integ, "X-Content-Type-Options: nosniff", kind="binary",
                         x=None if headers is None else int((nosniff or "").lower() == "nosniff"),
                         reference=f"{OWASP} · V14.4.4", not_measured=RUNTIME,
                         finding="Falta X-Content-Type-Options: nosniff (el navegador puede reinterpretar tipos de archivo).",
                         recommendation="Enviar X-Content-Type-Options: nosniff en todas las respuestas."))

    third = page.get("third_party_scripts") or {}
    m.append(make_metric("SE-12", char, integ, "Scripts de terceros con integridad verificada (SRI)", kind="ratio",
                         a=third.get("with_sri") if third.get("total") else None, b=third.get("total") or None,
                         weight=0.5, reference=f"{OWASP} · V14.2.3",
                         not_measured="no aplica (sin scripts de terceros)" if third else RUNTIME,
                         finding=f"{third.get('total', 0) - third.get('with_sri', 0)} de {third.get('total')} scripts de "
                                 "terceros se cargan sin atributo integrity.",
                         recommendation="Agregar integrity y crossorigin a los scripts de CDN con versión fija.",
                         examples=third.get("samples")))

    meta_ref = soup.find("meta", attrs={"name": re.compile("^referrer$", re.I)})
    ref_policy = header("referrer_policy")
    m.append(make_metric("SE-13", char, conf, "Política de referencia (Referrer-Policy)", kind="binary",
                         x=None if (headers is None and meta_ref is None) else int(bool(ref_policy) or meta_ref is not None),
                         weight=0.5, reference=f"{OWASP} · V14.4.6", not_measured=RUNTIME,
                         finding="No se define Referrer-Policy: las URL completas pueden filtrarse a sitios externos.",
                         recommendation="Enviar Referrer-Policy: strict-origin-when-cross-origin (o no-referrer)."))
    return m


def _reliability(ev) -> list[dict]:
    m = []
    char = "fiabilidad"
    ev = ev or {}
    status = (ev.get("navigation") or {}).get("status")
    m.append(make_metric("FI-01", char, "Disponibilidad", "La interfaz responde sin error HTTP", kind="binary",
                         x=None if status is None else int(status < 400), reference="ISO/IEC 25023 · disponibilidad",
                         not_measured=RUNTIME,
                         finding=f"La interfaz respondió con el código HTTP {status}.",
                         recommendation="Revisar el servidor o la ruta: la interfaz no está disponible para el usuario."))

    js = ev.get("js_errors")
    m.append(make_metric("FI-02", char, "Ausencia de fallos", "Errores JavaScript no capturados", kind="count",
                         x=js.get("count") if js else None, reference="ISO/IEC 25023 · ausencia de fallos",
                         not_measured=RUNTIME,
                         finding=f"Se produjeron {(js or {}).get('count')} errores JavaScript no capturados al cargar la interfaz.",
                         recommendation="Corregir los errores y agregar manejo de excepciones (try/catch, Error Boundaries).",
                         examples=(js or {}).get("samples")))

    console = ev.get("console_errors")
    m.append(make_metric("FI-03", char, "Ausencia de fallos", "Errores registrados en consola", kind="count",
                         x=console.get("count") if console else None, weight=0.5,
                         reference="ISO/IEC 25023 · ausencia de fallos", not_measured=RUNTIME,
                         finding=f"La consola registró {(console or {}).get('count')} errores durante la carga.",
                         recommendation="Revisar y resolver los errores registrados en la consola del navegador.",
                         examples=(console or {}).get("samples")))

    req = ev.get("requests") or {}
    total, failed = req.get("total"), req.get("failed", 0)
    m.append(make_metric("FI-04", char, "Tolerancia a fallos", "Recursos cargados sin error", kind="ratio",
                         target=0.98, a=(total - failed) if total else None, b=total or None,
                         reference="ISO/IEC 25023 · tolerancia a fallos", not_measured=RUNTIME,
                         finding=f"{failed} de {total} recursos (scripts, estilos, imágenes o API) fallaron al cargar.",
                         recommendation="Corregir los recursos que fallan y prever alternativas cuando un servicio no responde.",
                         examples=req.get("failed_samples")))
    return m


def _efficiency(rt) -> list[dict]:
    rt = rt or {}

    def num(key):
        v = rt.get(key)
        return v if isinstance(v, (int, float)) else None

    char, temporal, resources = "eficiencia_desempeno", "Comportamiento temporal", "Utilización de recursos"
    cwv = "Core Web Vitals (umbral 'bueno')"
    ttfb, lcp, cls = num("ttfb_ms"), num("lcp_ms"), num("cls")
    transfer, requests, heap = num("transfer_bytes"), num("requests"), num("js_heap_mb")
    return [
        make_metric("EF-01", char, temporal, "Tiempo hasta el primer byte (TTFB)", kind="max", target=800, unit="ms",
                    x=round(ttfb) if ttfb is not None else None, reference=cwv, not_measured=RUNTIME,
                    finding=f"TTFB medido de {round(ttfb or 0)} ms.",
                    recommendation="Reducir el tiempo de respuesta del servidor (caché, CDN, consultas)."),
        make_metric("EF-02", char, temporal, "Largest Contentful Paint (LCP)", kind="max", target=2500, unit="ms",
                    x=round(lcp) if lcp is not None else None, reference=cwv, not_measured=RUNTIME,
                    finding=f"LCP medido de {(lcp or 0) / 1000:.1f} s.",
                    recommendation="Optimizar la imagen o bloque principal y reducir el JS que bloquea el render."),
        make_metric("EF-03", char, temporal, "Cumulative Layout Shift (CLS)", kind="max", target=0.1, x=cls,
                    reference=cwv, not_measured=RUNTIME, finding=f"CLS medido de {cls}.",
                    recommendation="Reservar espacio para imágenes y contenido dinámico (width/height o aspect-ratio)."),
        make_metric("EF-04", char, resources, "Datos transferidos", kind="max", target=3000, unit="KB",
                    x=round(transfer / 1024) if transfer is not None else None,
                    reference="Referencia práctica de peso de página", not_measured=RUNTIME,
                    finding=f"La página transfiere {round((transfer or 0) / 1024)} KB.",
                    recommendation="Comprimir imágenes, dividir el bundle y cargar recursos bajo demanda."),
        make_metric("EF-05", char, resources, "Peticiones de red", kind="max", target=100, x=requests,
                    reference="Referencia práctica", not_measured=RUNTIME,
                    finding=f"La página realiza {requests} peticiones.",
                    recommendation="Agrupar recursos y eliminar dependencias innecesarias."),
        make_metric("EF-06", char, resources, "Memoria JS del cliente", kind="max", target=50, unit="MB", x=heap,
                    reference="Referencia práctica", not_measured=RUNTIME,
                    finding=f"La página usa {heap} MB de memoria JavaScript.",
                    recommendation="Liberar referencias y reducir el estado y las librerías cargadas."),
    ]


def compute_metrics(soup, runtime=None, evidence=None, expected_functions=None) -> list[dict]:
    return apply_impact(
        _functional_suitability(soup, evidence, expected_functions)
        + _interaction_capability(soup, runtime, evidence)
        + _compatibility(evidence)
        + _flexibility(soup, evidence)
        + _security(soup, evidence)
        + _reliability(evidence)
        + _efficiency(runtime)
    )


def _engineering_tips(findings: list[dict]) -> list[str]:
    tips: list[str] = []
    for f in findings:
        if f["recommendation"] and f["recommendation"] not in tips:
            tips.append(f["recommendation"])
        if len(tips) == 5:
            break
    return tips


def evaluate_iso_25010(
    html: str,
    runtime_metrics: dict | None = None,
    characteristics: list | None = None,
    evidence: dict | None = None,
    expected_functions: list | None = None,
) -> dict[str, Any]:
    selected = normalize_selection(characteristics)
    labels = {k: CHARACTERISTICS[k] for k in selected}
    base = {
        "evaluated_characteristics": selected,
        "characteristic_labels": labels,
        "evaluation_scope": evaluation_scope(selected),
        "restrictions": evaluation_restrictions(bool(evidence)),
        "runtime_metrics": runtime_metrics or None,
        "evidence_received": bool(evidence),
        "strict_mode": True,
    }

    if not html or len(html.strip()) < 50:
        finding = {
            "metric_id": None, "dimension": "Adecuación funcional", "subdimension": "Artefacto evaluable",
            "severity": "Crítica", "severity_grade": 4, "severity_grade_label": SEVERITY_GRADES[4]["label"],
            "finding": "El contenido HTML recibido es insuficiente para realizar una evaluación técnica.",
            "recommendation": "Verificar que la interfaz se capture completa antes de evaluarla.",
        }
        decision = decision_criterion(0)
        return {**base, "global_score": 0, "quality_level": decision["category"], "quality_decision": decision,
                "scores": {}, "not_evaluated": selected, "total_findings": 1, "findings": [finding],
                "engineering_tips": [finding["recommendation"]], "metrics": []}

    soup = BeautifulSoup(html, "html.parser")
    metrics = [m for m in compute_metrics(soup, runtime_metrics, evidence, expected_functions)
               if m["characteristic"] in selected]
    scores, not_evaluated = score_characteristics(metrics, selected)
    global_score = round(sum(scores.values()) / len(scores)) if scores else 0
    findings = findings_from_metrics(metrics)
    decision = decision_criterion(global_score)

    return {
        **base,
        "global_score": global_score,
        "quality_level": decision["category"],
        "quality_decision": decision,
        "scores": scores,
        "not_evaluated": not_evaluated,
        "total_findings": len(findings),
        "findings": findings,
        "engineering_tips": _engineering_tips(findings),
        "metrics": metrics,
    }
