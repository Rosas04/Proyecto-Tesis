"""
services/iso_framework.py — Operacionalización de ISO/IEC 25010:2023 para frontend.

La norma es un modelo conceptual: no prescribe algoritmos de medición. Este
módulo hace explícito el mapeo característica → subcaracterística → métrica,
define cómo se calcula cada puntaje y declara qué NO puede medirse de forma
automática.

Características evaluadas
  Núcleo (siempre): Adecuación funcional, Capacidad de interacción, Compatibilidad,
                    Flexibilidad, Seguridad y Fiabilidad.
  Opcional:         Eficiencia de desempeño (sólo si se solicita).
  Excluida:         Mantenibilidad: exige el código fuente y su historial, no la
                    interfaz desplegada que audita FrontMind.

Puntaje
  Cada métrica produce un cumplimiento c ∈ [0, 1]:
    proporción  X = A/B      → c = min(1, X / meta)
    binaria     X ∈ {0, 1}   → c = X
    conteo      X = nº fallos (meta 0)    → c = 1 / (1 + X)
    máximo      X ≤ umbral               → c = min(1, umbral / X)
  Puntaje de la característica = 100 · Σ(peso·c) / Σ(peso) de sus métricas
  medidas. Una característica sin métricas medidas queda "no evaluada" y no
  entra al puntaje global (promedio de las características evaluadas).
"""
from __future__ import annotations

import re
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Características
# ─────────────────────────────────────────────────────────────────────────────

CHARACTERISTICS = {
    "adecuacion_funcional": "Adecuación funcional",
    "capacidad_interaccion": "Capacidad de interacción",
    "compatibilidad": "Compatibilidad",
    "flexibilidad": "Flexibilidad",
    "seguridad": "Seguridad",
    "fiabilidad": "Fiabilidad",
    "eficiencia_desempeno": "Eficiencia de desempeño",
}
CORE_CHARACTERISTICS = [
    "adecuacion_funcional", "capacidad_interaccion", "compatibilidad",
    "flexibilidad", "seguridad", "fiabilidad",
]
OPTIONAL_CHARACTERISTICS = ["eficiencia_desempeno"]

# Claves de versiones anteriores (ISO/IEC 25010:2011 y FrontMind ≤ 1.1)
LEGACY_ALIASES = {
    "usabilidad": "capacidad_interaccion",
    "accesibilidad": "capacidad_interaccion",
    "portabilidad": "flexibilidad",
}


def normalize_selection(characteristics: Optional[list[str]]) -> list[str]:
    """Subconjunto priorizado. Vacío/None = las seis características núcleo."""
    if not characteristics:
        return list(CORE_CHARACTERISTICS)
    selected: list[str] = []
    for c in characteristics:
        key = LEGACY_ALIASES.get(c, c)
        if key in CHARACTERISTICS and key not in selected:
            selected.append(key)
    return [c for c in CHARACTERISTICS if c in selected] or list(CORE_CHARACTERISTICS)


# ─────────────────────────────────────────────────────────────────────────────
# Escala de severidad (0–4) y criterio de decisión (0–10)
# ─────────────────────────────────────────────────────────────────────────────

SEVERITY_GRADES = {
    0: {"label": "No", "criterion": "Cumplimiento satisfactorio (≥ 90 %)"},
    1: {"label": "Cosmético", "criterion": "Defecto menor que no impide la operación (51 % – 89 %)"},
    2: {"label": "Menor", "criterion": "Inconveniente local que afecta la fluidez (11 % – 50 %)"},
    3: {"label": "Mayor", "criterion": "Fallo grave que dificulta completar tareas clave (1 % – 10 %)"},
    4: {"label": "Catastrófico", "criterion": "Bloqueo crítico o incumplimiento total (< 1 %)"},
}
_GRADE_TO_SEVERITY = {4: "Crítica", 3: "Alta", 2: "Media", 1: "Baja"}
_SEVERITY_TO_GRADE = {v: k for k, v in _GRADE_TO_SEVERITY.items()}


