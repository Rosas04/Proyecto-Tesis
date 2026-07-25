import React, { useMemo } from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LabelList
} from 'recharts';
import './ReportDashboard.css';

export const ReportDashboard = React.forwardRef(({ reportResult, sourceLabel, inputType }, ref) => {
  const summary = reportResult?.summary || {};
  const scores = reportResult?.scores || {};
  const findings = Array.isArray(reportResult?.findings) ? reportResult.findings : [];
  const recommendations = Array.isArray(reportResult?.main_recommendations) ? reportResult.main_recommendations : [];

  const dimensionData = useMemo(() => {
    const counts = {};
    findings.forEach(f => {
      const dim = f.dimension || 'Otros';
      counts[dim] = (counts[dim] || 0) + 1;
    });
    return Object.keys(counts).map(key => ({
      name: key,
      count: counts[key]
    })).sort((a, b) => b.count - a.count);
  }, [findings]);

  const globalScore = summary.global_score ?? 0;
  const pieData = [
    { name: 'Score', value: globalScore },
    { name: 'Rest', value: 100 - globalScore }
  ];
  const COLORS = ['#2563eb', '#e2e8f0'];

  const severityData = useMemo(() => {
    const s = summary.severity_summary || {};
    return [
      { name: 'Crítica', count: s['Crítica'] || 0, fill: '#ef4444' },
      { name: 'Alta', count: s['Alta'] || 0, fill: '#f97316' },
      { name: 'Media', count: s['Media'] || 0, fill: '#f59e0b' },
      { name: 'Baja', count: s['Baja'] || 0, fill: '#0ea5e9' },
    ];
  }, [summary.severity_summary]);

  return (
    <div className="pdf-report-wrapper" ref={ref}>
      {/* PAGE 1: Executive Dashboard */}
      <div className="pdf-page page-1">
        <div className="pdf-header">
          <div>
            <h1>Reporte Técnico ISO/IEC 25010</h1>
            <p>Evaluación de Calidad de Software Frontend</p>
          </div>
          <div className="pdf-branding">
            <span>FrontMind AI</span>
            <p>{reportResult?.generated_at}</p>
          </div>
        </div>

        <div className="pdf-grid-top">
          <div className="pdf-card">
            <h3>Puntaje Global</h3>
            <div className="pdf-score-container">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    startAngle={90}
                    endAngle={-270}
                    dataKey="value"
                    stroke="none"
                    isAnimationActive={false}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ position: 'absolute', textAlign: 'center', fontWeight: '800', fontSize: '48px', color: '#0f172a' }}>
                {globalScore}
              </div>
            </div>
          </div>

          <div className="pdf-card">
            <h3>Métricas Clave</h3>
            <div className="pdf-metric">
              <div className="pdf-metric-value">{summary.total_interfaces ?? 1}</div>
              <div className="pdf-metric-label">Interfaces Analizadas</div>
            </div>
          </div>

          <div className="pdf-card">
            <h3>Hallazgos Detectados</h3>
            <div className="pdf-metric">
              <div className="pdf-metric-value" style={{ color: '#ef4444' }}>{summary.total_findings ?? findings.length}</div>
              <div className="pdf-metric-label">Incidencias Encontradas</div>
            </div>
          </div>
        </div>

        <div className="pdf-grid-main">
          <div className="pdf-card">
            <h3>Hallazgos por Dimensión</h3>
            <div className="pdf-chart-area">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dimensionData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 11, fontWeight: 600}} width={120} />
                  <Tooltip cursor={{fill: '#f1f5f9'}} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} isAnimationActive={false}>
                    <LabelList dataKey="count" position="right" fill="#475569" fontWeight="bold" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pdf-card">
            <h3>Información General</h3>
            <ul className="pdf-info-list">
              <li>
                <span className="info-label">Fuente</span>
                <span className="info-value">{sourceLabel}</span>
              </li>
              <li>
                <span className="info-label">Tipo Entrada</span>
                <span className="info-value">{inputType.toUpperCase()}</span>
              </li>
              <li>
                <span className="info-label">Calidad Global</span>
                <span className="info-value" style={{ color: '#2563eb' }}>{summary.quality_level || 'No calculado'}</span>
              </li>
              {summary.best_interface && (
                <li>
                  <span className="info-label">Mejor Interfaz</span>
                  <span className="info-value">{summary.best_interface}</span>
                </li>
              )}
            </ul>
          </div>
        </div>

        <div className="pdf-footer">
          <span>Generado por FrontMind AI</span>
          <span>Página 1 de 2</span>
        </div>
      </div>

      {/* PAGE 2: Details & Recommendations */}
      <div className="pdf-page page-2">
        <div className="pdf-header">
          <div>
            <h1>Análisis Detallado</h1>
            <p>Severidad y Recomendaciones Técnicas</p>
          </div>
          <div className="pdf-branding">
            <span>FrontMind AI</span>
          </div>
        </div>

        <div className="pdf-grid-main" style={{ gridTemplateColumns: '1fr 2fr' }}>
          <div className="pdf-card">
            <h3>Distribución de Severidad</h3>
            <div className="pdf-chart-bar">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityData} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 13}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <Tooltip cursor={{fill: '#f1f5f9'}} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]} isAnimationActive={false}>
                    <LabelList dataKey="count" position="top" fill="#475569" fontWeight="bold" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pdf-card" style={{ padding: '0', background: 'transparent', boxShadow: 'none', border: 'none' }}>
            <h3 style={{ marginLeft: '10px' }}>Recomendaciones Prioritarias</h3>
            <div className="pdf-recommendations" style={{ marginTop: '10px' }}>
              {recommendations.slice(0, 4).map((rec, idx) => (
                <div key={idx} className="pdf-rec-item">
                  {rec}
                </div>
              ))}
            </div>
          </div>
        </div>

        {findings.length > 0 && (
          <div className="pdf-table-container">
            <table className="pdf-table">
              <thead>
                <tr>
                  <th style={{ width: '5%' }}>N°</th>
                  <th style={{ width: '20%' }}>Dimensión</th>
                  <th style={{ width: '15%' }}>Severidad</th>
                  <th style={{ width: '30%' }}>Hallazgo</th>
                  <th style={{ width: '30%' }}>Recomendación</th>
                </tr>
              </thead>
              <tbody>
                {findings.slice(0, 7).map((item, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td><strong>{item.dimension || 'N/A'}</strong></td>
                    <td>
                      <span className={`pdf-badge ${item.severity?.toLowerCase() || 'media'}`}>
                        {item.severity || 'Media'}
                      </span>
                    </td>
                    <td>{item.finding?.replace('[VIOLACIÓN]', '') || 'N/A'}</td>
                    <td>{item.recommendation || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="pdf-footer">
          <span>Generado por FrontMind AI</span>
          <span>Página 2 de 2</span>
        </div>
      </div>
    </div>
  );
});
