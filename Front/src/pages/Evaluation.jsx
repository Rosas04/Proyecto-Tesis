import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { evaluateHtml } from "../services/api";
import "./Evaluation.css";

export default function Evaluation() {
  const navigate = useNavigate();

  const [evaluationResult, setEvaluationResult] = useState(null);
  const [htmlToEvaluate, setHtmlToEvaluate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedEvaluation = localStorage.getItem("isoEvaluation");
    const savedHtml = localStorage.getItem("htmlToEvaluate");

    if (!savedHtml) {
      setError("No se encontró HTML para evaluar. Regrese a la réplica HTML.");
      return;
    }

    setHtmlToEvaluate(savedHtml);

    if (savedEvaluation) {
      try {
        setEvaluationResult(JSON.parse(savedEvaluation));
        return;
      } catch (err) {
        console.error(err);
      }
    }

    runEvaluation(savedHtml);
  }, []);

  const runEvaluation = async (html) => {
    try {
      setLoading(true);
      setError("");

      const result = await evaluateHtml(html);

      setEvaluationResult(result);
      localStorage.setItem("isoEvaluation", JSON.stringify(result));
    } catch (err) {
      setError(
        "No se pudo ejecutar la evaluación ISO/IEC 25010. Verifique que el backend esté encendido."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const evaluation = useMemo(() => {
    return evaluationResult?.evaluation || evaluationResult || {};
  }, [evaluationResult]);

  const scores = useMemo(() => {
    return evaluation?.scores || {};
  }, [evaluation]);

  const findings = useMemo(() => {
    if (!evaluation?.findings || !Array.isArray(evaluation.findings)) {
      return [];
    }

    return evaluation.findings;
  }, [evaluation]);

  const globalScore = evaluation?.global_score ?? 0;
  const qualityLevel = evaluation?.quality_level || "No calculado";
  const totalFindings = evaluation?.total_findings ?? findings.length;

  const scoreItems = [
    {
      label: "Adecuación funcional",
      key: "adecuacion_funcional",
      value: scores.adecuacion_funcional ?? 0,
    },
    {
      label: "Eficiencia de desempeño",
      key: "eficiencia_desempeno",
      value: scores.eficiencia_desempeno ?? 0,
    },
    {
      label: "Usabilidad",
      key: "usabilidad",
      value: scores.usabilidad ?? 0,
    },
    {
      label: "Accesibilidad",
      key: "accesibilidad",
      value: scores.accesibilidad ?? 0,
    },
    {
      label: "Mantenibilidad",
      key: "mantenibilidad",
      value: scores.mantenibilidad ?? 0,
    },
    {
      label: "Compatibilidad",
      key: "compatibilidad",
      value: scores.compatibilidad ?? 0,
    },
    {
      label: "Seguridad",
      key: "seguridad",
      value: scores.seguridad ?? 0,
    },
    {
      label: "Portabilidad",
      key: "portabilidad",
      value: scores.portabilidad ?? 0,
    },
  ];

  const severityCount = useMemo(() => {
    const result = {
      Alta: 0,
      Media: 0,
      Baja: 0,
      Crítica: 0,
    };

    findings.forEach((item) => {
      const severity = item.severity || "Media";

      if (result[severity] === undefined) {
        result[severity] = 0;
      }

      result[severity] += 1;
    });

    return result;
  }, [findings]);

  const getScoreClass = (score) => {
    if (score >= 90) return "excellent";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    if (score >= 40) return "low";
    return "critical";
  };

  const getSeverityClass = (severity) => {
    if (severity === "Crítica") return "critical";
    if (severity === "Alta") return "high";
    if (severity === "Media") return "medium";
    return "low";
  };

  const goBack = () => {
    navigate("/html");
  };

  const continueToReport = () => {
    if (!evaluationResult) {
      setError("No existe una evaluación para generar el reporte.");
      return;
    }

    navigate("/report");
  };

  const reevaluate = () => {
    localStorage.removeItem("isoEvaluation");
    runEvaluation(htmlToEvaluate);
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="evaluation-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Evaluación ISO/IEC 25010</p>
          <h1 className="page-title">Diagnóstico técnico de calidad frontend</h1>
          <p className="page-description">
            El agente crítico analiza el HTML evaluable y calcula puntajes de
            calidad por dimensión, hallazgos técnicos, severidades y
            recomendaciones según criterios de ISO/IEC 25010 y accesibilidad web.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Ejecutando reglas de evaluación ISO/IEC 25010. Espere unos
            segundos...
          </div>
        )}

        {!loading && evaluationResult && (
          <>
            <section className="evaluation-hero card">
              <div className="score-circle-wrapper">
                <div className={`score-circle ${getScoreClass(globalScore)}`}>
                  <strong>{globalScore}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div className="evaluation-hero-content">
                <span className="result-label">Puntaje global</span>
                <h2>{qualityLevel}</h2>
                <p>
                  El puntaje global representa el nivel de calidad técnica de la
                  interfaz frontend evaluada, considerando eficiencia,
                  usabilidad, accesibilidad, mantenibilidad, compatibilidad,
                  seguridad y portabilidad.
                </p>
              </div>

              <div className="findings-total">
                <span>Total de hallazgos</span>
                <strong>{totalFindings}</strong>
              </div>
            </section>

            <section className="severity-grid">
              <article className="severity-card card critical">
                <span>Críticas</span>
                <strong>{severityCount.Crítica || 0}</strong>
              </article>

              <article className="severity-card card high">
                <span>Altas</span>
                <strong>{severityCount.Alta || 0}</strong>
              </article>

              <article className="severity-card card medium">
                <span>Medias</span>
                <strong>{severityCount.Media || 0}</strong>
              </article>

              <article className="severity-card card low">
                <span>Bajas</span>
                <strong>{severityCount.Baja || 0}</strong>
              </article>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Puntajes por dimensión ISO/IEC 25010</h2>
                <p>
                  Cada dimensión se calcula sobre una escala de 0 a 100,
                  aplicando penalizaciones por deficiencias detectadas.
                </p>
              </div>

              <div className="score-list">
                {scoreItems.map((item) => (
                  <div className="score-row" key={item.key}>
                    <div className="score-row-label">
                      <strong>{item.label}</strong>
                      <span>{item.value}/100</span>
                    </div>

                    <div className="score-bar">
                      <div
                        className="score-bar-fill"
                        style={{ width: `${item.value}%`, background: "#000000" }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="findings-section card">
              <div className="section-header">
                <h2>Hallazgos técnicos detectados</h2>
                <p>
                  Los hallazgos se clasifican por dimensión, subdimensión y
                  severidad para orientar la toma de decisiones técnicas.
                </p>
              </div>

              {findings.length > 0 ? (
                <div className="findings-table-wrapper">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>N°</th>
                        <th>Dimensión</th>
                        <th>Subdimensión</th>
                        <th>Severidad</th>
                        <th>Hallazgo</th>
                        <th>Recomendación</th>
                      </tr>
                    </thead>

                    <tbody>
                      {findings.map((item, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{item.dimension || "No especificada"}</td>
                          <td>{item.subdimension || "No especificada"}</td>
                          <td>
                            <span
                              className={`severity-pill ${getSeverityClass(
                                item.severity
                              )}`}
                            >
                              {item.severity || "Media"}
                            </span>
                          </td>
                          <td>{item.finding || "Hallazgo no especificado."}</td>
                          <td>
                            {item.recommendation ||
                              "No se registró recomendación."}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="success-box">
                  No se detectaron hallazgos técnicos relevantes.
                </div>
              )}
            </section>

            {evaluation?.engineering_tips?.length > 0 && (
              <section className="tips-section card">
                <div className="section-header">
                  <h2>Recomendaciones de ingeniería</h2>
                  <p>
                    Sugerencias generales para mejorar la calidad frontend del
                    artefacto evaluado.
                  </p>
                </div>

                <ul>
                  {evaluation.engineering_tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </section>
            )}

            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button className="secondary-btn" type="button" onClick={reevaluate}>
                Reevaluar
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToReport}
              >
                Generar reporte
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}