import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../context/AuthContext";
import { fetchUserRuns, fetchRunFindings } from "../services/historyService";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
} from "recharts";
import "./Home.css";
import { getQualityLevel, toScore } from "../utils/qualityLevel";

// Características ISO/IEC 25010 que persiste cada análisis (analysis_runs.scores).
const ISO_CHARACTERISTICS = {
  adecuacion_funcional: "Adecuación funcional",
  eficiencia_desempeno: "Eficiencia de desempeño",
  usabilidad: "Usabilidad",
  accesibilidad: "Accesibilidad",
  mantenibilidad: "Mantenibilidad",
  compatibilidad: "Compatibilidad",
  seguridad: "Seguridad",
  portabilidad: "Portabilidad",
};

const SEVERITY_ORDER = ["Crítica", "Alta", "Media", "Baja"];

const formatDate = (iso) => {
  const d = new Date(iso);
  return `${d.getDate()} ${d.toLocaleString("es", { month: "short" })} ${d.getFullYear()}`;
};

const formatTime = (iso) =>
  new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit", hour12: true });

const siteName = (run) => run?.projects?.project_name || "Proyecto";

function ScorePill({ score }) {
  const level = getQualityLevel(score);
  return (
    <span className="score-pill" style={{ color: level.color, borderColor: level.color }}>
      {toScore(score) ?? "N/D"}
    </span>
  );
}

