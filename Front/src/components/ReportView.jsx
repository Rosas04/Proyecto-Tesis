import { useEffect, useMemo, useState } from "react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip,
} from "recharts";
import NormativeSection from "./NormativeSection";
import { getQualityLevel, toScore, QUALITY_LEVELS } from "../utils/qualityLevel";
import "./ReportView.css";

const CHARACTERISTICS = [
  { key: "adecuacion_funcional", label: "Adecuación funcional", short: "Adecuación" },
  { key: "eficiencia_desempeno", label: "Eficiencia de desempeño", short: "Eficiencia" },
  { key: "usabilidad", label: "Usabilidad", short: "Usabilidad" },
  { key: "accesibilidad", label: "Accesibilidad", short: "Accesibilidad" },
  { key: "mantenibilidad", label: "Mantenibilidad", short: "Mantenibilidad" },
  { key: "compatibilidad", label: "Compatibilidad", short: "Compatibilidad" },
  { key: "seguridad", label: "Seguridad", short: "Seguridad" },
  { key: "portabilidad", label: "Portabilidad", short: "Portabilidad" },
];

const SEVERITIES = [
  { key: "Crítica", cls: "critica", color: "#b91c1c" },
  { key: "Alta", cls: "alta", color: "#c2410c" },
  { key: "Media", cls: "media", color: "#b45309" },
  { key: "Baja", cls: "baja", color: "#475569" },
];

const SECTIONS = [
  { id: "rv-resumen", label: "Resumen ejecutivo" },
  { id: "rv-caracteristicas", label: "Resultados ISO/IEC 25010" },
  { id: "rv-hallazgos", label: "Hallazgos técnicos" },
  { id: "rv-recomendaciones", label: "Plan de acción" },
  { id: "rv-normativo", label: "Marco normativo" },
];

const severityOf = (f) => {
  const s = (f?.severity || "").toLowerCase();
  if (s.startsWith("crít") || s.startsWith("crit")) return "Crítica";
  if (s.startsWith("alt")) return "Alta";
  if (s.startsWith("baj")) return "Baja";
  return "Media";
};

const parseGeneratedAt = (value) => {
  if (!value) return null;
  const iso = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(value) ? `${value.replace(" ", "T")}Z` : value;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
};

/** Separa la descripción del ejemplo de código "(Ejemplo: ...)" que adjunta el evaluador. */
const splitExample = (text) => {
  const clean = (text || "Hallazgo no especificado").replace("[VIOLACIÓN]", "").trim();
  const i = clean.search(/\((Ejemplo|Ejemplos):/i);
  if (i === -1) return { text: clean, example: "" };
  return {
    text: clean.slice(0, i).trim(),
    example: clean.slice(i).replace(/^\((Ejemplo|Ejemplos):\s*/i, "").replace(/\)\s*$/, ""),
  };
};

/** Anima un número de 0 al valor final (respeta prefers-reduced-motion). */
function useCountUp(target, duration = 900) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (target === null || target === undefined) return undefined;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    let frame;
    const start = performance.now() - (reduce ? duration : 0);
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      setValue(Math.round(target * (1 - Math.pow(1 - t, 3))));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);
  return value;
}

function ScoreGauge({ score }) {
  const level = getQualityLevel(score);
  const shown = useCountUp(score);
  const r = 62;
  const c = 2 * Math.PI * r;
  const [drawn, setDrawn] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setDrawn(true));
    return () => cancelAnimationFrame(id);
  }, []);
  return (
    <div className="rv-gauge">
      <svg width="156" height="156" viewBox="0 0 156 156" role="img" aria-label={`Puntaje global ${score ?? "N/D"} de 100`}>
        <circle cx="78" cy="78" r={r} fill="none" stroke="#e2e8f0" strokeWidth="11" />
        <circle
          cx="78" cy="78" r={r} fill="none" stroke={level.color} strokeWidth="11" strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={drawn ? c - ((score ?? 0) / 100) * c : c}
          transform="rotate(-90 78 78)"
          className="rv-gauge-arc"
        />
      </svg>
      <div className="rv-gauge-center">
        <span className="rv-gauge-value">{score === null ? "N/D" : shown}</span>
        <span className="rv-gauge-max">de 100</span>
      </div>
    </div>
  );
}

