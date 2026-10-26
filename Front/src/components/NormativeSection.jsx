import "./NormativeSection.css";

const GRADE_CLASS = { 0: "ok", 1: "cosmetic", 2: "minor", 3: "major", 4: "catastrophic" };
const GRADE_LABEL = { 0: "No", 1: "Cosmético", 2: "Menor", 3: "Mayor", 4: "Catastrófico" };

function formatValue(metric) {
  if (metric.X === null || metric.X === undefined) return "—";
  return `${metric.X}${metric.unit ? ` ${metric.unit}` : ""}`;
}


/** Texto de recomendación por métrica cuando no se cumple la meta. */
const FIX_HINT = {
  "ACC-01": "Agregue el atributo alt a cada imagen (alt=\"\" si es decorativa).",
  "ACC-02": "Asocie cada campo con un <label for> o aria-label.",
  "ACC-03": "Dé a cada botón un texto visible o un aria-label.",
  "ACC-04": "Use textos descriptivos en los enlaces (evite «clic aquí» o enlaces vacíos).",
  "ACC-05": "Declare el idioma en la etiqueta <html lang=\"es\">.",
  "USA-01": "Use type (email, number, tel…) y required/pattern para validar los campos sin depender de JavaScript.",
  "USA-02": "Agregue una región role=\"status\" o aria-live para anunciar mensajes de error y confirmación.",
  "MAN-01": "Reemplace <div> genéricos por <main>, <nav>, <header>, <section> o <footer>.",
  "MAN-02": "Elimine los id repetidos: cada id debe ser único en la página.",
  "MAN-03": "Mueva los estilos inline (style=\"…\") a una hoja de estilos CSS.",
  "POR-01": "Agregue <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">.",
  "EFI-01": "Reduzca el tiempo de respuesta del servidor (caché, CDN, menos procesamiento).",
  "EFI-02": "Optimice la imagen o bloque principal: compresión, tamaños adecuados y carga prioritaria.",
  "EFI-03": "Reserve espacio (ancho y alto) para imágenes y anuncios para evitar saltos de diseño.",
  "EFI-04": "Comprima imágenes, minifique JS/CSS y active compresión gzip/brotli.",
  "EFI-05": "Reduzca peticiones: combine recursos, use lazy-loading y elimine scripts innecesarios.",
  "EFI-06": "Reduzca el JavaScript cargado y libere memoria de componentes que no se usan.",
};

function pct(x) {
  return `${Math.round(x * 100)} %`;
}

/** Resultado en lenguaje natural: "2 de 2 (100 %)" o el valor medido con su unidad. */
function resultText(m) {
  if (m.A !== null && m.A !== undefined && m.B) {
    return `${m.A} de ${m.B} (${pct(m.X)})`;
  }
  return formatValue(m);
}

/** Meta en lenguaje natural. */
function goalText(m) {
  const t = String(m.target || "");
  const ratio = t.match(/X\s*≥\s*([\d.]+)/);
  if (ratio && m.B !== null && m.B !== undefined) return `Meta: al menos ${pct(Number(ratio[1]))}`;
  return t ? `Meta: ${t.replace(/^X\s*/, "")}` : "";
}

/** Por qué cumple o no cumple, y qué hacer. */
function diagnosis(m) {
  if (m.meets === null || m.meets === undefined) return { ok: null, why: "No se pudo medir en esta página.", fix: "" };
  if (m.meets) {
    return { ok: true, why: "Cumple la meta establecida.", fix: "" };
  }
  const missing = m.A !== null && m.A !== undefined && m.B ? m.B - m.A : null;
  const why = missing !== null
    ? `${missing} de ${m.B} elementos no cumplen${m.B_description ? ` (${m.B_description})` : ""}.`
    : "El valor medido está fuera de la meta.";
  return { ok: false, why, fix: FIX_HINT[m.id] || "Revise este aspecto y corríjalo para alcanzar la meta." };
}

function automationClass(automation = "") {
  if (automation.startsWith("automatizada")) return "auto";
  if (automation.startsWith("parcial")) return "partial";
  return "manual";
}

/** Agrupa las subcaracterísticas por característica, preservando el orden del modelo. */
function groupByCharacteristic(items = []) {
  const groups = [];
  for (const item of items) {
    let group = groups.find((g) => g.label === item.characteristic_label);
    if (!group) {
      group = { label: item.characteristic_label, items: [] };
      groups.push(group);
    }
    group.items.push(item);
  }
  return groups;
}

/**
 * Sección de evaluación según el modelo de calidad ISO/IEC 25010:
 *   1. Resultado global  2. Métricas medidas  3. Cobertura del modelo
 *   4. Características no evaluadas  5. Condiciones de la evaluación
 * `data` es el resultado de /evaluate/iso o de /report/generate.
 */
