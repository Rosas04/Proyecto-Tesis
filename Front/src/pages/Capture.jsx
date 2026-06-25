import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_URL } from "../services/api";
import "./Capture.css";

const TYPE_COLORS = {
  // Core
  html:     { bg: "#ecfdf5", color: "#047857", label: "HTML"     },
  jsx:      { bg: "#eff6ff", color: "#1d4ed8", label: "JSX"      },
  tsx:      { bg: "#f5f3ff", color: "#6d28d9", label: "TSX"      },
  ts:       { bg: "#fdf4ff", color: "#7e22ce", label: "TS"       },
  js:       { bg: "#fefce8", color: "#92400e", label: "JS"       },
  // Vue / Svelte / Astro
  vue:      { bg: "#f0fdf4", color: "#15803d", label: "VUE"      },
  svelte:   { bg: "#fff7ed", color: "#c2410c", label: "SVELTE"   },
  astro:    { bg: "#faf5ff", color: "#7c3aed", label: "ASTRO"    },
  // .NET
  cshtml:   { bg: "#f0f9ff", color: "#0369a1", label: "CSHTML"   },
  razor:    { bg: "#f0f9ff", color: "#0369a1", label: "RAZOR"    },
  // PHP ecosystem
  php:      { bg: "#f5f3ff", color: "#5b21b6", label: "PHP"      },
  blade:    { bg: "#fdf2f8", color: "#9d174d", label: "BLADE"    },
  // Ruby
  erb:      { bg: "#fef2f2", color: "#991b1b", label: "ERB"      },
  // Template engines
  hbs:      { bg: "#fff8f0", color: "#c2410c", label: "HBS"      },
  mustache: { bg: "#fff8f0", color: "#c2410c", label: "MUSTACHE" },
  ejs:      { bg: "#f0fdf4", color: "#166534", label: "EJS"      },
  pug:      { bg: "#f9fafb", color: "#374151", label: "PUG"      },
  jinja:    { bg: "#fefce8", color: "#854d0e", label: "JINJA"    },
  njk:      { bg: "#fefce8", color: "#854d0e", label: "NJK"      },
  twig:     { bg: "#f0fdf4", color: "#065f46", label: "TWIG"     },
  liquid:   { bg: "#eff6ff", color: "#1e40af", label: "LIQUID"   },
  // Combined / fallback
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

export default function Capture() {
  const navigate = useNavigate();

  const [captureResult, setCaptureResult] = useState(null);
  const [error, setError]                 = useState("");
  const [selectedIface, setSelectedIface] = useState(null); // null = combined

  useEffect(() => {
    const savedCapture = localStorage.getItem("captureResult");

    if (!savedCapture) {
      setError("No se encontró una captura previa. Inicie un nuevo análisis.");
      return;
    }

    try {
      setCaptureResult(JSON.parse(savedCapture));
    } catch (err) {
      setError("La información de captura almacenada no es válida.");
      console.error(err);
    }
  }, []);

  const captures = useMemo(() => {
    if (selectedIface && Array.isArray(selectedIface.captures)) {
      return selectedIface.captures;
    }
    if (!captureResult?.captures || !Array.isArray(captureResult.captures)) return [];
    return captureResult.captures;
  }, [captureResult, selectedIface]);

  const interfaces = useMemo(() => {
    if (!captureResult?.interfaces || !Array.isArray(captureResult.interfaces)) return [];
    return captureResult.interfaces;
  }, [captureResult]);

  const isZip      = captureResult?.source_type === "zip";
  const inputType  = localStorage.getItem("inputType") || "url";

  // The HTML that will be forwarded to HtmlReplica
  const activeHtml = selectedIface
    ? selectedIface.html_content
    : captureResult?.html_content || "";

  const continueToHtml = () => {
    if (activeHtml) {
      // Update captureResult with whichever html the user selected
      const updated = { ...captureResult, html_content: activeHtml };
      localStorage.setItem("captureResult", JSON.stringify(updated));
      localStorage.removeItem("htmlReplicaResult");
      localStorage.removeItem("isoEvaluation");
      localStorage.removeItem("technicalReport");
    }
    navigate("/html");
  };

  const goBack = () => navigate("/input");

  const getDeviceLabel = (device) => {
    if (device === "desktop") return "Desktop";
    if (device === "tablet")  return "Tablet";
    if (device === "mobile")  return "Mobile";
    return "Vista";
  };

  const getImageSource = (item) => {
    if (item.public_url) {
      return item.public_url.replace(/http:\/\/127\.0\.0\.1:\d+/, API_URL);
    }
    if (item.file_name) return `${API_URL}/captures/${item.file_name}`;
    return "";
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="capture-main">
        <section className="page-header">
          <p className="page-kicker">Agente de Captura</p>
          <h1 className="page-title">Evidencia visual y estructural</h1>
          <p className="page-description">
            El framework registra la fuente de análisis y muestra las capturas
            generadas en diferentes resoluciones. Estas evidencias servirán para
            la réplica HTML y la evaluación ISO/IEC 25010.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {!error && captureResult && (
          <>
            {/* ── Interface Tabs ───────────────── */}
            {interfaces.length > 0 && (
              <nav className="tabs-navigation">
                <button
                  type="button"
                  className={`tab-btn ${!selectedIface ? "tab-btn--active" : ""}`}
                  onClick={() => setSelectedIface(null)}
                >
                  <TypeBadge type="combined" />
                  <span>Paquete completo</span>
                </button>

                {interfaces.map((iface, i) => (
                  <button
                    key={i}
                    type="button"
                    className={`tab-btn ${selectedIface === iface ? "tab-btn--active" : ""}`}
                    onClick={() => setSelectedIface(iface)}
                  >
                    <TypeBadge type={iface.type} />
                    <span>{iface.file_name}</span>
                  </button>
                ))}
              </nav>
            )}

            {/* ── Summary ─────────────────────────────────── */}
            <section className="capture-summary card">
              <div>
                <span className="summary-label">Fuente evaluada</span>
                <strong>{captureResult.url || "No especificada"}</strong>
              </div>
              <div>
                <span className="summary-label">Tipo</span>
                <strong>{inputType.toUpperCase()}</strong>
              </div>
              {isZip && (
                <div>
                  <span className="summary-label">Tipo de proyecto</span>
                  <strong>{captureResult.project_type || "zip"}</strong>
                </div>
              )}
              <div>
                <span className="summary-label">Capturas</span>
                <strong>{captures.length}</strong>
              </div>
              {interfaces.length > 0 && (
                <div>
                  <span className="summary-label">Interfaces</span>
                  <strong>{interfaces.length}</strong>
                </div>
              )}
            </section>

            {/* ── Agent message ───────────────────────────── */}
            <section className="capture-message card">
              <h2>Resultado del agente</h2>
              <p>
                {captureResult.message ||
                  "El Agente de Captura procesó la entrada correctamente."}
              </p>
              {activeHtml ? (
                <div className="success-box">
                  Se obtuvo contenido HTML para continuar con la réplica y
                  evaluación técnica.
                </div>
              ) : (
                <div className="error-box">
                  No se encontró HTML evaluable. Revise la fuente de entrada.
                </div>
              )}
            </section>

            {/* ── Captures grid ───────────────────────────── */}
            {captures.length > 0 ? (
              <section className="captures-section">
                <div className="section-title">
                  <h2>Capturas generadas</h2>
                  <p>
                    Vista comparativa de la interfaz en resoluciones desktop,
                    tablet y mobile.
                  </p>
                </div>

                <div className="capture-grid">
                  {captures.map((item, index) => (
                    <article className="capture-card card" key={index}>
                      <div className="capture-card-header">
                        <div>
                          <h3>{getDeviceLabel(item.device)}</h3>
                          <p>
                            {item.width} × {item.height}
                          </p>
                        </div>
                        <span>{item.error ? "Error" : "OK"}</span>
                      </div>

                      {item.error ? (
                        <div className="capture-error">
                          <strong>No se pudo generar esta captura</strong>
                          <p>{item.error}</p>
                        </div>
                      ) : (
                        <div className={`device-preview ${item.device}`}>
                          {getImageSource(item) ? (
                            <img
                              src={getImageSource(item)}
                              alt={`Captura ${item.device}`}
                              className="device-img"
                            />
                          ) : (
                            <p>No se encontró la imagen de captura.</p>
                          )}
                        </div>
                      )}
                    </article>
                  ))}
                </div>
              </section>
            ) : (
              <section className="no-captures card">
                <h2>No se generaron capturas visuales</h2>
                <p>
                  Esto puede ocurrir cuando el backend no pudo renderizar la
                  interfaz. El sistema continuará usando el contenido HTML
                  extraído como artefacto evaluable.
                </p>
              </section>
            )}

            {/* ── Actions ─────────────────────────────────── */}
            <div className="page-actions">
              <button className="secondary-btn" type="button" onClick={goBack}>
                Volver
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToHtml}
                disabled={!activeHtml}
              >
                Continuar a réplica HTML
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}