export default function ReportView({
  reportResult, sourceLabel, inputType, onDownload, generatingPdf, onBack, onNew,
}) {
  const summary = reportResult?.summary || {};
  const scores = useMemo(() => reportResult?.scores || {}, [reportResult]);
  const findings = useMemo(
    () => (Array.isArray(reportResult?.findings) ? reportResult.findings : []),
    [reportResult]
  );
  const score = toScore(summary.global_score);
  const level = getQualityLevel(score);
  const decision = reportResult?.quality_decision;

  const generated = parseGeneratedAt(reportResult?.generated_at);
  const pad = (n) => String(n).padStart(2, "0");
  const reportCode = generated
    ? `RM-${generated.getFullYear()}${pad(generated.getMonth() + 1)}${pad(generated.getDate())}-${pad(generated.getHours())}${pad(generated.getMinutes())}`
    : "—";
  const dateLabel = generated
    ? `${generated.toLocaleDateString("es-PE", { day: "numeric", month: "long", year: "numeric" })}, ${generated.toLocaleTimeString("es-PE", { hour: "2-digit", minute: "2-digit", hour12: false })}`
    : "No especificada";

  // Severidades: se usan las del backend y, si faltan, se cuentan los hallazgos.
  const severityCounts = useMemo(() => {
    const fromBackend = summary.severity_summary;
    const counts = Object.fromEntries(SEVERITIES.map((s) => [s.key, 0]));
    if (fromBackend && typeof fromBackend === "object") {
      SEVERITIES.forEach((s) => { counts[s.key] = Number(fromBackend[s.key]) || 0; });
    } else {
      findings.forEach((f) => { counts[severityOf(f)]++; });
    }
    return counts;
  }, [summary.severity_summary, findings]);
  const totalFindings = summary.total_findings ?? findings.length;
  const severityTotal = Object.values(severityCounts).reduce((a, b) => a + b, 0);

  const charRows = useMemo(
    () => CHARACTERISTICS.map((c) => ({ ...c, value: toScore(scores[c.key]) })),
    [scores]
  );
  const measured = charRows.filter((c) => c.value !== null);
  const sortedChars = [...measured].sort((a, b) => a.value - b.value);
  const weakest = sortedChars[0];
  const strongest = sortedChars[sortedChars.length - 1];
  const radarData = measured.map((c) => ({ name: c.short, value: c.value, full: c.label }));

  const dimensions = useMemo(() => {
    const set = new Set(findings.map((f) => f.dimension).filter(Boolean));
    return ["Todas", ...set];
  }, [findings]);

  const [sevFilter, setSevFilter] = useState("Todas");
  const [dimFilter, setDimFilter] = useState("Todas");
  const [openId, setOpenId] = useState(null);

  const indexedFindings = useMemo(
    () => findings.map((f, i) => ({ ...f, _id: `H-${String(i + 1).padStart(2, "0")}`, _sev: severityOf(f) })),
    [findings]
  );
  const visibleFindings = indexedFindings.filter(
    (f) => (sevFilter === "Todas" || f._sev === sevFilter) && (dimFilter === "Todas" || f.dimension === dimFilter)
  );

  // Plan de acción: recomendación única con la severidad más alta que la origina.
  const actionPlan = useMemo(() => {
    const rank = (s) => SEVERITIES.findIndex((x) => x.key === s);
    const map = new Map();
    indexedFindings.forEach((f) => {
      const rec = (f.recommendation || "").trim();
      if (!rec || rec === "Sin recomendación registrada.") return;
      const prev = map.get(rec);
      if (!prev) map.set(rec, { rec, sev: f._sev, dims: new Set([f.dimension].filter(Boolean)), refs: [f._id] });
      else {
        if (rank(f._sev) < rank(prev.sev)) prev.sev = f._sev;
        if (f.dimension) prev.dims.add(f.dimension);
        prev.refs.push(f._id);
      }
    });
    return [...map.values()].sort((a, b) => rank(a.sev) - rank(b.sev));
  }, [indexedFindings]);

  const hasNormative = Boolean(
    reportResult?.quality_decision ||
    (Array.isArray(reportResult?.metrics) && reportResult.metrics.length) ||
    reportResult?.evaluation_scope
  );
  const sections = hasNormative ? SECTIONS : SECTIONS.filter((s) => s.id !== "rv-normativo");

  // Dictamen: la conclusión del backend o, si falta, un resumen construido con los datos medidos.
  const conclusion = useMemo(() => {
    if (reportResult?.technical_conclusion) return reportResult.technical_conclusion;
    if (score === null) return "No se registró una conclusión técnica para esta evaluación.";
    const parts = SEVERITIES.filter((s) => severityCounts[s.key] > 0).map(
      (s) => `${severityCounts[s.key]} de severidad ${s.key.toLowerCase()}`
    );
    let text = `La interfaz evaluada obtuvo ${score}/100, nivel ${(summary.quality_level || level.label).toLowerCase()}, según ISO/IEC 25010.`;
    text += totalFindings
      ? ` Se identificaron ${totalFindings} hallazgos${parts.length ? ` (${parts.join(", ")})` : ""}.`
      : " No se identificaron hallazgos.";
    if (weakest && weakest !== strongest) {
      text += ` La característica con menor desempeño es ${weakest.label} (${weakest.value}/100) y la de mejor desempeño, ${strongest.label} (${strongest.value}/100).`;
    }
    return text;
  }, [reportResult, score, severityCounts, summary.quality_level, level.label, totalFindings, weakest, strongest]);

  const [activeSection, setActiveSection] = useState(SECTIONS[0].id);
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveSection(visible[0].target.id);
      },
      { rootMargin: "-80px 0px -60% 0px" }
    );
    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, [sections]);

  const goTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

  return (
    <div className="rv">
      {/* Portada */}
      <header className="rv-cover">
        <div className="rv-cover-top">
          <div>
            <span className="rv-eyebrow">Informe técnico · ISO/IEC 25010 · WCAG 2.2</span>
            <h1>Informe de evaluación de calidad frontend</h1>
            <p className="rv-cover-target">{sourceLabel}</p>
          </div>
          <div className="rv-cover-actions">
            <button type="button" className="rv-btn rv-btn-primary" onClick={onDownload} disabled={generatingPdf}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
              {generatingPdf ? "Generando PDF..." : "Descargar PDF"}
            </button>
          </div>
        </div>
        <dl className="rv-meta">
          <div><dt>Código de informe</dt><dd>{reportCode}</dd></div>
          <div><dt>Fecha de emisión</dt><dd>{dateLabel}</dd></div>
          <div><dt>Tipo de fuente</dt><dd>{inputType === "zip" ? "Proyecto comprimido (ZIP)" : "Sitio web (URL)"}</dd></div>
          <div><dt>Interfaces evaluadas</dt><dd>{summary.total_interfaces ?? 1}</dd></div>
          <div><dt>Alcance</dt><dd>{reportResult?.scope || "Frontend"}</dd></div>
        </dl>
      </header>

      <div className="rv-body">
        {/* Índice */}
        <nav className="rv-toc" aria-label="Contenido del informe">
          <span className="rv-toc-title">Contenido</span>
          <ol>
            {sections.map((s, i) => (
              <li key={s.id}>
                <button type="button" className={activeSection === s.id ? "active" : ""} onClick={() => goTo(s.id)}>
                  <span className="rv-toc-num">{i + 1}</span>{s.label}
                </button>
              </li>
            ))}
          </ol>
        </nav>

        <div className="rv-content">
          {/* 1. Resumen ejecutivo */}
          <section id="rv-resumen" className="rv-section">
            <h2><span className="rv-sec-num">1</span>Resumen ejecutivo</h2>
            <div className="rv-exec">
              <div className="rv-exec-score">
                <ScoreGauge score={score} />
                <span className="rv-level" style={{ background: level.color }}>
                  {summary.quality_level || level.label}
                </span>
                {decision?.category && (
                  <span className="rv-decision">
                    {decision.category} · {decision.score_10}/10
                  </span>
                )}
              </div>
              <div className="rv-exec-text">
                <h3>Dictamen</h3>
                <p>{conclusion}</p>
                {decision?.meaning && <p className="rv-muted">{decision.meaning}</p>}
                <div className="rv-highlights">
                  {weakest && (
                    <div className="rv-hl rv-hl-weak">
                      <span>Característica más débil</span>
                      <strong>{weakest.label}</strong>
                      <em>{weakest.value}/100</em>
                    </div>
                  )}
                  {strongest && (
                    <div className="rv-hl rv-hl-strong">
                      <span>Característica más sólida</span>
                      <strong>{strongest.label}</strong>
                      <em>{strongest.value}/100</em>
                    </div>
                  )}
                  {summary.worst_interface && summary.worst_interface !== "Ninguna" && (summary.total_interfaces ?? 1) > 1 && (
                    <div className="rv-hl">
                      <span>Interfaz con menor puntaje</span>
                      <strong title={summary.worst_interface}>{summary.worst_interface}</strong>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="rv-kpis">
              <div className="rv-kpi">
                <span className="rv-kpi-val">{totalFindings}</span>
                <span className="rv-kpi-lbl">Hallazgos totales</span>
              </div>
              {SEVERITIES.map((s) => (
                <div key={s.key} className={`rv-kpi rv-kpi-${s.cls}`}>
                  <span className="rv-kpi-val">{severityCounts[s.key]}</span>
                  <span className="rv-kpi-lbl">Severidad {s.key.toLowerCase()}</span>
                </div>
              ))}
            </div>
            {severityTotal > 0 && (
              <div className="rv-sevbar" aria-hidden="true">
                {SEVERITIES.map((s) =>
                  severityCounts[s.key] > 0 ? (
                    <div
                      key={s.key}
                      className={`rv-sevbar-seg rv-bg-${s.cls}`}
                      style={{ flexGrow: severityCounts[s.key] }}
                      title={`${s.key}: ${severityCounts[s.key]}`}
                    />
                  ) : null
                )}
              </div>
            )}
          </section>

          {/* 2. Características ISO/IEC 25010 */}
          <section id="rv-caracteristicas" className="rv-section">
            <h2><span className="rv-sec-num">2</span>Resultados por característica ISO/IEC 25010</h2>
            <p className="rv-lead">
              Puntaje de 0 a 100 de cada característica del modelo de calidad del producto. La escala de niveles es{" "}
              {QUALITY_LEVELS.map((l, i) => (
                <span key={l.label}>
                  <b style={{ color: l.color }}>{l.label}</b> ({l.range}){i < QUALITY_LEVELS.length - 1 ? ", " : "."}
                </span>
              ))}
            </p>
            <div className="rv-chars">
              <div className="rv-radar">
                {radarData.length >= 3 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarData} outerRadius="72%">
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis dataKey="name" tick={{ fill: "#475569", fontSize: 11 }} />
                      <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                      <Tooltip formatter={(v) => [`${v} / 100`, "Puntaje"]} labelFormatter={(_, p) => p?.[0]?.payload?.full || ""} />
                      <Radar dataKey="value" stroke="#1d4ed8" fill="#3b82f6" fillOpacity={0.22} strokeWidth={2} dot={{ r: 3, fill: "#1d4ed8" }} />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="rv-empty">No hay suficientes características medidas para el gráfico.</div>
                )}
              </div>
              <table className="rv-table rv-char-table">
                <thead>
                  <tr><th>Característica</th><th>Puntaje</th><th>Nivel</th></tr>
                </thead>
                <tbody>
                  {charRows.map((c) => {
                    const lv = getQualityLevel(c.value);
                    return (
                      <tr key={c.key}>
                        <td>{c.label}</td>
                        <td>
                          <div className="rv-bar">
                            <div className="rv-bar-track">
                              <div className="rv-bar-fill" style={{ width: `${c.value ?? 0}%`, background: lv.color }} />
                            </div>
                            <span>{c.value ?? "N/D"}</span>
                          </div>
                        </td>
                        <td><span className="rv-chip" style={{ color: lv.color, borderColor: lv.color }}>{lv.label}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* 3. Hallazgos */}
          <section id="rv-hallazgos" className="rv-section">
            <h2><span className="rv-sec-num">3</span>Hallazgos técnicos</h2>
            <p className="rv-lead">
              {totalFindings} hallazgos identificados. Filtre por severidad o característica y despliegue cada uno para ver su recomendación.
            </p>

            <div className="rv-filters">
              <div className="rv-filter-group" role="group" aria-label="Filtrar por severidad">
                {["Todas", ...SEVERITIES.map((s) => s.key)].map((s) => {
                  const count = s === "Todas" ? indexedFindings.length : indexedFindings.filter((f) => f._sev === s).length;
                  return (
                    <button
                      key={s}
                      type="button"
                      className={`rv-filter ${sevFilter === s ? "active" : ""}`}
                      aria-pressed={sevFilter === s}
                      onClick={() => setSevFilter(s)}
                    >
                      {s} <span>{count}</span>
                    </button>
                  );
                })}
              </div>
              {dimensions.length > 2 && (
                <label className="rv-select">
                  Característica
                  <select value={dimFilter} onChange={(e) => setDimFilter(e.target.value)}>
                    {dimensions.map((d) => <option key={d} value={d}>{d}</option>)}
                  </select>
                </label>
              )}
            </div>

            {visibleFindings.length === 0 ? (
              <div className="rv-empty">No hay hallazgos con los filtros seleccionados.</div>
            ) : (
              <ul className="rv-findings">
                {visibleFindings.map((f) => {
                  const sev = SEVERITIES.find((s) => s.key === f._sev);
                  const open = openId === f._id;
                  return (
                    <li key={f._id} className={`rv-finding rv-border-${sev.cls} ${open ? "open" : ""}`}>
                      <button type="button" className="rv-finding-head" aria-expanded={open} onClick={() => setOpenId(open ? null : f._id)}>
                        <span className="rv-finding-id">{f._id}</span>
                        <span className={`rv-sev rv-bg-soft-${sev.cls}`}>{f._sev}</span>
                        <span className="rv-finding-text">{splitExample(f.finding).text}</span>
                        <span className="rv-finding-dim">{f.dimension || "—"}</span>
                        <svg className="rv-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><polyline points="6 9 12 15 18 9" /></svg>
                      </button>
                      {open && (
                        <div className="rv-finding-body">
                          <dl>
                            <div><dt>Característica</dt><dd>{f.dimension || "No especificada"}</dd></div>
                            <div><dt>Subcaracterística</dt><dd>{f.subdimension || "No especificada"}</dd></div>
                            {f.interface && <div><dt>Interfaz</dt><dd>{f.interface}</dd></div>}
                          </dl>
                          <div className="rv-finding-detail">
                          {splitExample(f.finding).example && (
                            <div className="rv-evidence">
                              <span>Evidencia en el código</span>
                              <code>{splitExample(f.finding).example}</code>
                            </div>
                          )}
                          <div className="rv-reco">
                            <span>Recomendación</span>
                            <p>{f.recommendation || "No se registró recomendación."}</p>
                          </div>
                          </div>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          {/* 4. Plan de acción */}
          <section id="rv-recomendaciones" className="rv-section">
            <h2><span className="rv-sec-num">4</span>Plan de acción priorizado</h2>
            <p className="rv-lead">Recomendaciones ordenadas por la severidad más alta de los hallazgos que atienden.</p>
            {actionPlan.length === 0 ? (
              <div className="rv-empty">No se registraron recomendaciones.</div>
            ) : (
              <table className="rv-table rv-plan">
                <thead>
                  <tr><th>#</th><th>Prioridad</th><th>Acción recomendada</th><th>Características</th><th>Hallazgos</th></tr>
                </thead>
                <tbody>
                  {actionPlan.map((a, i) => {
                    const sev = SEVERITIES.find((s) => s.key === a.sev);
                    return (
                      <tr key={a.rec}>
                        <td className="rv-plan-num">{i + 1}</td>
                        <td><span className={`rv-sev rv-bg-soft-${sev.cls}`}>{a.sev}</span></td>
                        <td>{a.rec}</td>
                        <td className="rv-muted">{[...a.dims].join(", ") || "—"}</td>
                        <td className="rv-muted">{a.refs.join(", ")}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </section>

          {/* 5. Marco normativo */}
          {hasNormative && (
            <section id="rv-normativo" className="rv-section rv-section-flush">
              <h2><span className="rv-sec-num">5</span>Marco normativo y métricas</h2>
              <NormativeSection data={reportResult} />
            </section>
          )}

          <footer className="rv-footer">
            <p>
              Informe {reportCode} generado automáticamente por FrontMind AI. Los puntajes provienen de métricas
              automatizadas y deben complementarse con revisión experta en los criterios no automatizables.
            </p>
            <div className="rv-footer-actions">
              <button type="button" className="rv-btn" onClick={onBack}>Volver a la evaluación</button>
              <button type="button" className="rv-btn" onClick={onNew}>Nuevo análisis</button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
