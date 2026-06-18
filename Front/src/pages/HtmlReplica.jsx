import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { replicateHtmlFromContent } from "../services/api";
import "./HtmlReplica.css";

export default function HtmlReplica() {
  const navigate = useNavigate();

  const [captureResult, setCaptureResult] = useState(null);
  const [replicaResult, setReplicaResult] = useState(null);
  const [htmlPreview, setHtmlPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const inputType = localStorage.getItem("inputType") || "url";
  const inputUrl = localStorage.getItem("inputUrl") || "";

  useEffect(() => {
    const savedCapture = localStorage.getItem("captureResult");
    const savedReplica = localStorage.getItem("htmlReplicaResult");

    if (!savedCapture) {
      setError("No se encontró contenido capturado. Inicie un nuevo análisis.");
      return;
    }

    try {
      const parsedCapture = JSON.parse(savedCapture);
      setCaptureResult(parsedCapture);

      if (savedReplica) {
        const parsedReplica = JSON.parse(savedReplica);
        setReplicaResult(parsedReplica);

        const html =
          parsedReplica?.html_replication?.html_replicated ||
          parsedReplica?.html_replicated ||
          "";

        setHtmlPreview(html);
        return;
      }

      generateReplica(parsedCapture);
    } catch (err) {
      setError("No se pudo leer la información almacenada.");
      console.error(err);
    }
  }, []);

  const generateReplica = async (captureData) => {
    try {
      setLoading(true);
      setError("");

      const htmlContent = captureData?.html_content || "";

      if (!htmlContent.trim()) {
        setError("No existe contenido HTML para generar la réplica.");
        return;
      }

      const sourceUrl =
        captureData?.url ||
        inputUrl ||
        "Interfaz evaluada por FrontMind AI";

      const result = await replicateHtmlFromContent(htmlContent, sourceUrl);

      const replicatedHtml =
        result?.html_replication?.html_replicated ||
        result?.html_replicated ||
        "";

      setReplicaResult(result);
      setHtmlPreview(replicatedHtml);

      localStorage.setItem("htmlReplicaResult", JSON.stringify(result));
    } catch (err) {
      setError(
        "No se pudo generar la réplica HTML. Verifique que el backend esté encendido."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const htmlStats = useMemo(() => {
    const html = htmlPreview || "";

    return {
      characters: html.length,
      lines: html ? html.split("\n").length : 0,
      tags: html ? (html.match(/<[^/!][^>]*>/g) || []).length : 0,
      images: html ? (html.match(/<img/gi) || []).length : 0,
      links: html ? (html.match(/<a\s/gi) || []).length : 0,
      buttons: html ? (html.match(/<button/gi) || []).length : 0,
    };
  }, [htmlPreview]);

  const continueToEvaluation = () => {
    if (!htmlPreview.trim()) {
      setError("No existe HTML replicado para evaluar.");
      return;
    }

    localStorage.setItem("htmlToEvaluate", htmlPreview);
    navigate("/evaluation");
  };

  const goBack = () => {
    navigate("/capture");
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="html-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Réplica HTML</p>
          <h1 className="page-title">HTML real o replicado</h1>
          <p className="page-description">
            En esta etapa, el framework reconstruye una versión evaluable del
            artefacto frontend, incorporando estructura HTML, estilos y recursos
            necesarios para su posterior evaluación técnica bajo ISO/IEC 25010.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Generando réplica HTML evaluable. Espere unos segundos...
          </div>
        )}

        {!loading && captureResult && (
          <>
            <section className="html-summary card">
              <div>
                <span>Fuente</span>
                <strong>{captureResult.url || inputUrl || "No especificada"}</strong>
              </div>

              <div>
                <span>Tipo</span>
                <strong>{inputType.toUpperCase()}</strong>
              </div>

              <div>
                <span>Caracteres</span>
                <strong>{htmlStats.characters}</strong>
              </div>

              <div>
                <span>Etiquetas</span>
                <strong>{htmlStats.tags}</strong>
              </div>
            </section>

            <section className="html-stats-grid">
              <article className="html-stat card">
                <span>Líneas</span>
                <strong>{htmlStats.lines}</strong>
              </article>

              <article className="html-stat card">
                <span>Imágenes</span>
                <strong>{htmlStats.images}</strong>
              </article>

              <article className="html-stat card">
                <span>Enlaces</span>
                <strong>{htmlStats.links}</strong>
              </article>

              <article className="html-stat card">
                <span>Botones</span>
                <strong>{htmlStats.buttons}</strong>
              </article>
            </section>

            <section className="html-workspace">
              <article className="html-code-panel card">
                <div className="panel-header">
                  <div>
                    <h2>Código HTML evaluable</h2>
                    <p>
                      Contenido generado por el Agente de Réplica para ser
                      analizado por el Agente ISO/IEC 25010.
                    </p>
                  </div>
                </div>

                <textarea
                  className="html-code"
                  value={htmlPreview}
                  onChange={(event) => setHtmlPreview(event.target.value)}
                  spellCheck="false"
                />
              </article>

              <article className="html-preview-panel card">
                <div className="panel-header">
                  <div>
                    <h2>Vista previa</h2>
                    <p>
                      Renderización aproximada del HTML replicado para validar
                      su estructura visual.
                    </p>
                  </div>
                </div>

                <div className="preview-frame-wrapper">
                  {htmlPreview ? (
                    <iframe
                      title="Vista previa HTML"
                      className="preview-frame"
                      srcDoc={htmlPreview}
                      sandbox="allow-same-origin"
                    />
                  ) : (
                    <div className="empty-preview">
                      No existe HTML para mostrar.
                    </div>
                  )}
                </div>
              </article>
            </section>

            {replicaResult && (
              <section className="replica-info card">
                <h2>Resultado del agente</h2>
                <p>
                  {replicaResult?.html_replication?.source ||
                    replicaResult?.source ||
                    "HTML replicado correctamente."}
                </p>
              </section>
            )}

            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToEvaluation}
                disabled={!htmlPreview.trim()}
              >
                Evaluar con ISO/IEC 25010
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}