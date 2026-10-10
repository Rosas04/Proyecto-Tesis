import "./NormativeSection.css";

const GRADE_CLASS = { 0: "ok", 1: "cosmetic", 2: "minor", 3: "major", 4: "catastrophic" };
const GRADE_LABEL = { 0: "No", 1: "Cosmético", 2: "Menor", 3: "Mayor", 4: "Catastrófico" };

function formatValue(metric) {
  if (metric.X === null || metric.X === undefined) return "—";
  return `${metric.X}${metric.unit ? ` ${metric.unit}` : ""}`;
}

/**
 * Sección normativa de la evaluación (ISO/IEC 25010 · 25022/25023 · 25040):
 * criterio de decisión 0–10, métricas X = A/B, alcance y restricciones.
 * `data` es el resultado de /evaluate/iso o de /report/generate.
 */
export default function NormativeSection({ data }) {
  if (!data) return null;
  const { iso25040, metrics = [], evaluation_scope: scope, restrictions = [], severity_grade_summary: grades } = data;
  if (!iso25040 && metrics.length === 0 && !scope) return null;

  const measured = metrics.filter((m) => m.X !== null && m.X !== undefined);
  const notMeasured = metrics.filter((m) => m.X === null || m.X === undefined);

  return (
    <section className="normative card">
      <div className="normative-header">
        <h2>Evaluación normativa ISO/IEC 25040</h2>
        <p>
          Operacionalización de ISO/IEC 25010 en métricas medibles (X = A / B) y criterios de decisión.
          Los resultados dependen de las restricciones de evaluación declaradas al final.
        </p>
      </div>

      {iso25040 && (
        <div className="normative-decision">
          <div className="normative-score">
            <span className="normative-score-value">{iso25040.score_10}</span>
            <span className="normative-score-max">/ 10</span>
          </div>
          <div>
            <strong>{iso25040.category}</strong>
            <p>{iso25040.meaning}</p>
            <small>Escala: [9.0–10.0] Alta · ]6.0–9.0[ Buena · ]2.0–6.0] Regular · [0.0–2.0] Mala</small>
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
      )}

      {measured.length > 0 && (
        <>
          <h3>Métricas de calidad medidas</h3>
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
                  <th>Severidad (0–4)</th>
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
              No medidas en esta evaluación: {notMeasured.map((m) => `${m.id} (${m.status})`).join(", ")}.
            </p>
          )}
        </>
      )}

      {scope && (
        <>
          <h3>Alcance de la evaluación</h3>
          <p className="normative-note">
            Características evaluadas: {scope.selected_characteristics?.join(", ")}.
            Subcaracterísticas: {scope.coverage?.automatizada} automatizadas, {scope.coverage?.parcial} con
            indicador aproximado y {scope.coverage?.no_automatizable} no automatizables.
          </p>
          <div className="normative-table-wrap">
            <table className="normative-table">
              <thead>
                <tr>
                  <th>Característica</th>
                  <th>Subcaracterística</th>
                  <th>Medición</th>
                  <th>Método</th>
                  <th>Limitación</th>
                </tr>
              </thead>
              <tbody>
                {scope.subcharacteristics?.map((s, i) => (
                  <tr key={i}>
                    <td>{s.characteristic_label}</td>
                    <td>{s.sub}</td>
                    <td>
                      <span className={`automation-pill ${s.automation.startsWith("automatizada") ? "auto" : s.automation.startsWith("parcial") ? "partial" : "manual"}`}>
                        {s.automation}
                      </span>
                    </td>
                    <td>{s.method}</td>
                    <td>{s.limit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {scope.out_of_scope?.length > 0 && (
            <ul className="normative-list">
              {scope.out_of_scope.map((o) => (
                <li key={o.characteristic}><strong>Fuera de alcance — {o.characteristic}:</strong> {o.reason}</li>
              ))}
            </ul>
          )}
        </>
      )}

      {restrictions.length > 0 && (
        <>
          <h3>Restricciones de evaluación (ISO/IEC 25040)</h3>
          <ul className="normative-list">
            {restrictions.map((r) => (
              <li key={r.type}><strong>{r.type}:</strong> {r.detail}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
