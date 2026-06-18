import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_URL } from "../services/api";
import "./Capture.css";

export default function Capture() {
  const navigate = useNavigate();

  const [captureResult, setCaptureResult] = useState(null);
  const [error, setError] = useState("");

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
    if (!captureResult?.captures || !Array.isArray(captureResult.captures)) {
      return [];
    }

    return captureResult.captures;
  }, [captureResult]);

  const inputType = localStorage.getItem("inputType") || "url";

  const continueToHtml = () => {
    navigate("/html");
  };

  const goBack = () => {
    navigate("/input");
  };

  const getDeviceLabel = (device) => {
    if (device === "desktop") return "Desktop";
    if (device === "tablet") return "Tablet";
    if (device === "mobile") return "Mobile";
    return "Vista";
  };

  const getImageSource = (item) => {
    if (item.public_url) {
      if (item.public_url.includes("http://127.0.0.1:8000")) {
        return item.public_url.replace("http://127.0.0.1:8000", API_URL);
      }
      return item.public_url;
    }

    if (item.file_name) {
      return `${API_URL}/captures/${item.file_name}`;
    }

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
            En esta etapa, el framework registra la fuente de análisis y muestra
            las capturas generadas en diferentes resoluciones. Estas evidencias
            servirán para la réplica HTML y la evaluación ISO/IEC 25010.
          </p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {!error && captureResult && (
          <>
            <section className="capture-summary card">
              <div>
                <span className="summary-label">Fuente evaluada</span>
                <strong>{captureResult.url || "No especificada"}</strong>
              </div>

              <div>
                <span className="summary-label">Tipo de entrada</span>
                <strong>{inputType.toUpperCase()}</strong>
              </div>

              <div>
                <span className="summary-label">Estado</span>
                <strong>{captureResult.status || "completed"}</strong>
              </div>

              <div>
                <span className="summary-label">Capturas</span>
                <strong>{captures.length}</strong>
              </div>
            </section>

            <section className="capture-message card">
              <h2>Resultado del agente</h2>
              <p>
                {captureResult.message ||
                  "El Agente de Captura procesó la entrada correctamente."}
              </p>

              {captureResult.html_content ? (
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
                  Esto es normal cuando el análisis inicia desde código HTML
                  pegado manualmente o desde un archivo ZIP. El sistema
                  continuará usando el contenido HTML extraído como artefacto
                  evaluable.
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
                onClick={continueToHtml}
                disabled={!captureResult.html_content}
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