export default function Home() {
  const { user } = useAuth();
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
        console.error("No se pudo cargar el historial de análisis:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [user]);

  const latest = runs[0];
  const previous = runs[1];

  // Indicadores calculados únicamente con datos persistidos.
  const stats = useMemo(() => {
    const scored = runs.map((r) => toScore(r.global_score)).filter((s) => s !== null);
    const avgScore = scored.length
      ? Math.round(scored.reduce((a, s) => a + s, 0) / scored.length)
      : null;
    const sites = new Set(runs.map((r) => r.projects?.project_name).filter(Boolean)).size;

    const latestScore = toScore(latest?.global_score);
    const prevScore = toScore(previous?.global_score);
    const delta = latestScore !== null && prevScore !== null ? latestScore - prevScore : null;

    return { evaluaciones: runs.length, sites, avgScore, latestScore, delta };
  }, [runs, latest, previous]);

  const severityCounts = useMemo(() => {
    const counts = Object.fromEntries(SEVERITY_ORDER.map((s) => [s, 0]));
    latestFindings.forEach((f) => {
      if (f.severity in counts) counts[f.severity]++;
    });
    return counts;
  }, [latestFindings]);

  const priorityFindings = useMemo(() => {
    const rank = (s) => {
      const i = SEVERITY_ORDER.indexOf(s);
      return i === -1 ? SEVERITY_ORDER.length : i;
    };
    return [...latestFindings]
      .sort((a, b) => rank(a.severity) - rank(b.severity))
      .slice(0, 5);
  }, [latestFindings]);

  // Promedio por característica ISO/IEC 25010 en los análisis que la registran.
  const isoAverages = useMemo(() => {
    return Object.entries(ISO_CHARACTERISTICS)
      .map(([key, label]) => {
        const values = runs.map((r) => toScore(r.scores?.[key])).filter((v) => v !== null);
        if (values.length === 0) return null;
        return { key, label, value: Math.round(values.reduce((a, v) => a + v, 0) / values.length) };
      })
      .filter(Boolean)
      .sort((a, b) => a.value - b.value);
  }, [runs]);

  const lineChartData = useMemo(
    () =>
      [...runs]
        .reverse()
        .slice(-10)
        .map((r) => {
          const d = new Date(r.created_at);
          return {
            dateStr: `${d.getDate()} ${d.toLocaleString("es", { month: "short" })}`,
            site: siteName(r),
            score: toScore(r.global_score),
          };
        }),
    [runs]
  );

  const latestLevel = getQualityLevel(stats.latestScore);
  const criticalCount = severityCounts["Crítica"] + severityCounts["Alta"];

  return (
    <div className="home-layout">
      <Sidebar />
      <main className="home-main">
        <div className="dashboard-header">
          <div className="dashboard-header-text">
            <h1>Panel de evaluaciones</h1>
            <p>Estado de calidad de tus interfaces según ISO/IEC 25010 y WCAG 2.2.</p>
          </div>
          <Link to="/input" className="new-analysis-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Iniciar análisis
          </Link>
        </div>

        {loading ? (
          <div className="empty-state">Cargando métricas...</div>
        ) : runs.length === 0 ? (
          <div className="dash-card empty-onboarding">
            <h3>Aún no tienes evaluaciones</h3>
            <p>Analiza la URL de tu sitio para obtener su puntaje de calidad, hallazgos y recomendaciones.</p>
            <Link to="/input" className="new-analysis-btn">Iniciar primer análisis</Link>
          </div>
        ) : (
          <>
            {/* KPIs */}
            <div className="stats-grid">
              <div className="stat-card stat-card--highlight" style={{ borderTopColor: latestLevel.color }}>
                <span className="stat-title">Último puntaje</span>
                <span className="stat-value">
                  {stats.latestScore ?? "N/D"} <small>/ 100</small>
                </span>
                <span className="stat-sub">
                  <span className="level-tag" style={{ background: latestLevel.color }}>{latestLevel.label}</span>
                  {stats.delta !== null && (
                    <span className={`delta ${stats.delta > 0 ? "up" : stats.delta < 0 ? "down" : ""}`}>
                      {stats.delta > 0 ? "▲" : stats.delta < 0 ? "▼" : "="} {Math.abs(stats.delta)} vs. análisis anterior
                    </span>
                  )}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-title">Hallazgos del último análisis</span>
                <span className="stat-value">{latest?.total_findings ?? latestFindings.length}</span>
                <span className="stat-sub">
                  {criticalCount > 0 ? (
                    <span className="delta down">{criticalCount} de prioridad crítica o alta</span>
                  ) : (
                    <span className="muted">Sin hallazgos críticos ni altos</span>
                  )}
                </span>
              </div>
              <div className="stat-card">
                <span className="stat-title">Promedio de calidad</span>
                <span className="stat-value">
                  {stats.avgScore ?? "N/D"} <small>/ 100</small>
                </span>
                <span className="stat-sub muted">En {stats.evaluaciones} {stats.evaluaciones === 1 ? "evaluación" : "evaluaciones"}</span>
              </div>
              <div className="stat-card">
                <span className="stat-title">Sitios analizados</span>
                <span className="stat-value">{stats.sites}</span>
                <span className="stat-sub muted">URLs distintas evaluadas</span>
              </div>
            </div>

            <div className="dashboard-grid">
              <div className="grid-column">
              {/* Recomendaciones prioritarias */}
              <section className="dash-card">
                <div className="dash-card-header">
                  <div>
                    <h3>Qué corregir primero</h3>
                    <p className="dash-card-sub">
                      Último análisis: <strong>{siteName(latest)}</strong> · {formatDate(latest.created_at)}
                    </p>
                  </div>
                  <Link to="/history" className="dash-card-link">Ver en historial &rarr;</Link>
                </div>

                <div className="severity-strip">
                  {SEVERITY_ORDER.map((s) => (
                    <div key={s} className={`severity-chip sev-${s}`}>
                      <span className="severity-count">{severityCounts[s]}</span>
                      <span>{s}</span>
                    </div>
                  ))}
                </div>

                {priorityFindings.length === 0 ? (
                  <div className="empty-state">El último análisis no registró hallazgos.</div>
                ) : (
                  <ul className="priority-list">
                    {priorityFindings.map((f) => (
                      <li key={f.id} className="priority-item">
                        <span className={`priority-badge sev-${f.severity}`}>{f.severity}</span>
                        <div className="priority-text">
                          <p className="priority-rec">{f.recommendation}</p>
                          {f.dimension && f.dimension !== "No especificada" && (
                            <span className="priority-dim">{f.dimension}</span>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              {/* Evolución */}
              <section className="dash-card">
                <div className="dash-card-header">
                  <h3>Evolución del puntaje</h3>
                  <span className="dash-card-sub">Últimos {lineChartData.length} análisis</span>
                </div>
                {lineChartData.length < 2 ? (
                  <div className="empty-state">Se necesitan al menos dos análisis para mostrar la tendencia.</div>
                ) : (
                  <div style={{ width: "100%", height: "200px" }}>
                    <ResponsiveContainer>
                      <LineChart data={lineChartData} margin={{ top: 10, right: 16, bottom: 0, left: -20 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="dateStr" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 11 }} dy={8} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 11 }} domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} />
                        <RechartsTooltip
                          cursor={{ stroke: "#e2e8f0", strokeWidth: 1 }}
                          contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: 12 }}
                          labelFormatter={(_, p) => p?.[0]?.payload?.site || ""}
                          formatter={(v) => [`${v} / 100`, "Puntaje"]}
                        />
                        <Line type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2} dot={{ fill: "#2563eb", r: 3, strokeWidth: 2, stroke: "white" }} activeDot={{ r: 5 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </section>

              </div>
              <div className="grid-column">
              {/* Características ISO/IEC 25010 */}
              <section className="dash-card">
                <div className="dash-card-header">
                  <div>
                    <h3>Calidad por característica</h3>
                    <p className="dash-card-sub">Promedio ISO/IEC 25010 · de menor a mayor</p>
                  </div>
                </div>
                {isoAverages.length === 0 ? (
                  <div className="empty-state">
                    Tus análisis aún no registran puntajes por característica.
                  </div>
                ) : (
                  <div className="criteria-list">
                    {isoAverages.map((c) => {
                      const level = getQualityLevel(c.value);
                      return (
                        <div className="criteria-item" key={c.key}>
                          <div className="criteria-label">{c.label}</div>
                          <div className="criteria-bar-bg">
                            <div className="criteria-bar-fill" style={{ width: `${c.value}%`, background: level.color }} />
                          </div>
                          <div className="criteria-score">{c.value}</div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>

              {/* Últimas evaluaciones */}
              <section className="dash-card">
                <div className="dash-card-header">
                  <h3>Últimas evaluaciones</h3>
                  <Link to="/history" className="dash-card-link">Ver historial &rarr;</Link>
                </div>
                <ul className="recent-list">
                  {runs.slice(0, 5).map((run) => (
                    <li key={run.id} className="recent-item">
                      <div className="recent-info">
                        <span className="recent-site">{siteName(run)}</span>
                        <span className="recent-date">
                          {formatDate(run.created_at)} · {formatTime(run.created_at)} · {run.total_findings ?? 0} hallazgos
                        </span>
                      </div>
                      <ScorePill score={run.global_score} />
                    </li>
                  ))}
                </ul>
              </section>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
