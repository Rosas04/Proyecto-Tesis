import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import Sidebar from "../components/Sidebar";
import { generateReport } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { addAnalysisRun } from "../historyService";
import "./Report.css";

export default function Report() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [reportResult, setReportResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [generatingPdf, setGeneratingPdf] = useState(false);
  
  const hasCalled = useRef(false);

  const inputUrl = localStorage.getItem("inputUrl") || "";
  const inputZip = localStorage.getItem("inputZip") || "";
  const inputType = localStorage.getItem("inputType") || "url";

  useEffect(() => {
    const savedReport = localStorage.getItem("technicalReport");
    const savedEvaluation = localStorage.getItem("isoEvaluation");

    if (savedReport) {
      try {
        setReportResult(JSON.parse(savedReport));
        return;
      } catch (err) {
        console.error(err);
      }
    }

    if (!savedEvaluation) {
      setError(
        "No se encontró una evaluación previa. Regrese a la etapa de evaluación ISO/IEC 25010."
      );
      return;
    }

    if (hasCalled.current) return;
    hasCalled.current = true;

    try {
      const parsedEvaluation = JSON.parse(savedEvaluation);
      const evaluation = parsedEvaluation?.evaluation || parsedEvaluation;
      generateTechnicalReport(evaluation);
    } catch (err) {
      setError("No se pudo leer la evaluación almacenada.");
      console.error(err);
    }
  }, []);

  const generateTechnicalReport = async (evaluation) => {
    try {
      setLoading(true);
      setError("");

      const userId = user?.id || null;
      const result = await generateReport(evaluation, userId);

      setReportResult(result);
      localStorage.setItem("technicalReport", JSON.stringify(result));

      // Guardar el análisis en la base de datos si el usuario está autenticado
      if (user && user.id) {
        try {
          const evalData = evaluation || {};
          const findings = evalData.findings || [];
          const localSourceType = localStorage.getItem("inputType") || "url";
          
          // Generar hash simple del HTML evaluado para identificar esta ejecución
          const generateSimpleHash = (str) => {
            let hash = 0;
            if (!str) return hash.toString();
            for (let i = 0; i < str.length; i++) {
              hash = (hash << 5) - hash + str.charCodeAt(i);
              hash |= 0;
            }
            return Math.abs(hash).toString(16);
          };
          
          const savedHtml = localStorage.getItem("htmlToEvaluate") || "";
          const localInputHash = savedHtml ? generateSimpleHash(savedHtml) : `hash_${Date.now()}`;

          // Calcular el nombre del proyecto real basado en la URL o archivo ZIP
          const localInputUrl = localStorage.getItem("inputUrl") || "";
          const localInputZip = localStorage.getItem("inputZip") || "";
          let localProjectName = "Proyecto URL";

          if (localSourceType === "zip") {
            localProjectName = localInputZip || "Proyecto ZIP";
          } else if (localInputUrl) {
            try {
              let formattedUrl = localInputUrl.trim();
              if (!/^https?:\/\//i.test(formattedUrl)) {
                formattedUrl = "http://" + formattedUrl;
              }
              const urlObj = new URL(formattedUrl);
              let hostname = urlObj.hostname;
              if (hostname.startsWith("www.")) {
                hostname = hostname.substring(4);
              }
              localProjectName = hostname || localInputUrl;
            } catch (e) {
              console.error("Error al extraer el dominio de la URL:", e);
              localProjectName = localInputUrl;
            }
          }

          await addAnalysisRun({
            userId: user.id,
            globalScore: evalData.global_score ?? 0,
            qualityLevel: evalData.quality_level || "No calculado",
            totalFindings: evalData.total_findings ?? findings.length,
            findings: findings,
            sourceType: localSourceType,
            inputHash: localInputHash,
            projectName: localProjectName,
          });
          console.log("Análisis guardado en historial de Supabase exitosamente.");
        } catch (dbErr) {
          console.error("Error al persistir el análisis en Supabase:", dbErr);
        }
      }
    } catch (err) {
      setError(
        "No se pudo generar el reporte técnico. Verifique que el backend esté encendido."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const summary = useMemo(() => reportResult?.summary || {}, [reportResult]);
  const scores = useMemo(() => reportResult?.scores || {}, [reportResult]);
  const findings = useMemo(
    () => (Array.isArray(reportResult?.findings) ? reportResult.findings : []),
    [reportResult]
  );
  const recommendations = useMemo(
    () =>
      Array.isArray(reportResult?.main_recommendations)
        ? reportResult.main_recommendations
        : [],
    [reportResult]
  );

  const sourceLabel =
    inputType === "zip"
      ? inputZip || "Proyecto ZIP"
      : inputUrl || "No especificada";

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

  const getScoreClass = (score) => {
    if (score >= 90) return "excellent";
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    if (score >= 40) return "low";
    return "critical";
  };

  const goBack = () => {
    navigate("/evaluation");
  };

  const startNewAnalysis = () => {
    localStorage.removeItem("inputType");
    localStorage.removeItem("inputUrl");
    localStorage.removeItem("inputZip");
    localStorage.removeItem("captureResult");
    localStorage.removeItem("zipResult");
    localStorage.removeItem("htmlReplicaResult");
    localStorage.removeItem("htmlToEvaluate");
    localStorage.removeItem("isoEvaluation");
    localStorage.removeItem("technicalReport");
    navigate("/input");
  };

  const downloadPdf = () => {
    if (!reportResult) {
      return;
    }

    try {
      setGeneratingPdf(true);

      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const pageWidth = doc.internal.pageSize.getWidth();
      const marginX = 40;
      let cursorY = 50;

      doc.setFillColor(37, 99, 235);
      doc.rect(0, 0, pageWidth, 70, "F");

      doc.setTextColor(255, 255, 255);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text("FrontMind AI - Reporte técnico de evaluación frontend", marginX, 35);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text("Norma aplicada: ISO/IEC 25010", marginX, 52);

      cursorY = 95;
      doc.setTextColor(17, 24, 39);

      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text("Información general", marginX, cursorY);
      cursorY += 18;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);

      const generalInfo = [
        ["Fuente evaluada", sourceLabel],
        ["Tipo de entrada", inputType.toUpperCase()],
        ["Fecha de generación", reportResult.generated_at || "No especificada"],
        ["Puntaje global", `${summary.global_score ?? 0} / 100`],
        ["Nivel de calidad", summary.quality_level || "No calculado"],
        ["Total de hallazgos", `${summary.total_findings ?? findings.length}`],
      ];

      generalInfo.forEach(([label, value]) => {
        doc.setFont("helvetica", "bold");
        doc.text(`${label}:`, marginX, cursorY);
        doc.setFont("helvetica", "normal");
        doc.text(String(value), marginX + 150, cursorY);
        cursorY += 16;
      });

      cursorY += 8;

      const scoreRows = Object.entries(scoreLabels).map(([key, label]) => [
        label,
        `${scores[key] ?? 0} / 100`,
      ]);

      autoTable(doc, {
        startY: cursorY,
        margin: { left: marginX, right: marginX },
        head: [["Dimensión ISO/IEC 25010", "Puntaje"]],
        body: scoreRows,
        theme: "grid",
        headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: "bold" },
        styles: { fontSize: 9, cellPadding: 6 },
      });

      cursorY = doc.lastAutoTable.finalY + 24;

      if (cursorY > 680) {
        doc.addPage();
        cursorY = 50;
      }

      doc.setFont("helvetica", "bold");
      doc.setFontSize(12);
      doc.text("Conclusión técnica", marginX, cursorY);
      cursorY += 16;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);

      const conclusionText = reportResult.technical_conclusion || "Sin conclusión disponible.";
      const splitConclusion = doc.splitTextToSize(conclusionText, pageWidth - marginX * 2);
      doc.text(splitConclusion, marginX, cursorY);
      cursorY += splitConclusion.length * 13 + 16;

      if (findings.length > 0) {
        if (cursorY > 650) {
          doc.addPage();
          cursorY = 50;
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.text("Hallazgos técnicos detectados", marginX, cursorY);
        cursorY += 12;

        const findingsRows = findings.map((item, index) => [
          String(index + 1),
          item.dimension || "No especificada",
          item.severity || "Media",
          item.finding || "Hallazgo no especificado.",
          item.recommendation || "Sin recomendación registrada.",
        ]);

        autoTable(doc, {
          startY: cursorY + 8,
          margin: { left: marginX, right: marginX },
          head: [["N°", "Dimensión", "Severidad", "Hallazgo", "Recomendación"]],
          body: findingsRows,
          theme: "striped",
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: "bold" },
          styles: { fontSize: 8, cellPadding: 5 },
          columnStyles: {
            0: { cellWidth: 22 },
            1: { cellWidth: 75 },
            2: { cellWidth: 55 },
            3: { cellWidth: 160 },
            4: { cellWidth: 160 },
          },
        });

        cursorY = doc.lastAutoTable.finalY + 24;
      }

      if (recommendations.length > 0) {
        if (cursorY > 650) {
          doc.addPage();
          cursorY = 50;
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.text("Recomendaciones principales", marginX, cursorY);
        cursorY += 16;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);

        recommendations.forEach((tip) => {
          if (cursorY > 760) {
            doc.addPage();
            cursorY = 50;
          }

          const splitTip = doc.splitTextToSize(`• ${tip}`, pageWidth - marginX * 2);
          doc.text(splitTip, marginX, cursorY);
          cursorY += splitTip.length * 13 + 6;
        });
      }

      const totalPages = doc.internal.getNumberOfPages();

      for (let page = 1; page <= totalPages; page += 1) {
        doc.setPage(page);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(107, 114, 128);
        doc.text(
          `FrontMind AI · Evaluación técnica frontend ISO/IEC 25010 · Página ${page} de ${totalPages}`,
          marginX,
          820
        );
      }

      const fileSafeSource = sourceLabel
        .replace(/^https?:\/\//, "")
        .replace(/[^a-zA-Z0-9]/g, "_")
        .slice(0, 40);

      doc.save(`reporte-frontmind-${fileSafeSource || "evaluacion"}.pdf`);
    } catch (err) {
      setError("No se pudo generar el archivo PDF del reporte.");
      console.error(err);
    } finally {
      setGeneratingPdf(false);
    }
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="report-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Reporte</p>
          <h1 className="page-title">Reporte técnico final</h1>
          <p className="page-description">
            En esta etapa, el framework consolida los resultados de la
            evaluación ISO/IEC 25010 en un informe técnico profesional, listo
            para descarga y presentación.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Generando reporte técnico consolidado. Espere unos segundos...
          </div>
        )}

        {!loading && reportResult && (
          <>
            <section className="report-hero card">
              <div className="score-circle-wrapper">
                <div
                  className={`score-circle ${getScoreClass(
                    summary.global_score ?? 0
                  )}`}
                >
                  <strong>{summary.global_score ?? 0}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div className="report-hero-content">
                <span className="result-label">Nivel de calidad</span>
                <h2>{summary.quality_level || "No calculado"}</h2>
                <p>{reportResult.technical_conclusion}</p>
              </div>
            </section>

            <section className="report-summary card">
              <div>
                <span className="summary-label">Fuente evaluada</span>
                <strong>{sourceLabel}</strong>
              </div>

              <div>
                <span className="summary-label">Tipo de entrada</span>
                <strong>{inputType.toUpperCase()}</strong>
              </div>

              <div>
                <span className="summary-label">Generado el</span>
                <strong>{reportResult.generated_at || "No especificado"}</strong>
              </div>

              <div>
                <span className="summary-label">Total de hallazgos</span>
                <strong>{summary.total_findings ?? findings.length}</strong>
              </div>
            </section>

            <section className="severity-grid">
              <article className="severity-card card critical">
                <span>Críticas</span>
                <strong>{summary.severity_summary?.["Crítica"] || 0}</strong>
              </article>

              <article className="severity-card card high">
                <span>Altas</span>
                <strong>{summary.severity_summary?.Alta || 0}</strong>
              </article>

              <article className="severity-card card medium">
                <span>Medias</span>
                <strong>{summary.severity_summary?.Media || 0}</strong>
              </article>

              <article className="severity-card card low">
                <span>Bajas</span>
                <strong>{summary.severity_summary?.Baja || 0}</strong>
              </article>
            </section>

            <section className="scores-section card">
              <div className="section-header">
                <h2>Puntajes finales por dimensión</h2>
                <p>
                  Resultados consolidados de la evaluación técnica ISO/IEC
                  25010 aplicada al artefacto frontend.
                </p>
              </div>

              <div className="score-list">
                {Object.entries(scoreLabels).map(([key, label]) => (
                  <div className="score-row" key={key}>
                    <div className="score-row-label">
                      <strong>{label}</strong>
                      <span>{scores[key] ?? 0}/100</span>
                    </div>

                    <div className="score-bar">
                      <div
                        className={`score-bar-fill ${getScoreClass(
                          scores[key] ?? 0
                        )}`}
                        style={{ width: `${scores[key] ?? 0}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {recommendations.length > 0 && (
              <section className="recommendations-section card">
                <div className="section-header">
                  <h2>Recomendaciones principales</h2>
                  <p>
                    Listado priorizado de mejoras técnicas a implementar en el
                    frontend evaluado.
                  </p>
                </div>

                <ul>
                  {recommendations.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </section>
            )}

            <section className="findings-section card">
              <div className="section-header">
                <h2>Detalle de hallazgos técnicos</h2>
                <p>
                  Hallazgos clasificados por dimensión y severidad según
                  ISO/IEC 25010.
                </p>
              </div>

              {findings.length > 0 ? (
                <div className="findings-table-wrapper">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>N°</th>
                        <th>Dimensión</th>
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
                          <td>{item.severity || "Media"}</td>
                          <td>
                            {item.finding?.replace(/\[.*?\]\s*/g, '') || "Hallazgo no especificado."}
                          </td>
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

            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button
                className="secondary-btn"
                type="button"
                onClick={startNewAnalysis}
              >
                Nuevo análisis
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={downloadPdf}
                disabled={generatingPdf}
              >
                {generatingPdf ? "Generando PDF..." : "Descargar reporte PDF"}
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}