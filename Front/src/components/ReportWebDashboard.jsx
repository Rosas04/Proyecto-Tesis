import './ReportWebDashboard.css';
import { getQualityLevel, toScore } from '../utils/qualityLevel';

export function ReportWebDashboard({ reportResult, summary, findings, scores, sourceLabel, inputType, getBadgeClassUI }) {
  const scoreValue = toScore(summary?.global_score);
  const scoreLabels = {
    adecuacion_funcional: "Adecuación funcional",
    eficiencia_desempeno: "Eficiencia de desempeño",
    usabilidad: "Usabilidad",
    accesibilidad: "Accesibilidad",
    mantenibilidad: "Mantenibilidad",
    compatibilidad: "Compatibilidad",
    seguridad: "Seguridad",
    portabilidad: "Portabilidad",
  };

  return (
    <div className="report-web-dashboard">
      <div className="pdf-grid-2col">
        
        <div className="pdf-col">
          
          {/* Resumen ejecutivo */}
          <div className="pdf-card">
            <h3 className="card-title">Resumen ejecutivo</h3>
            <div className="exec-summary-content">
              <div className="score-circle-container">
                <svg width="120" height="120" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                  <circle cx="60" cy="60" r="50" fill="none" stroke={getQualityLevel(scoreValue).color} strokeWidth="8" strokeDasharray={2 * Math.PI * 50} strokeDashoffset={(2 * Math.PI * 50) - ((scoreValue ?? 0) / 100) * (2 * Math.PI * 50)} transform="rotate(-90 60 60)" strokeLinecap="round" />
                  <text x="60" y="55" textAnchor="middle" fontSize="28" fontWeight="800" fill="#0f172a">{scoreValue ?? "N/D"}<tspan fontSize="14" fill="#64748b">/100</tspan></text>
                </svg>
                <div className="score-label-ui" style={{ backgroundColor: getQualityLevel(scoreValue).color }}>{(summary.quality_level || getQualityLevel(scoreValue).label)}</div>
              </div>
              <div className="exec-text">
                <p>{reportResult?.technical_conclusion || "No se pudo determinar una conclusión técnica para esta evaluación."}</p>
                <h4>Alcance de la evaluación</h4>
                <p className="last">Se evaluaron las interfaces frontend del proyecto según los criterios de la norma ISO/IEC 25010.</p>
              </div>
            </div>
          </div>

          {/* Resumen de hallazgos */}
          <div className="pdf-card">
            <h3 className="card-title">Resumen de hallazgos</h3>
            <div className="findings-summary">
              <div className="findings-total">
                <span className="total-num">{summary.total_findings ?? findings.length}</span>
                <span className="total-label">Total hallazgos</span>
              </div>
              <div className="findings-counts">
                <div className="count-box critico">
                  <span className="count-title critico">Críticos</span>
                  <span className="count-val">{summary.severity_summary?.['Crítica'] || 0}</span>
                </div>
                <div className="count-box alto">
                  <span className="count-title alto">Altos</span>
                  <span className="count-val">{summary.severity_summary?.['Alta'] || 0}</span>
                </div>
                <div className="count-box medio">
                  <span className="count-title medio">Medios</span>
                  <span className="count-val">{summary.severity_summary?.['Media'] || 0}</span>
                </div>
                <div className="count-box bajo">
                  <span className="count-title bajo">Bajos</span>
                  <span className="count-val">{summary.severity_summary?.['Baja'] || 0}</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        <div className="pdf-col">
          
          {/* Ficha del proyecto */}
          <div className="pdf-card">
            <h3 className="card-title">Ficha del proyecto</h3>
            <table className="info-table">
              <tbody>
                <tr>
                  <td className="info-lbl">URL evaluada</td>
                  <td className="info-val">{sourceLabel}</td>
                </tr>
                <tr>
                  <td className="info-lbl">Tipo de evaluación</td>
                  <td className="info-val">{inputType?.toUpperCase() || 'URL'}</td>
                </tr>
                <tr>
                  <td className="info-lbl">Fecha de evaluación</td>
                  <td className="info-val">{reportResult?.generated_at || "No especificado"}</td>
                </tr>
                <tr>
                  <td className="info-lbl">Interfaces evaluadas</td>
                  <td className="info-val">{summary.total_interfaces ?? 3}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Resultados ISO/IEC 25010 */}
          <div className="pdf-card">
            <h3 className="card-title">Resultados ISO/IEC 25010</h3>
            <div className="chars-list">
              {Object.entries(scoreLabels).map(([key, label], idx) => {
                 const score = typeof scores[key] === "number" ? scores[key] : null;
                 return (
                <div className="char-item" key={idx}>
                  <div className="char-name">{label}</div>
                  <div className="char-bar-bg">
                    <div className="char-bar-fill" style={{ width: `${score ?? 0}%` }}></div>
                  </div>
                  <div className="char-score">{score === null ? "N/D" : `${score}/100`}</div>
                </div>
              )})}
            </div>
          </div>
        </div>
      </div>

      {/* Findings detail */}
      <div className="pdf-card findings-detail-card">
        <div className="findings-detail-header">
          <h3 className="card-title">Detalle de hallazgos técnicos</h3>
        </div>
        <div className="findings-table-wrapper">
          <table className="findings-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Dimensión</th>
                <th>Descripción</th>
                <th>Severidad</th>
                <th>Recomendación</th>
              </tr>
            </thead>
            <tbody>
              {findings.length > 0 ? findings.map((f, i) => (
                <tr key={i}>
                  <td>H-{String(i+1).padStart(2, '0')}</td>
                  <td>{f.dimension || 'Accesibilidad'}</td>
                  <td className="desc">{f.finding?.replace('[VIOLACIÓN]', '') || 'N/A'}</td>
                  <td>
                    <span style={{ 
                      padding: '4px 10px', 
                      borderRadius: '99px', 
                      fontSize: '11px', 
                      fontWeight: '600',
                      backgroundColor: getBadgeClassUI(f.severity).includes('alta') ? '#fee2e2' : getBadgeClassUI(f.severity).includes('media') ? '#fef3c7' : '#d1fae5',
                      color: getBadgeClassUI(f.severity).includes('alta') ? '#ef4444' : getBadgeClassUI(f.severity).includes('media') ? '#f59e0b' : '#10b981',
                      border: `1px solid ${getBadgeClassUI(f.severity).includes('alta') ? '#fca5a5' : getBadgeClassUI(f.severity).includes('media') ? '#fcd34d' : '#86efac'}`
                    }}>{f.severity || 'Media'}</span>
                  </td>
                  <td>{f.recommendation || 'N/A'}</td>
                </tr>
              )) : (
                <tr><td colSpan="5" className="findings-empty">No se encontraron hallazgos técnicos.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
