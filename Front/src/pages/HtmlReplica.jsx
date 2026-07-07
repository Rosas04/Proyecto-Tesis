import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { replicateHtmlFromContent } from "../services/api";
import "./HtmlReplica.css";

const TYPE_COLORS = {
  html:     { bg: "#ecfdf5", color: "#047857", label: "HTML"     },
  jsx:      { bg: "#eff6ff", color: "#1d4ed8", label: "JSX"      },
  tsx:      { bg: "#f5f3ff", color: "#6d28d9", label: "TSX"      },
  ts:       { bg: "#fdf4ff", color: "#7e22ce", label: "TS"       },
  js:       { bg: "#fefce8", color: "#92400e", label: "JS"       },
  vue:      { bg: "#f0fdf4", color: "#15803d", label: "VUE"      },
  svelte:   { bg: "#fff7ed", color: "#c2410c", label: "SVELTE"   },
  astro:    { bg: "#faf5ff", color: "#7c3aed", label: "ASTRO"    },
  cshtml:   { bg: "#f0f9ff", color: "#0369a1", label: "CSHTML"   },
  razor:    { bg: "#f0f9ff", color: "#0369a1", label: "RAZOR"    },
  php:      { bg: "#f5f3ff", color: "#5b21b6", label: "PHP"      },
  blade:    { bg: "#fdf2f8", color: "#9d174d", label: "BLADE"    },
  erb:      { bg: "#fef2f2", color: "#991b1b", label: "ERB"      },
  hbs:      { bg: "#fff8f0", color: "#c2410c", label: "HBS"      },
  mustache: { bg: "#fff8f0", color: "#c2410c", label: "MUSTACHE" },
  ejs:      { bg: "#f0fdf4", color: "#166534", label: "EJS"      },
  pug:      { bg: "#f9fafb", color: "#374151", label: "PUG"      },
  jinja:    { bg: "#fefce8", color: "#854d0e", label: "JINJA"    },
  njk:      { bg: "#fefce8", color: "#854d0e", label: "NJK"      },
  twig:     { bg: "#f0fdf4", color: "#065f46", label: "TWIG"     },
  liquid:   { bg: "#eff6ff", color: "#1e40af", label: "LIQUID"   },
  combined: { bg: "#f1f5f9", color: "#334155", label: "FULL"     },
};

function TypeBadge({ type }) {
  const t = TYPE_COLORS[type] || TYPE_COLORS.combined;
  return (
    <span
      className="type-badge"
      style={{ background: t.bg, color: t.color }}
    >
      {t.label}
    </span>
  );
}

