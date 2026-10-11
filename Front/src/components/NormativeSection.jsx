import "./NormativeSection.css";

const GRADE_CLASS = { 0: "ok", 1: "cosmetic", 2: "minor", 3: "major", 4: "catastrophic" };
const GRADE_LABEL = { 0: "No", 1: "Cosmético", 2: "Menor", 3: "Mayor", 4: "Catastrófico" };

function formatValue(metric) {
  if (metric.X === null || metric.X === undefined) return "—";
  return `${metric.X}${metric.unit ? ` ${metric.unit}` : ""}`;
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
                  <th>Fórmula</th>
                  <th>A</th>
                  <th>B</th>
                  <th>X</th>
                  <th>Meta</th>
                  <th>Severidad</th>
                </tr>
              </thead>
              <tbody>
                {measured.map((m) => (
                  <tr key={m.id}>
                    <td className="mono">{m.id}</td>
                    <td>{m.subcharacteristic}</td>
                    <td>
                      {m.name}
                      {m.reference && <small className="normative-ref">{m.reference}</small>}
                    </td>
                    <td className="mono">{m.formula}</td>
                    <td>{m.A ?? "—"}</td>
                    <td>{m.B ?? "—"}</td>
                    <td><strong>{formatValue(m)}</strong></td>
                    <td className="mono">{m.target}</td>
                    <td>
                      {m.severity_grade !== null && m.severity_grade !== undefined ? (
                        <span className={`grade-pill ${GRADE_CLASS[m.severity_grade]}`}>
                          {m.severity_grade} · {GRADE_LABEL[m.severity_grade]}
                        </span>
                      ) : "—"}
                    </td>
                  </tr>
                ))}
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
