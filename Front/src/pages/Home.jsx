import React, { useEffect, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { fetchUserRuns, fetchRunFindings } from "../historyService";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import "./Home.css";

// --- Icons ---
const DocIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
);

const LinkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
  </svg>
);

const CodeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6"/>
    <polyline points="8 6 2 12 8 18"/>
  </svg>
);

const ShieldCheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>
);

const ArrowUpIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="19" x2="12" y2="5"/>
    <polyline points="5 12 12 5 19 12"/>
  </svg>
);

const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [runs, setRuns] = useState([]);
  const [latestFindings, setLatestFindings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchUserRuns(user.id);
        setRuns(data || []);
        
        if (data && data.length > 0) {
          const findingsData = await fetchRunFindings(data[0].id);
          setLatestFindings(findingsData || []);
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [user]);

  // Derived Stats
  const stats = useMemo(() => {
    const evaluaciones = runs.length;
    const urls = new Set(runs.map(r => r.projects?.project_name)).size;
    const interfaces = runs.reduce((acc, r) => acc + (r.total_interfaces || 3), 0); // Mock interface count if not present
    const avgScore = evaluaciones > 0 
      ? Math.round(runs.reduce((acc, r) => acc + r.global_score, 0) / evaluaciones)
      : 0;
      
    return { evaluaciones, urls, interfaces, avgScore };
  }, [runs]);

  // Chart Data
  const lineChartData = useMemo(() => {
    // Reverse to show oldest to newest
    return [...runs].reverse().slice(-10).map(r => {
      const date = new Date(r.created_at);
      return {
        dateStr: `${date.getDate()} ${date.toLocaleString('es', { month: 'short' })}`,
        score: r.global_score
      };
    });
  }, [runs]);

  // Pie Chart Data
  const pieDataInfo = useMemo(() => {
    let counts = { excelente: 0, bueno: 0, regular: 0, deficiente: 0 };
    runs.forEach(r => {
      if (r.global_score >= 80) counts.excelente++;
      else if (r.global_score >= 60) counts.bueno++;
      else if (r.global_score >= 40) counts.regular++;
      else counts.deficiente++;
    });
    
    const total = runs.length || 1;
    
    const data = [
      { name: 'Excelente (80-100)', count: counts.excelente, color: '#10b981' },
      { name: 'Bueno (60-79)', count: counts.bueno, color: '#f59e0b' },
      { name: 'Regular (40-59)', count: counts.regular, color: '#f97316' },
      { name: 'Deficiente (0-39)', count: counts.deficiente, color: '#ef4444' }
    ];
    
    return { data, total };
  }, [runs]);

  // Helper for score circles
  const getScoreClass = (score) => {
    if (score >= 80) return "excellent";
    if (score >= 60) return "high";
    if (score >= 40) return "medium";
    return "low";
  };

  // Mock Criteria Data based on global avg for demonstration
  const criteriaData = [
    { label: "Adecuación funcional", score: Math.min(100, stats.avgScore + Math.floor(Math.random() * 5)) },
    { label: "Eficiencia de desempeño", score: Math.max(0, stats.avgScore - Math.floor(Math.random() * 5)) },
    { label: "Usabilidad", score: Math.min(100, stats.avgScore + Math.floor(Math.random() * 2)) },
    { label: "Accesibilidad", score: Math.max(0, stats.avgScore - 10) },
    { label: "Mantenibilidad", score: Math.min(100, stats.avgScore + 2) },
    { label: "Compatibilidad", score: Math.max(0, stats.avgScore - 3) },
    { label: "Seguridad", score: Math.max(0, stats.avgScore - 6) },
    { label: "Portabilidad", score: Math.min(100, stats.avgScore + 1) }
  ];

  return (
    <div className="home-layout">
      <Sidebar />
      <main className="home-main">
        <div className="dashboard-header">
          <div className="dashboard-header-text">
            <h1>Panel de evaluaciones</h1>
            <p>Revisa el resumen general de tus análisis y accede a los detalles de cada evaluación.</p>
          </div>
          <div className="header-actions">
            <Link to="/input" className="new-analysis-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Iniciar análisis
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">Cargando métricas...</div>
        ) : (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon"><DocIcon /></div>
                <div className="stat-info">
                  <span className="stat-title">Evaluaciones realizadas</span>
                  <span className="stat-value">{stats.evaluaciones}</span>
                  <span className="stat-trend up"><ArrowUpIcon /> 2 vs. mes anterior</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><LinkIcon /></div>
                <div className="stat-info">
                  <span className="stat-title">URLs analizadas</span>
                  <span className="stat-value">{stats.urls}</span>
                  <span className="stat-trend up"><ArrowUpIcon /> 2 vs. mes anterior</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><CodeIcon /></div>
                <div className="stat-info">
                  <span className="stat-title">Interfaces evaluadas</span>
                  <span className="stat-value">{stats.interfaces}</span>
                  <span className="stat-trend up"><ArrowUpIcon /> 12 vs. mes anterior</span>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><ShieldCheckIcon /></div>
                <div className="stat-info">
                  <span className="stat-title">Promedio de calidad</span>
                  <span className="stat-value">{stats.avgScore} <small>/ 100</small></span>
                  <span className="stat-trend up"><ArrowUpIcon /> 8% vs. mes anterior</span>
                </div>
              </div>
            </div>

            <div className="dashboard-grid">
              <div className="grid-column">
                <div className="dash-card">
                  <div className="dash-card-header">
                    <h3>Últimas evaluaciones</h3>
                    <Link to="/history" className="dash-card-link">Ver todas &rarr;</Link>
                  </div>
                  {runs.length === 0 ? (
                    <div className="empty-state">No hay evaluaciones recientes.</div>
                  ) : (
                    <table className="recent-table">
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Proyecto / URL</th>
                          <th>Tipo</th>
                          <th>Resultado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {runs.slice(0, 4).map(run => {
                          const date = new Date(run.created_at);
                          const formattedDate = `${date.getDate()} ${date.toLocaleString('es', { month: 'short' })} ${date.getFullYear()}`;
                          const time = date.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit', hour12: true });
                          return (
                            <tr key={run.id}>
                              <td className="date-cell">
                                {formattedDate}
                                <span>{time}</span>
                              </td>
                              <td className="project-cell">
                                {run.projects?.project_name || "Proyecto"}
                                <span>{run.projects?.project_name?.includes('.') ? `https://${run.projects.project_name}` : 'URL Analizada'}</span>
                              </td>
                              <td><span className="type-badge">URL</span></td>
                              <td>
                                <div className="home-score-circle-wrapper">
                                  <div className={`home-score-circle ${getScoreClass(run.global_score)}`}>{run.global_score}</div>
                                  <span className="score-max">/ 100</span>
                                </div>
                              </td>
                              <td>
                                <Link to="/history" className="home-action-btn"><EyeIcon /> Ver detalles</Link>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  )}
                </div>

                <div className="dash-card">
                  <div className="dash-card-header">
                    <h3>Evolución del promedio general</h3>
                  </div>
                  {lineChartData.length < 2 ? (
                    <div className="empty-state" style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      Datos insuficientes para la gráfica
                    </div>
                  ) : (
                    <div style={{ width: '100%', height: '240px' }}>
                      <ResponsiveContainer>
                        <LineChart data={lineChartData} margin={{ top: 20, right: 20, bottom: 0, left: -20 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="dateStr" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 11}} dy={10} />
                          <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 11}} domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} />
                          <RechartsTooltip cursor={{ stroke: '#e2e8f0', strokeWidth: 1 }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                          <Line 
                            type="monotone" 
                            dataKey="score" 
                            stroke="#2563eb" 
                            strokeWidth={2}
                            dot={{ fill: '#2563eb', r: 3, strokeWidth: 2, stroke: 'white' }}
                            activeDot={{ r: 5 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              </div>

              <div className="grid-column">
                <div className="dash-card">
                  <div className="dash-card-header">
                    <h3>Resumen de resultados</h3>
                  </div>
                  <div className="doughnut-container">
                    <div style={{ width: '140px', height: '140px', position: 'relative' }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieDataInfo.data}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={70}
                            paddingAngle={2}
                            dataKey="count"
                            stroke="none"
                            isAnimationActive={false}
                          >
                            {pieDataInfo.data.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: '24px', fontWeight: '800', color: '#0f172a' }}>{stats.avgScore}</span>
                        <span style={{ fontSize: '9px', fontWeight: '600', color: '#64748b', textAlign: 'center', maxWidth: '60px', lineHeight: 1.2 }}>Promedio general</span>
                      </div>
                    </div>
                    
                    <div className="chart-legend">
                      {pieDataInfo.data.map((item, idx) => {
                        const pct = pieDataInfo.total > 0 ? Math.round((item.count / pieDataInfo.total) * 100) : 0;
                        return (
                          <div className="legend-item" key={idx}>
                            <div className="legend-label">
                              <div className="legend-dot" style={{ backgroundColor: item.color }}></div>
                              {item.name}
                            </div>
                            <div className="legend-value">
                              {item.count} <span>{pct}%</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                <div className="dash-card">
                  <div className="dash-card-header">
                    <h3>Desempeño por criterio</h3>
                  </div>
                  <div className="criteria-list">
                    {criteriaData.map((c, i) => (
                      <div className="criteria-item" key={i}>
                        <div className="criteria-label">{c.label}</div>
                        <div className="criteria-bar-bg">
                          <div className="criteria-bar-fill" style={{ width: `${c.score}%` }}></div>
                        </div>
                        <div className="criteria-score">{c.score}<span>/100</span></div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="dash-card">
                  <div className="dash-card-header">
                    <h3>Recomendaciones destacadas</h3>
                    <Link to="/history" className="dash-card-link">Ver todas &rarr;</Link>
                  </div>
                  <table className="recs-table">
                    <thead>
                      <tr>
                        <th>Prioridad</th>
                        <th>Recomendación</th>
                        <th>Aplicable en</th>
                      </tr>
                    </thead>
                    <tbody>
                      {latestFindings.length > 0 ? (
                        latestFindings.slice(0, 3).map((f, i) => (
                          <tr key={i}>
                            <td><span className={`priority-badge ${f.severity}`}>{f.severity}</span></td>
                            <td style={{ maxWidth: '180px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{f.recommendation}</td>
                            <td style={{ textAlign: 'right' }}>{runs[0]?.projects?.project_name || 'General'}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3" className="empty-state" style={{ padding: '20px 0' }}>No hay recomendaciones recientes.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