def severity_grade(severity: str) -> dict:
    grade = _SEVERITY_TO_GRADE.get(severity, 2)
    return {"grade": grade, "label": SEVERITY_GRADES[grade]["label"]}


def grade_from_compliance(ratio: Optional[float]) -> Optional[int]:
    """Grado 0–4 a partir del cumplimiento (0–1) de una métrica."""
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
    """
    score_10 = round(max(0.0, min(100.0, float(global_score_100))) / 10, 1)
    if score_10 >= 9.0:
        category, meaning = "Alta calidad", "El sistema cumple holgadamente con los estándares."
    elif score_10 > 6.0:
        category, meaning = "Buena calidad", "Cumplimiento adecuado con observaciones menores."
    elif score_10 > 2.0:
        category, meaning = "Regular calidad", "Presencia de barreras o defectos moderados."
    else:
        category, meaning = "Mala calidad", "Deficiencias críticas que requieren reestructuración."
    return {"score_10": score_10, "category": category, "meaning": meaning}


# ─────────────────────────────────────────────────────────────────────────────
# Alcance: subcaracterísticas, método y límites
# ─────────────────────────────────────────────────────────────────────────────

AUTOMATED, PARTIAL, MANUAL = "automatizada", "parcial (indicador aproximado)", "no automatizable"

QUALITY_MODEL: list[dict[str, Any]] = [
    # Adecuación funcional
    {"characteristic": "adecuacion_funcional", "sub": "Completitud funcional", "automation": PARTIAL,
     "method": "AF-01: funciones esperadas (declaradas por el evaluador) presentes en la interfaz.",
     "limit": "Requiere la lista de funciones esperadas; sin ella no se evalúa."},
    {"characteristic": "adecuacion_funcional", "sub": "Corrección funcional", "automation": AUTOMATED,
     "method": "AF-02 enlaces internos que responden sin error; AF-03 imágenes de contenido que cargan.",
     "limit": "No verifica que los cálculos o datos mostrados sean correctos (requiere oráculos de prueba)."},
    {"characteristic": "adecuacion_funcional", "sub": "Pertinencia funcional", "automation": PARTIAL,
     "method": "AF-04: funciones esperadas disponibles como control operable (enlace, botón o campo).",
     "limit": "Requiere la lista de funciones esperadas; no mide el número de pasos de una tarea."},
    # Capacidad de interacción
    {"characteristic": "capacidad_interaccion", "sub": "Reconocibilidad de adecuación", "automation": MANUAL,
     "method": "Cuestionarios o juicio de expertos.", "limit": "Depende de la percepción del usuario."},
    {"characteristic": "capacidad_interaccion", "sub": "Aprendibilidad", "automation": MANUAL,
     "method": "Tiempo para completar tareas en pruebas con usuarios.", "limit": "Requiere participantes reales."},
    {"characteristic": "capacidad_interaccion", "sub": "Operabilidad", "automation": AUTOMATED,
     "method": "CI-08 objetivos táctiles ≥ 24 px (WCAG 2.5.8), CI-09 orden de foco (2.4.3), CI-15 texto legible en móvil.",
     "limit": "No mide el esfuerzo real de operación de una tarea."},
    {"characteristic": "capacidad_interaccion", "sub": "Protección contra errores del usuario", "automation": AUTOMATED,
     "method": "CI-10 validación declarativa, CI-11 autocompletado de datos personales (WCAG 1.3.5).",
     "limit": "No mide la tasa real de recuperación ante entradas inválidas."},
    {"characteristic": "capacidad_interaccion", "sub": "Compromiso del usuario", "automation": MANUAL,
     "method": "Cuestionarios (p. ej. SUS, UEQ).", "limit": "Atributo subjetivo."},
    {"characteristic": "capacidad_interaccion", "sub": "Inclusividad", "automation": AUTOMATED,
     "method": "CI-01…CI-07: texto alternativo, etiquetas, nombres accesibles, idioma, contraste y zoom (WCAG 2.2 AA).",
     "limit": "Las pruebas automáticas cubren sólo una parte de WCAG; se recomienda revisión con lector de pantalla."},
    {"characteristic": "capacidad_interaccion", "sub": "Asistencia al usuario", "automation": PARTIAL,
     "method": "CI-12: región de mensajes de estado en interfaces con formularios (WCAG 4.1.3).",
     "limit": "No evalúa la calidad de la ayuda ofrecida."},
    {"characteristic": "capacidad_interaccion", "sub": "Autodescriptividad", "automation": AUTOMATED,
     "method": "CI-13 título de página (WCAG 2.4.2), CI-14 encabezado principal.",
     "limit": "No evalúa si el texto es comprensible."},
    # Compatibilidad
    {"characteristic": "compatibilidad", "sub": "Coexistencia", "automation": PARTIAL,
     "method": "CO-04: variables globales añadidas al entorno compartido del navegador.",
     "limit": "No se prueba junto a otros productos concretos (extensiones, widgets)."},
    {"characteristic": "compatibilidad", "sub": "Interoperabilidad", "automation": AUTOMATED,
     "method": "CO-01 peticiones a API exitosas; CO-02 carga sin errores nuevos en Chromium, Firefox y WebKit; "
               "CO-03 diseño coherente entre motores.",
     "limit": "Navegadores de escritorio en modo headless; no cubre versiones antiguas ni navegadores móviles reales."},
    # Flexibilidad
    {"characteristic": "flexibilidad", "sub": "Adaptabilidad", "automation": AUTOMATED,
     "method": "FL-01 meta viewport, FL-02 sin desbordamiento en 1366/768/390 px, FL-03 reflow a 320 px (WCAG 1.4.10).",
     "limit": "Resoluciones simuladas en un navegador headless."},
    {"characteristic": "flexibilidad", "sub": "Escalabilidad", "automation": MANUAL,
     "method": "Pruebas de carga creciente.", "limit": "Requiere generar carga sobre el sistema auditado."},
    {"characteristic": "flexibilidad", "sub": "Instalabilidad", "automation": PARTIAL,
     "method": "FL-04 (informativa): manifiesto de aplicación web instalable.",
     "limit": "Sólo aplica si el sistema pretende instalarse (PWA); no puntúa."},
    {"characteristic": "flexibilidad", "sub": "Reemplazabilidad", "automation": MANUAL,
     "method": "Análisis de dependencias y contratos de integración.", "limit": "Requiere documentación del sistema."},
    # Seguridad
    {"characteristic": "seguridad", "sub": "Confidencialidad", "automation": AUTOMATED,
     "method": "SE-01 HTTPS, SE-02 certificado válido, SE-03 HSTS, SE-04 redirección HTTP→HTTPS, SE-05 formularios de "
               "contraseña seguros, SE-06 sin contenido mixto, SE-07 cookies Secure, SE-08 credenciales fuera de Web "
               "Storage, SE-13 Referrer-Policy.",
     "limit": "Observación pasiva de la interfaz; no es una prueba de penetración."},
    {"characteristic": "seguridad", "sub": "Integridad", "automation": AUTOMATED,
     "method": "SE-09 Content-Security-Policy, SE-10 protección anti-clickjacking, SE-11 nosniff, SE-12 SRI en scripts de terceros.",
     "limit": "Comprueba la presencia de la política, no su solidez completa."},
    {"characteristic": "seguridad", "sub": "No repudio, responsabilidad y autenticidad", "automation": MANUAL,
     "method": "Revisión de registros de auditoría y del mecanismo de autenticación.",
     "limit": "Ocurre en el servidor; no es observable desde la interfaz."},
    {"characteristic": "seguridad", "sub": "Resistencia", "automation": MANUAL,
     "method": "Pruebas de penetración autorizadas.", "limit": "Fuera del alcance de una auditoría pasiva."},
    # Fiabilidad
    {"characteristic": "fiabilidad", "sub": "Disponibilidad", "automation": AUTOMATED,
     "method": "FI-01: la interfaz responde sin error HTTP.",
     "limit": "Medición puntual; la disponibilidad sostenida requiere monitoreo en el tiempo."},
    {"characteristic": "fiabilidad", "sub": "Ausencia de fallos", "automation": AUTOMATED,
     "method": "FI-02 errores JavaScript no capturados, FI-03 errores en consola.",
     "limit": "Sólo detecta fallos que ocurren al cargar la interfaz, no durante tareas."},
    {"characteristic": "fiabilidad", "sub": "Tolerancia a fallos", "automation": AUTOMATED,
     "method": "FI-04: recursos (scripts, estilos, imágenes, API) cargados sin error.",
     "limit": "No inyecta fallos de red para observar la degradación."},
    {"characteristic": "fiabilidad", "sub": "Recuperabilidad", "automation": MANUAL,
     "method": "Pruebas de recuperación ante caídas.", "limit": "Requiere provocar fallos en el sistema."},
    # Eficiencia (opcional)
    {"characteristic": "eficiencia_desempeno", "sub": "Comportamiento temporal", "automation": AUTOMATED,
     "method": "EF-01 TTFB, EF-02 LCP, EF-03 CLS medidos con Playwright.",
     "limit": "Medido desde el servidor de evaluación, no desde el dispositivo del usuario."},
    {"characteristic": "eficiencia_desempeno", "sub": "Utilización de recursos", "automation": AUTOMATED,
     "method": "EF-04 bytes transferidos, EF-05 peticiones, EF-06 memoria JS.",
     "limit": "transferSize es 0 en recursos de otro origen sin Timing-Allow-Origin."},
    {"characteristic": "eficiencia_desempeno", "sub": "Capacidad", "automation": MANUAL,
     "method": "Pruebas de carga y concurrencia.", "limit": "Requiere generar carga sobre el sistema auditado."},
]

OUT_OF_SCOPE = [
    {"characteristic": "Mantenibilidad",
     "reason": "Sus métricas (modularidad, reusabilidad, analizabilidad, capacidad de prueba) requieren el "
               "código fuente, el grafo de dependencias y el historial de defectos, no la interfaz desplegada."},
    {"characteristic": "Seguridad física (Safety, ISO/IEC 25010:2023)",
     "reason": "No aplica a interfaces web sin riesgo físico para personas o entorno."},
    {"characteristic": "Calidad en uso (efectividad, eficiencia, satisfacción)",
     "reason": "Requiere usuarios reales, cuestionarios y tareas observadas."},
]


def evaluation_scope(selected: list[str]) -> dict:
    items = [
        {**item, "characteristic_label": CHARACTERISTICS[item["characteristic"]]}
        for item in QUALITY_MODEL if item["characteristic"] in selected
    ]
    out_of_scope = list(OUT_OF_SCOPE)
    if "eficiencia_desempeno" not in selected:
        out_of_scope.append({
            "characteristic": "Eficiencia de desempeño (opcional)",
            "reason": "No se seleccionó en esta evaluación; puede incluirse a pedido.",
        })
    return {
        "selected_characteristics": [CHARACTERISTICS[c] for c in selected],
        "subcharacteristics": items,
        "coverage": {
            "automatizada": sum(1 for i in items if i["automation"] == AUTOMATED),
            "parcial": sum(1 for i in items if i["automation"] == PARTIAL),
            "no_automatizable": sum(1 for i in items if i["automation"] == MANUAL),
            "total": len(items),
        },
        "out_of_scope": out_of_scope,
    }


def evaluation_restrictions(has_runtime_evidence: bool) -> list[dict]:
    return [
        {"type": "Herramientas y metodología",
         "detail": "Análisis del DOM renderizado (BeautifulSoup) y observación en ejecución con Playwright "
                   "(Chromium, Firefox y WebKit). Las métricas son una operacionalización propia de la norma."},
        {"type": "Artefacto evaluado",
         "detail": "DOM original de cada interfaz capturada (no su réplica). No se analiza el código fuente."},
        {"type": "Entorno de prueba",
         "detail": "Resoluciones 1366×768, 768×1024, 390×844 y 320×640 en navegadores headless. "
                   + ("Las evidencias de ejecución se midieron una vez desde el servidor de evaluación."
                      if has_runtime_evidence else
                      "No se recibieron evidencias de ejecución: las métricas que las requieren figuran como no medidas.")},
        {"type": "Tiempo y recursos",
         "detail": "Máximo de interfaces configurable (por defecto 10), hasta 15 enlaces verificados por interfaz "
                   "y compatibilidad multinavegador en las primeras 5 interfaces."},
        {"type": "Atributos subjetivos",
         "detail": "Aprendibilidad, compromiso y reconocibilidad requieren cuestionarios o juicio experto y no se puntúan."},
        {"type": "Selección de características",
         "detail": "Se evalúan Adecuación funcional, Capacidad de interacción, Compatibilidad, Flexibilidad, Seguridad "
                   "y Fiabilidad; Eficiencia de desempeño es opcional. Las características sin métricas medidas no "
                   "influyen en el puntaje global."},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Construcción de métricas
# ─────────────────────────────────────────────────────────────────────────────

_FORMULAS = {
    "ratio": "X = A / B",
    "binary": "X = 1 si cumple, 0 si no",
    "count": "X = número de ocurrencias",
    "max": "X = valor medido",
}


def compliance_of(kind: str, x: Optional[float], target: float) -> Optional[float]:
    if x is None:
        return None
    if kind == "ratio":
        return min(1.0, x / target) if target else 1.0
    if kind == "binary":
        return float(x)
    if kind == "count":
        return 1.0 / (1.0 + x)
    if kind == "max":
        return 1.0 if x <= target else (target / x if x else 0.0)
    return None


def target_text(kind: str, target: float, unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    if kind == "ratio":
        return f"X ≥ {target:g}"
    if kind == "binary":
        return "X = 1"
    if kind == "count":
        return "X = 0"
    return f"X ≤ {target:g}{suffix}"


def make_metric(mid: str, characteristic: str, sub: str, name: str, *, kind: str, target: float = 1.0,
                x: Optional[float] = None, a: Optional[float] = None, b: Optional[float] = None,
                unit: str = "", reference: str = "", weight: float = 1.0, scored: bool = True,
                not_measured: str = "no medido", finding: str = "", recommendation: str = "",
                examples: Optional[list[str]] = None) -> dict:
    if kind == "ratio":
        x = round(a / b, 3) if (a is not None and b) else None
    c = compliance_of(kind, x, target)
    measured = x is not None
    meets = (c >= 0.999) if measured else None
    return {
        "id": mid, "characteristic": characteristic, "characteristic_label": CHARACTERISTICS[characteristic],
        "subcharacteristic": sub, "name": name, "kind": kind, "formula": _FORMULAS[kind],
        "A": a if kind == "ratio" else None, "B": b if kind == "ratio" else None,
        "X": x, "unit": unit, "target": target_text(kind, target, unit), "target_value": target,
        "compliance": round(c, 3) if c is not None else None,
        "meets": meets, "severity_grade": grade_from_compliance(c) if measured else None,
        "weight": weight, "scored": scored,
        "status": ("medido" if scored else "informativo") if measured else not_measured,
        "reference": reference,
        "finding": finding, "recommendation": recommendation, "examples": examples or [],
    }


# Impacto de cada métrica: (severidad máxima 1–4, peso en el puntaje).
# La severidad de un hallazgo es el grado por cumplimiento (0–4) acotado por la
# severidad máxima: p. ej. la falta de Referrer-Policy nunca es "Crítica",
# mientras que una interfaz sin HTTPS sí puede serlo.
METRIC_IMPACT: dict[str, tuple[int, float]] = {
    "AF-01": (3, 2.0), "AF-02": (3, 1.5), "AF-03": (2, 1.0), "AF-04": (3, 1.5),
    "CI-01": (3, 1.0), "CI-02": (3, 1.0), "CI-03": (3, 1.0), "CI-04": (3, 1.0), "CI-05": (2, 0.5),
    "CI-06": (3, 1.0), "CI-07": (3, 1.0), "CI-08": (2, 1.0), "CI-09": (2, 0.5), "CI-10": (2, 1.0),
    "CI-11": (2, 0.5), "CI-12": (2, 0.5), "CI-13": (2, 0.5), "CI-14": (1, 0.5), "CI-15": (2, 1.0),
    "CO-01": (3, 1.5), "CO-02": (3, 2.0), "CO-03": (2, 1.0), "CO-04": (1, 0.5),
    "FL-01": (3, 1.0), "FL-02": (3, 2.0), "FL-03": (2, 1.0), "FL-04": (1, 0.0),
    "SE-01": (4, 3.0), "SE-02": (4, 2.0), "SE-03": (2, 1.0), "SE-04": (2, 1.0), "SE-05": (4, 3.0),
    "SE-06": (3, 1.5), "SE-07": (2, 1.0), "SE-08": (3, 1.5), "SE-09": (2, 1.0), "SE-10": (2, 1.0),
    "SE-11": (1, 0.5), "SE-12": (1, 0.5), "SE-13": (1, 0.5),
    "FI-01": (4, 2.0), "FI-02": (3, 1.5), "FI-03": (1, 0.5), "FI-04": (2, 1.0),
    "EF-01": (2, 1.0), "EF-02": (2, 1.0), "EF-03": (2, 1.0), "EF-04": (2, 1.0), "EF-05": (1, 0.5), "EF-06": (1, 0.5),
}


def apply_impact(metrics: list[dict]) -> list[dict]:
    for m in metrics:
        max_grade, weight = METRIC_IMPACT.get(m["id"], (4, m["weight"]))
        m["weight"] = weight
        m["max_severity"] = max_grade
        if m["severity_grade"]:
            m["severity_grade"] = min(m["severity_grade"], max_grade)
    return metrics


def score_characteristics(metrics: list[dict], selected: list[str]) -> tuple[dict, list[str]]:
    """Puntaje 0–100 por característica (promedio ponderado de cumplimientos)."""
    scores, not_evaluated = {}, []
    for key in selected:
        own = [m for m in metrics if m["characteristic"] == key and m["scored"] and m["compliance"] is not None]
        weight = sum(m["weight"] for m in own)
        if not own or weight == 0:
            not_evaluated.append(key)
            continue
        scores[key] = round(100 * sum(m["weight"] * m["compliance"] for m in own) / weight)
    return scores, not_evaluated


def findings_from_metrics(metrics: list[dict]) -> list[dict]:
    """Un hallazgo por métrica medida que no alcanza su meta (trazable a la métrica)."""
    findings = []
    for m in metrics:
        if not m["scored"] or m["meets"] is not False:
            continue
        grade = max(1, m["severity_grade"] or 1)
        severity = _GRADE_TO_SEVERITY[grade]
        detail = m["finding"]
        if m["examples"]:
            detail += " (Ejemplo: " + ", ".join(m["examples"][:3]) + ")"
        findings.append({
            "metric_id": m["id"],
            "dimension": m["characteristic_label"],
            "subdimension": m["subcharacteristic"],
            "severity": severity,
            "severity_grade": grade,
            "severity_grade_label": SEVERITY_GRADES[grade]["label"],
            "finding": detail,
            "recommendation": m["recommendation"],
            "reference": m["reference"],
        })
    order = {"Crítica": 0, "Alta": 1, "Media": 2, "Baja": 3}
    findings.sort(key=lambda f: order[f["severity"]])
    return findings


_SPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    return _SPACE_RE.sub(" ", (value or "").strip().lower())