export default function NormativeSection({ data }) {
  if (!data) return null;
  const {
    quality_decision: decision,
    metrics = [],
    evaluation_scope: scope,
    restrictions = [],
    severity_grade_summary: grades,
  } = data;
  if (!decision && metrics.length === 0 && !scope) return null;

  const measured = metrics.filter((m) => m.X !== null && m.X !== undefined);
  const notMeasured = metrics.filter((m) => m.X === null || m.X === undefined);
  const groups = groupByCharacteristic(scope?.subcharacteristics);
  const outOfScope = scope?.out_of_scope || [];

  return (
    <section className="normative card">
      <header className="normative-header">
        <h2>Evaluación según ISO/IEC 25010</h2>
        <p>
          Resultado del modelo de calidad del producto aplicado a la interfaz: puntaje global, métricas
          medidas, cobertura de características y condiciones bajo las que se realizó la evaluación.
        </p>
      </header>

      {/* 1. Resultado global */}
      {decision && (
        <div className="normative-block">
          <h3><span className="normative-step">1</span> Resultado global</h3>
          <div className="normative-decision">
            <div className="normative-score">
              <span className="normative-score-value">{decision.score_10}</span>
              <span className="normative-score-max">/ 10</span>
            </div>
            <div className="normative-decision-text">
              <strong>{decision.category}</strong>
              <p>{decision.meaning}</p>
              <small>Escala: 9.0–10.0 Alta · 6.0–9.0 Buena · 2.0–6.0 Regular · 0.0–2.0 Mala</small>
            </div>
            {grades && (
              <div className="normative-grades">
                {Object.entries(grades).map(([label, count]) => (
                  <div key={label} className="normative-grade-item">
                    <span>{count}</span>
                    <small>{label}</small>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 2. Métricas medidas */}
      {measured.length > 0 && (
        <div className="normative-block">
          <h3><span className="normative-step">2</span> Métricas medidas</h3>
          <div className="normative-table-wrap">
            <table className="normative-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Subcaracterística</th>
                  <th>Métrica</th>
                  <th>Resultado</th>
                  <th>Estado</th>
                  <th>Diagnóstico y recomendación</th>
                  <th>Severidad</th>
                </tr>
              </thead>
              <tbody>
                {measured.map((m) => {
                  const dg = diagnosis(m);
                  return (
                  <tr key={m.id}>
                    <td className="mono">{m.id}</td>
                    <td>{m.subcharacteristic}</td>
                    <td>
                      {m.name}
                      {m.reference && <small className="normative-ref">{m.reference}</small>}
                    </td>
                    <td>
                      <strong>{resultText(m)}</strong>
                      <small className="normative-ref">{goalText(m)}</small>
                    </td>
                    <td>
                      {dg.ok === null ? "—" : (
                        <span className={`grade-pill ${dg.ok ? "ok" : "major"}`}>{dg.ok ? "Cumple" : "No cumple"}</span>
                      )}
                    </td>
                    <td>
                      {dg.why}
                      {dg.fix && <small className="normative-ref"><strong>Recomendación:</strong> {dg.fix}</small>}
                    </td>
                    <td>
                      {m.severity_grade !== null && m.severity_grade !== undefined ? (
                        <span className={`grade-pill ${GRADE_CLASS[m.severity_grade]}`}>
                          {m.severity_grade} · {GRADE_LABEL[m.severity_grade]}
                        </span>
                      ) : "—"}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {notMeasured.length > 0 && (
            <p className="normative-note">
              Sin medición en esta evaluación: {notMeasured.map((m) => m.id).join(", ")}.
            </p>
          )}
        </div>
      )}

      {/* 3. Cobertura del modelo de calidad */}
      {groups.length > 0 && (
        <div className="normative-block">
          <h3><span className="normative-step">3</span> Cobertura del modelo de calidad</h3>
          <div className="normative-coverage">
            <div className="coverage-item auto">
              <span>{scope.coverage?.automatizada}</span>
              <small>Automatizadas</small>
            </div>
            <div className="coverage-item partial">
              <span>{scope.coverage?.parcial}</span>
              <small>Indicador aproximado</small>
            </div>
            <div className="coverage-item manual">
              <span>{scope.coverage?.no_automatizable}</span>
              <small>No automatizables</small>
            </div>
          </div>
          <div className="normative-table-wrap">
            <table className="normative-table">
              <thead>
                <tr>
                  <th>Subcaracterística</th>
                  <th>Medición</th>
                  <th>Método</th>
                  <th>Limitación</th>
                </tr>
              </thead>
              <tbody>
                {groups.map((group) => [
                  <tr key={group.label} className="normative-group-row">
                    <td colSpan={4}>{group.label}</td>
                  </tr>,
                  ...group.items.map((s) => (
                    <tr key={`${group.label}-${s.sub}`}>
                      <td>{s.sub}</td>
                      <td><span className={`automation-pill ${automationClass(s.automation)}`}>{s.automation}</span></td>
                      <td>{s.method}</td>
                      <td>{s.limit}</td>
                    </tr>
                  )),
                ])}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. Características no evaluadas */}
      {outOfScope.length > 0 && (
        <div className="normative-block">
          <h3><span className="normative-step">4</span> Características no evaluadas</h3>
          <div className="normative-table-wrap">
            <table className="normative-table normative-two-cols">
              <thead>
                <tr>
                  <th>Característica</th>
                  <th>Motivo</th>
                </tr>
              </thead>
              <tbody>
                {outOfScope.map((o) => (
                  <tr key={o.characteristic}>
                    <td><strong>{o.characteristic}</strong></td>
                    <td>{o.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. Condiciones de la evaluación */}
      {restrictions.length > 0 && (
        <div className="normative-block">
          <h3><span className="normative-step">5</span> Condiciones de la evaluación</h3>
          <div className="normative-table-wrap">
            <table className="normative-table normative-two-cols">
              <thead>
                <tr>
                  <th>Aspecto</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>
                {restrictions.map((r) => (
                  <tr key={r.type}>
                    <td><strong>{r.type}</strong></td>
                    <td>{r.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
