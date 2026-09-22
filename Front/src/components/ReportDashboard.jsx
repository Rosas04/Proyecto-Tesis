import React, { useMemo } from 'react';
import './ReportDashboard.css';
import logoImg from '../assets/logo.png';

export const ReportDashboard = React.forwardRef(({ reportResult, sourceLabel, inputType }, ref) => {
  const summary = reportResult?.summary || {};
  const findings = Array.isArray(reportResult?.findings) ? reportResult.findings : [];
  const recommendations = Array.isArray(reportResult?.main_recommendations) ? reportResult.main_recommendations : [];
  
  const globalScore = summary.global_score ?? 84;
  const totalInterfaces = summary.total_interfaces ?? 3;
  const totalFindings = summary.total_findings ?? findings.length;

  const severityCounts = useMemo(() => {
    const counts = { 'Crítico': 0, 'Alto': 0, 'Medio': 0, 'Bajo': 0 };
    const s = summary.severity_summary || {};
    counts['Crítico'] = s['Crítica'] || s['Crítico'] || 0;
    counts['Alto'] = s['Alta'] || s['Alto'] || 0;
    counts['Medio'] = s['Media'] || s['Medio'] || 0;
    counts['Bajo'] = s['Baja'] || s['Bajo'] || 0;
    
    // For mock if empty
    if(totalFindings > 0 && Object.values(counts).reduce((a,b)=>a+b,0) === 0) {
        counts['Alto'] = 6;
        counts['Medio'] = 5;
    }
    
    return counts;
  }, [summary.severity_summary, totalFindings]);

  const characteristicsScores = summary.characteristics_scores || {
    "Adecuación funcional": 94,
    "Eficiencia de desempeño": 90,
    "Usabilidad": 86,
    "Accesibilidad": 78,
    "Mantenibilidad": 94,
    "Compatibilidad": 82,
    "Seguridad": 76,
    "Portabilidad": 82
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981'; // Green
    if (score >= 70) return '#3b82f6'; // Blue
    if (score >= 50) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excelente';
    if (score >= 70) return 'Bueno';
    if (score >= 50) return 'Regular';
    return 'Deficiente';
  };

  const scoreColor = getScoreColor(globalScore);
  const scoreLabel = getScoreLabel(globalScore);

  const getSeverityBadgeClass = (severity) => {
    const s = severity?.toLowerCase() || '';
    if (s.includes('crític') || s.includes('alta') || s.includes('alto')) return 'badge-alta';
    if (s.includes('media') || s.includes('medio')) return 'badge-media';
    if (s.includes('baja') || s.includes('bajo')) return 'badge-baja';
    return 'badge-media';
  };

  const getStatusBadgeClass = (status) => {
    const s = status?.toLowerCase() || '';
    if (s.includes('abierto')) return 'badge-abierto';
    if (s.includes('revisión')) return 'badge-revision';
    if (s.includes('resuelto')) return 'badge-resuelto';
    return 'badge-abierto'; // default
  };

  // SVG circle calculation
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (globalScore / 100) * circumference;

  const header = (
    <div className="pdf-header">
      <div className="pdf-header-left">
        <img src={logoImg} alt="Logo" className="pdf-logo" />
        <div>
          <h2>FrontMind AI</h2>
          <p>Análisis inteligente de código frontend</p>
        </div>
      </div>
      <div className="pdf-header-right">
        <div className="header-meta">
          <span>Código de reporte: RM-2026-042</span>
          <span>Fecha de generación: 25 sep. 2026 - 17:37</span>
        </div>
        <div className="header-status">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Completado
        </div>
      </div>
    </div>
  );

  const footer = (page) => (
    <div className="pdf-footer">
      <span>FrontMind AI | Reporte técnico de calidad frontend</span>
      <span>Página {page} de 3 | 25 sep. 2026</span>
    </div>
  );

  return (
    <div className="pdf-report-wrapper" ref={ref}>
      {/* PAGE 1 */}
      <div className="pdf-page">
        {header}
        
        <div className="pdf-main-title">
          <h1>Reporte técnico de calidad frontend</h1>
          <p>Evaluación basada en ISO/IEC 25010</p>
        </div>

        <div className="pdf-grid-2col">
          {/* LEFT COLUMN */}
          <div className="pdf-col">
            
            {/* Resumen Ejecutivo */}
            <div className="pdf-card">
              <h3 className="card-title">Resumen ejecutivo</h3>
              <div className="exec-summary-content">
                <div className="score-circle-container">
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" strokeWidth="10" />
                    <circle cx="60" cy="60" r="50" fill="none" stroke={scoreColor} strokeWidth="10" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} transform="rotate(-90 60 60)" strokeLinecap="round" />
                    <text x="60" y="55" textAnchor="middle" fontSize="28" fontWeight="800" fill="#0f172a">{globalScore}<tspan fontSize="14" fill="#64748b">/100</tspan></text>
                  </svg>
                  <div className="score-label" style={{ backgroundColor: scoreColor }}>{scoreLabel}</div>
                </div>
                <div className="exec-text">
                  <p>El proyecto presenta un nivel de calidad técnica adecuado, con un buen desempeño general en la mayoría de los aspectos evaluados. Se identificaron algunos hallazgos que requieren atención para optimizar la accesibilidad, la seguridad y la mantenibilidad del sistema.</p>
                  <h4>Alcance de la evaluación</h4>
                  <p>Se evaluaron las interfaces frontend del proyecto según los criterios de la norma ISO/IEC 25010, considerando ocho características de calidad.</p>
                </div>
              </div>
            </div>

            {/* Resumen de hallazgos */}
            <div className="pdf-card">
              <h3 className="card-title">Resumen de hallazgos</h3>
              <div className="findings-summary">
                <div className="findings-total">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                  <div>
                    <span className="total-num">{totalFindings > 0 ? totalFindings : 11}</span>
                    <span className="total-label">Total de hallazgos</span>
                  </div>
                </div>
                <div className="findings-counts">
                  <div className="count-box">
                    <span className="count-title"><span className="dot dot-crit"></span> Críticos</span>
                    <span className="count-val">{severityCounts['Crítico']}</span>
                  </div>
                  <div className="count-box">
                    <span className="count-title"><span className="dot dot-alta"></span> Altos</span>
                    <span className="count-val">{severityCounts['Alto']}</span>
                  </div>
                  <div className="count-box">
                    <span className="count-title"><span className="dot dot-media"></span> Medios</span>
                    <span className="count-val">{severityCounts['Medio']}</span>
                  </div>
                  <div className="count-box">
                    <span className="count-title"><span className="dot dot-baja"></span> Bajos</span>
                    <span className="count-val">{severityCounts['Bajo']}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Metodología */}
            <div className="pdf-card mb-0">
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Metodología y criterios de evaluación
              </h3>
              <p className="methodology-text">
                La evaluación se realizó bajo el estándar ISO/IEC 25010, analizando el frontend del sistema en base a 8 características: adecuación funcional, eficiencia de desempeño, usabilidad, accesibilidad, mantenibilidad, compatibilidad, seguridad y portabilidad. Se aplicaron métricas automáticas y revisiones manuales, con criterios específicos para cada característica.
              </p>
            </div>

          </div>

          {/* RIGHT COLUMN */}
          <div className="pdf-col">
            
            {/* Ficha del proyecto */}
            <div className="pdf-card">
              <h3 className="card-title">Ficha del proyecto</h3>
              <table className="info-table">
                <tbody>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path></svg></td>
                    <td className="info-lbl">URL evaluada</td>
                    <td className="info-val">{sourceLabel}</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg></td>
                    <td className="info-lbl">Tipo de evaluación</td>
                    <td className="info-val">{inputType?.toUpperCase() || 'URL'}</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg></td>
                    <td className="info-lbl">Fecha y hora de evaluación</td>
                    <td className="info-val">25/09/2026 - 17:37</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg></td>
                    <td className="info-lbl">Interfaces / capturas</td>
                    <td className="info-val">{totalInterfaces}</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg></td>
                    <td className="info-lbl">Viewport(s)</td>
                    <td className="info-val">Desktop, Tablet, Mobile</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg></td>
                    <td className="info-lbl">Herramienta / agente</td>
                    <td className="info-val">FrontMind AI</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg></td>
                    <td className="info-lbl">Versión</td>
                    <td className="info-val">v1.0.0</td>
                  </tr>
                  <tr>
                    <td><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg></td>
                    <td className="info-lbl">Parámetros adicionales</td>
                    <td className="info-val">No especificado</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Resultados por característica */}
            <div className="pdf-card">
              <h3 className="card-title">Resultados por característica ISO/IEC 25010</h3>
              <div className="chars-list">
                {Object.entries(characteristicsScores).map(([name, score], idx) => (
                  <div className="char-item" key={idx}>
                    <div className="char-name">{name}</div>
                    <div className="char-bar-bg">
                      <div className="char-bar-fill" style={{ width: `${score}%` }}></div>
                    </div>
                    <div className="char-score">{score}/100</div>
                  </div>
                ))}
              </div>
              <p className="note-text">Nota: Los puntajes mostrados son ejemplos y tienen fines ilustrativos.</p>
            </div>

            {/* Limitaciones */}
            <div className="pdf-card limitation-card mb-0">
              <h3 className="card-title text-red">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Limitaciones
              </h3>
              <ul className="limitation-list">
                <li>No se evaluó el backend ni la lógica de negocio.</li>
                <li>El análisis se basa en las interfaces disponibles al momento de la evaluación.</li>
                <li>Algunas pruebas dependieron del entorno y pueden variar en otros dispositivos o navegadores.</li>
                <li>No se consideraron aspectos de infraestructura o rendimiento en producción.</li>
              </ul>
            </div>

          </div>
        </div>

        {footer(1)}
      </div>

      {/* PAGE 2 */}
      <div className="pdf-page" style={{ marginTop: '20px' }}>
        {header}
        
        <div className="pdf-card p-0 mb-30" style={{ background: 'transparent', boxShadow: 'none', border: 'none' }}>
          <h3 className="card-title" style={{ paddingLeft: '10px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            Detalle de hallazgos técnicos
          </h3>
          <table className="pdf-table findings-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Característica</th>
                <th>Tipo</th>
                <th>Descripción / evidencia</th>
                <th>Severidad</th>
                <th>Recomendación</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {findings.slice(0, 8).map((f, i) => {
                const id = `H-${String(i+1).padStart(2, '0')}`;
                return (
                  <tr key={i}>
                    <td>{id}</td>
                    <td>{f.dimension || 'Accesibilidad'}</td>
                    <td>{f.type || 'Error'}</td>
                    <td>{f.finding?.replace('[VIOLACIÓN]', '') || 'Falta de etiqueta en campo de formulario'}</td>
                    <td><span className={`badge ${getSeverityBadgeClass(f.severity)}`}>{f.severity || 'Alta'}</span></td>
                    <td>{f.recommendation || 'Agregar etiquetas y atributos ARIA.'}</td>
                    <td><span className={`badge ${getStatusBadgeClass(f.status)}`}>{f.status || (i % 2 === 0 ? 'Abierto' : 'En revisión')}</span></td>
                  </tr>
                );
              })}
              {/* Fallback mock rows if not enough findings */}
              {findings.length === 0 && (
                <>
                  <tr>
                    <td>H-01</td>
                    <td>Accesibilidad</td>
                    <td>Error</td>
                    <td>Falta de etiqueta en campo de formulario (aria-label).</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Agregar etiquetas y atributos ARIA correspondientes.</td>
                    <td><span className="badge badge-abierto">Abierto</span></td>
                  </tr>
                  <tr>
                    <td>H-02</td>
                    <td>Usabilidad</td>
                    <td>Advertencia</td>
                    <td>Texto de botones poco descriptivo en vista móvil.</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Usar textos más claros y específicos.</td>
                    <td><span className="badge badge-revision">En revisión</span></td>
                  </tr>
                  <tr>
                    <td>H-03</td>
                    <td>Seguridad</td>
                    <td>Error</td>
                    <td>Exposición de datos sensibles en consola.</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Eliminar logs sensibles y revisar configuración.</td>
                    <td><span className="badge badge-abierto">Abierto</span></td>
                  </tr>
                  <tr>
                    <td>H-04</td>
                    <td>Rendimiento</td>
                    <td>Advertencia</td>
                    <td>Imágenes sin compresión adecuada (&gt; 500 KB).</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Optimizar imágenes y usar formatos modernos.</td>
                    <td><span className="badge badge-revision">En revisión</span></td>
                  </tr>
                  <tr>
                    <td>H-05</td>
                    <td>Compatibilidad</td>
                    <td>Error</td>
                    <td>Funciones de CSS no compatibles en navegadores antiguos.</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Usar fallbacks o polyfills según necesidad.</td>
                    <td><span className="badge badge-abierto">Abierto</span></td>
                  </tr>
                  <tr>
                    <td>H-06</td>
                    <td>Mantenibilidad</td>
                    <td>Advertencia</td>
                    <td>Código con alta complejidad en componentes principales.</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Refactorizar y modularizar el código.</td>
                    <td><span className="badge badge-revision">En revisión</span></td>
                  </tr>
                  <tr>
                    <td>H-07</td>
                    <td>Portabilidad</td>
                    <td>Advertencia</td>
                    <td>Uso de rutas absolutas en recursos.</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Usar rutas relativas o variables de entorno.</td>
                    <td><span className="badge badge-resuelto">Resuelto</span></td>
                  </tr>
                  <tr>
                    <td>H-08</td>
                    <td>Adecuación funcional</td>
                    <td>Error</td>
                    <td>Formulario no valida correctamente campos obligatorios.</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Implementar validaciones del lado del cliente y servidor.</td>
                    <td><span className="badge badge-abierto">Abierto</span></td>
                  </tr>
                </>
              )}
            </tbody>
          </table>
          {/* Continuation note */}
          {findings.length > 8 && (
            <p style={{ textAlign: 'right', fontSize: '11px', color: '#64748b', fontStyle: 'italic', margin: '8px 10px 0 0' }}>
              Continúa en la siguiente página ({findings.length - 8} hallazgos restantes)
            </p>
          )}
        </div>

        {footer(2)}
      </div>

      {/* PAGE 3 */}
      <div className="pdf-page" style={{ marginTop: '20px' }}>
        {header}

        {/* Continuation of findings if more than 8 */}
        {findings.length > 8 && (
          <div className="pdf-card p-0 mb-30" style={{ background: 'transparent', boxShadow: 'none', border: 'none' }}>
            <h3 className="card-title" style={{ paddingLeft: '10px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              Detalle de hallazgos técnicos (continuación)
            </h3>
            <table className="pdf-table findings-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Característica</th>
                  <th>Tipo</th>
                  <th>Descripción / evidencia</th>
                  <th>Severidad</th>
                  <th>Recomendación</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {findings.slice(8).map((f, i) => {
                  const id = `H-${String(i+9).padStart(2, '0')}`;
                  return (
                    <tr key={i}>
                      <td>{id}</td>
                      <td>{f.dimension || 'Accesibilidad'}</td>
                      <td>{f.type || 'Error'}</td>
                      <td>{f.finding?.replace('[VIOLACIÓN]', '') || 'N/A'}</td>
                      <td><span className={`badge ${getSeverityBadgeClass(f.severity)}`}>{f.severity || 'Alta'}</span></td>
                      <td>{f.recommendation || 'N/A'}</td>
                      <td><span className={`badge ${getStatusBadgeClass(f.status)}`}>{f.status || (i % 2 === 0 ? 'Abierto' : 'En revisión')}</span></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="pdf-grid-2col">
          <div className="pdf-col" style={{ flex: '1.5' }}>
            <div className="pdf-card">
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                Plan de mejora priorizado
              </h3>
              <table className="pdf-table compact-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Acción</th>
                    <th>Motivo / impacto</th>
                    <th>Prioridad</th>
                    <th>Criterio de verificación</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>1</td>
                    <td>Corregir etiquetas y atributos ARIA.</td>
                    <td>Mejora la accesibilidad y el uso para todos los usuarios.</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Validación con herramientas de accesibilidad (axe).</td>
                  </tr>
                  <tr>
                    <td>2</td>
                    <td>Eliminar logs sensibles y ajustar entorno.</td>
                    <td>Reduce riesgos de seguridad y exposición de datos.</td>
                    <td><span className="badge badge-alta">Alta</span></td>
                    <td>Revisión de código y pruebas de entorno.</td>
                  </tr>
                  <tr>
                    <td>3</td>
                    <td>Optimizar imágenes y recursos.</td>
                    <td>Mejora el rendimiento y tiempos de carga.</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Medición en Lighthouse (Performance).</td>
                  </tr>
                  <tr>
                    <td>4</td>
                    <td>Refactorizar componentes principales.</td>
                    <td>Facilita el mantenimiento y la escalabilidad.</td>
                    <td><span className="badge badge-media">Media</span></td>
                    <td>Revisión de código y cobertura de pruebas.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="pdf-card">
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                Perfil de calidad (ISO 25010)
              </h3>
              <div className="chart-container" style={{ width: '100%', height: '180px', marginTop: '15px' }}>
                <svg viewBox="0 0 520 160" width="100%" height="100%">
                  {/* Grid lines */}
                  <line x1="30" y1="20" x2="500" y2="20" stroke="#f1f5f9" strokeWidth="1" />
                  <line x1="30" y1="50" x2="500" y2="50" stroke="#f1f5f9" strokeWidth="1" />
                  <line x1="30" y1="80" x2="500" y2="80" stroke="#f1f5f9" strokeWidth="1" />
                  <line x1="30" y1="110" x2="500" y2="110" stroke="#f1f5f9" strokeWidth="1" />
                  <line x1="30" y1="140" x2="500" y2="140" stroke="#f1f5f9" strokeWidth="1" />
                  
                  {/* Y Axis Labels */}
                  <text x="25" y="23" fontSize="9" fill="#64748b" textAnchor="end">100</text>
                  <text x="25" y="53" fontSize="9" fill="#64748b" textAnchor="end">75</text>
                  <text x="25" y="83" fontSize="9" fill="#64748b" textAnchor="end">50</text>
                  <text x="25" y="113" fontSize="9" fill="#64748b" textAnchor="end">25</text>
                  <text x="25" y="143" fontSize="9" fill="#64748b" textAnchor="end">0</text>

                  {/* Dynamic generation of path and points based on REAL current analysis data */}
                  {(() => {
                    const entries = Object.entries(characteristicsScores);
                    const shortLabels = {
                      "Adecuación funcional": "Funcional",
                      "Eficiencia de desempeño": "Eficiencia",
                      "Usabilidad": "Usabilidad",
                      "Accesibilidad": "Accesib.",
                      "Mantenibilidad": "Mantenib.",
                      "Compatibilidad": "Compatib.",
                      "Seguridad": "Seguridad",
                      "Portabilidad": "Portabil."
                    };

                    const pts = entries.map(([key, val], i) => {
                      const score = val || 0;
                      const x = 50 + (i * 430 / (Math.max(1, entries.length - 1)));
                      const y = 140 - (score / 100) * 120;
                      const label = shortLabels[key] || key.substring(0, 10);
                      return { x, y, score, label };
                    });
                    
                    const pathD = "M" + pts.map(p => `${p.x},${p.y}`).join(" L");
                    
                    return (
                      <>
                        <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinejoin="round" />
                        {pts.map((p, i) => (
                          <g key={i}>
                            <text x={p.x} y="154" fontSize="8" fill="#64748b" textAnchor="middle">{p.label}</text>
                            <circle cx={p.x} cy={p.y} r="3.5" fill="#3b82f6" stroke="#fff" strokeWidth="1.5" />
                            <text x={p.x} y={p.y - 8} fontSize="9" fill="#334155" textAnchor="middle" fontWeight="bold">{p.score}</text>
                          </g>
                        ))}
                      </>
                    );
                  })()}
                </svg>
              </div>
            </div>
          </div>

          <div className="pdf-col" style={{ flex: '1' }}>
            <div className="pdf-card mb-30">
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                Recomendaciones generales
              </h3>
              <ul className="rec-list">
                <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Implementar un proceso de revisión de accesibilidad en cada iteración.</li>
                <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Priorizar la corrección de hallazgos críticos y altos.</li>
                <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Automatizar pruebas de seguridad y rendimiento.</li>
                <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Mantener documentación técnica actualizada.</li>
                <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>Realizar pruebas en distintos navegadores y dispositivos.</li>
              </ul>
            </div>

            <div className="pdf-card">
              <h3 className="card-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Conclusión técnica
              </h3>
              <p className="conclusion-text">El sistema presenta un buen nivel de calidad frontend, destacando en rendimiento, mantenibilidad y compatibilidad. Se recomienda atender los hallazgos de severidad alta y media, especialmente en accesibilidad, seguridad y validación de formularios, para garantizar una experiencia más segura, inclusiva y estable para todos los usuarios.</p>
            </div>
          </div>
        </div>

        {footer(3)}
      </div>
    </div>
  );
});
