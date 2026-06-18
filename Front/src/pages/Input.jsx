import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { captureInterfaceByUrl, uploadZip } from "../services/api";
import "./Input.css";

export default function Input() {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("url");
  const [url, setUrl] = useState("");
  const [htmlCode, setHtmlCode] = useState("");
  const [zipFile, setZipFile] = useState(null);
  const [zipName, setZipName] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const cleanPreviousAnalysis = () => {
    localStorage.removeItem("inputType");
    localStorage.removeItem("inputUrl");
    localStorage.removeItem("inputZip");
    localStorage.removeItem("captureResult");
    localStorage.removeItem("zipResult");
    localStorage.removeItem("htmlReplicaResult");
    localStorage.removeItem("isoEvaluation");
    localStorage.removeItem("technicalReport");
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setError("");
  };

  const handleZipChange = (event) => {
    const file = event.target.files[0];

    if (!file) {
      setZipFile(null);
      setZipName("");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError("Debe seleccionar un archivo con extensión .zip.");
      setZipFile(null);
      setZipName("");
      return;
    }

    setZipFile(file);
    setZipName(file.name);
    setError("");
  };

  const startAnalysis = async () => {
    setError("");

    if (activeTab === "url" && !url.trim()) {
      setError("Ingrese una URL válida para iniciar la captura.");
      return;
    }

    if (activeTab === "zip" && !zipFile) {
      setError("Seleccione un archivo ZIP del proyecto frontend.");
      return;
    }

    cleanPreviousAnalysis();

    localStorage.setItem("inputType", activeTab);
    localStorage.setItem("inputUrl", url.trim());
    localStorage.setItem("inputZip", zipName);

    if (activeTab === "url") {
      try {
        setLoading(true);

        const result = await captureInterfaceByUrl(url.trim());

        localStorage.setItem("captureResult", JSON.stringify(result));
        navigate("/capture");
      } catch (err) {
        setError(
          "No se pudo capturar la URL. Verifique que el backend esté encendido y que la URL sea accesible."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }

      return;
    }


    if (activeTab === "zip") {
      try {
        setLoading(true);

        const result = await uploadZip(zipFile);

        const combinedCode =
          result?.extraction?.combined_code ||
          result?.combined_code ||
          "";

        const captureResult = {
          agent: "ZipInput",
          status: "completed",
          source_type: "zip",
          url: zipName,
          message: "Proyecto ZIP procesado correctamente.",
          html_content: combinedCode,
          captures: [],
          total_captures: 0,
          zip_result: result,
        };

        localStorage.setItem("zipResult", JSON.stringify(result));
        localStorage.setItem("captureResult", JSON.stringify(captureResult));

        navigate("/capture");
      } catch (err) {
        setError(
          "No se pudo procesar el ZIP. Verifique que el backend esté encendido y que el archivo sea válido."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="input-main">
        <section className="page-header">
          <p className="page-kicker">Inicio del análisis</p>
          <h1 className="page-title">Evaluación técnica frontend</h1>
          <p className="page-description">
            Ingrese una URL, cargue un proyecto comprimido o pegue código HTML
            para iniciar el flujo agéntico de captura, réplica, evaluación
            ISO/IEC 25010 y generación de reporte técnico.
          </p>
        </section>

        <section className="input-card card">
          <div className="tabs">
            <button
              className={activeTab === "url" ? "tab active" : "tab"}
              onClick={() => handleTabChange("url")}
              type="button"
            >
              URL pública
            </button>

            <button
              className={activeTab === "zip" ? "tab active" : "tab"}
              onClick={() => handleTabChange("zip")}
              type="button"
            >
              Proyecto ZIP
            </button>

          </div>

          {activeTab === "url" && (
            <div className="input-panel">
              <h2>Analizar interfaz por URL</h2>
              <p>
                El Agente de Captura abrirá la página, extraerá el DOM y
                generará evidencias visuales en diferentes resoluciones.
              </p>

              <label className="field-label">URL de la interfaz</label>
              <input
                className="form-input"
                type="url"
                placeholder="https://ejemplo.com"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
              />
            </div>
          )}

          {activeTab === "zip" && (
            <div className="input-panel">
              <h2>Analizar proyecto frontend comprimido</h2>
              <p>
                El sistema recibirá el archivo ZIP, extraerá los archivos HTML,
                CSS, JS, JSX o TSX y preparará el artefacto para evaluación.
              </p>

              <label className="upload-box">
                <input
                  type="file"
                  accept=".zip"
                  onChange={handleZipChange}
                  hidden
                />

                <span className="upload-icon">ZIP</span>

                <strong>
                  {zipName || "Seleccione un archivo .zip del proyecto"}
                </strong>

                <small>
                  No incluya node_modules, venv, dist, uploads ni capturas.
                </small>
              </label>
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          {loading && (
            <div className="loading-box">
              Procesando análisis inicial. Espere unos segundos...
            </div>
          )}

          <div className="page-actions">
            <button
              className="primary-btn"
              type="button"
              onClick={startAnalysis}
              disabled={loading}
            >
              {loading ? "Procesando..." : "Iniciar análisis"}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}