export default function HtmlReplica() {
  const navigate = useNavigate();

  const [captureResult, setCaptureResult] = useState(null);
  const [replicaResult, setReplicaResult] = useState(null);
  const [htmlPreview, setHtmlPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedIface, setSelectedIface] = useState(null);
  const [replicatedCache, setReplicatedCache] = useState({});

  const inputType = localStorage.getItem("inputType") || "url";
  const inputUrl = localStorage.getItem("inputUrl") || "";

  const isZip = captureResult?.source_type === "zip";
  const interfaces = useMemo(() => {
    if (!captureResult?.interfaces || !Array.isArray(captureResult.interfaces)) return [];
    return captureResult.interfaces;
  }, [captureResult]);

  useEffect(() => {
    const savedCapture = localStorage.getItem("captureResult");

    if (!savedCapture) {
      if (window.globalCaptureResult) {
        setCaptureResult(window.globalCaptureResult);
        return;
      }
      setError("No se encontró una captura previa. Vuelve al inicio.");
      return;
    }

    try {
      const parsedCapture = JSON.parse(savedCapture);
      setCaptureResult(parsedCapture);

      let initialIface = null;
      if (parsedCapture.interfaces && parsedCapture.interfaces.length > 0) {
        initialIface = parsedCapture.interfaces.find(
          (iface) => iface.html_content === parsedCapture.html_content
        ) || null;
      }
      setSelectedIface(initialIface);

      const cacheKey = initialIface ? initialIface.file_name : "combined";

      if (savedReplica) {
        const parsedReplica = JSON.parse(savedReplica);
        setReplicaResult(parsedReplica);

        const html =
          parsedReplica?.html_replication?.html_replicated ||
          parsedReplica?.html_replicated ||
          "";

        setHtmlPreview(html);
        setReplicatedCache({
          [cacheKey]: { result: parsedReplica, html }
        });
        return;
      }

      const targetHtmlContent = initialIface
        ? initialIface.html_content
        : parsedCapture.html_content || "";

      if (targetHtmlContent.trim()) {
        initialGenerate(targetHtmlContent, initialIface, parsedCapture);
      }
    } catch (err) {
      setError("No se pudo leer la información almacenada.");
      console.error(err);
    }
  }, []);

  const initialGenerate = async (htmlContent, iface, captureData) => {
    try {
      setLoading(true);
      setError("");

      const sourceUrl = iface
        ? iface.file_name
        : captureData?.url || inputUrl || "Interfaz evaluada por FrontMind AI";

      const cssCache = captureData?.css_cache || null;
      const cssomStyles = iface
        ? iface.cssom_styles
        : (captureData?.cssom_styles || null);

      const result = await replicateHtmlFromContent(htmlContent, sourceUrl, cssCache, cssomStyles);

      const replicatedHtml =
        result?.html_replication?.html_replicated ||
        result?.html_replicated ||
        "";

      setReplicaResult(result);
      setHtmlPreview(replicatedHtml);

      const cacheKey = iface ? iface.file_name : "combined";
      setReplicatedCache({
        [cacheKey]: { result, html: replicatedHtml }
      });
      localStorage.setItem("htmlReplicaResult", JSON.stringify(result));
    } catch (err) {
      setError("No se pudo generar la réplica HTML. Verifique que el backend esté encendido.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = async (iface) => {
    setSelectedIface(iface);
    setError("");

    const targetHtmlContent = iface
      ? iface.html_content
      : captureResult?.html_content || "";

    if (!targetHtmlContent.trim()) {
      setHtmlPreview("");
      setError("No existe contenido HTML para esta interfaz.");
      return;
    }

    const cacheKey = iface ? iface.file_name : "combined";
    if (replicatedCache[cacheKey]) {
      const cached = replicatedCache[cacheKey];
      setReplicaResult(cached.result);
      setHtmlPreview(cached.html);
      return;
    }

    try {
      setLoading(true);
      const sourceUrl = iface
        ? iface.file_name
        : captureResult?.url || inputUrl || "Interfaz evaluada por FrontMind AI";

      const cssCache = captureResult?.css_cache || null;
      const cssomStyles = iface
        ? iface.cssom_styles
        : (captureResult?.cssom_styles || null);

      const result = await replicateHtmlFromContent(targetHtmlContent, sourceUrl, cssCache, cssomStyles);

      const replicatedHtml =
        result?.html_replication?.html_replicated ||
        result?.html_replicated ||
        "";

      setReplicaResult(result);
      setHtmlPreview(replicatedHtml);

      setReplicatedCache(prev => ({
        ...prev,
        [cacheKey]: { result, html: replicatedHtml }
      }));
    } catch (err) {
      setError("No se pudo generar la réplica HTML para esta interfaz.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const combinedHtml = useMemo(() => {
    return captureResult?.extraction?.combined_html || captureResult?.html_content || "";
  }, [captureResult]);

  const combinedHtmlStats = useMemo(() => {
    const html = combinedHtml || "";

    return {
      characters: html.length,
      lines: html ? html.split("\n").length : 0,
      tags: html ? (html.match(/<[^/!][^>]*>/g) || []).length : 0,
      images: html ? (html.match(/<img/gi) || []).length : 0,
      links: html ? (html.match(/<a\s/gi) || []).length : 0,
      buttons: html ? (html.match(/<button/gi) || []).length : 0,
    };
  }, [combinedHtml]);

  const continueToEvaluation = () => {
    if (!htmlPreview.trim()) {
      setError("No existe HTML replicado para evaluar.");
      return;
    }

    try {
      localStorage.setItem("htmlToEvaluate", htmlPreview);
      navigate("/evaluation");
    } catch (e) {
      console.warn("localStorage quota exceeded, cleaning up older items...", e);
      // Clean up massive temporary items that are no longer strictly needed in evaluation
      localStorage.removeItem("zipResult");
      localStorage.removeItem("captureResult");
      localStorage.removeItem("htmlReplicaResult");
      try {
        localStorage.setItem("htmlToEvaluate", htmlPreview);
        navigate("/evaluation");
      } catch (retryError) {
        setError("El archivo HTML es demasiado grande para guardarse en el almacenamiento de su navegador. Pruebe reduciendo el tamaño del archivo o limpiando la caché.");
        console.error("Fallo definitivo al guardar en localStorage:", retryError);
      }
    }
  };

  const goBack = () => {
    navigate("/capture");
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="html-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Réplica de Código</p>
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
                <strong>{combinedHtmlStats.characters}</strong>
              </div>

              <div>
                <span>Etiquetas</span>
                <strong>{combinedHtmlStats.tags}</strong>
              </div>
            </section>

            <section className="html-stats-grid">
              <article className="html-stat card">
                <span>Líneas</span>
                <strong>{combinedHtmlStats.lines}</strong>
              </article>

              <article className="html-stat card">
                <span>Imágenes</span>
                <strong>{combinedHtmlStats.images}</strong>
              </article>

              <article className="html-stat card">
                <span>Enlaces</span>
                <strong>{combinedHtmlStats.links}</strong>
              </article>

              <article className="html-stat card">
                <span>Botones</span>
                <strong>{combinedHtmlStats.buttons}</strong>
              </article>
            </section>

            {/* ── Interface Tabs ───────────────── */}
            {interfaces.length > 0 && (
              <nav className="tabs-navigation">
                <button
                  type="button"
                  className={`tab-btn ${!selectedIface ? "tab-btn--active" : ""}`}
                  onClick={() => handleTabChange(null)}
                >
                  <TypeBadge type="combined" />
                  <span>Paquete completo</span>
                </button>

                {interfaces.map((iface, i) => (
                  <button
                    key={i}
                    type="button"
                    className={`tab-btn ${selectedIface?.file_name === iface.file_name ? "tab-btn--active" : ""}`}
                    onClick={() => handleTabChange(iface)}
                  >
                    <TypeBadge type={iface.type} />
                    <span>{iface.file_name}</span>
                  </button>
                ))}
              </nav>
            )}

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
                      sandbox="allow-same-origin allow-scripts"
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