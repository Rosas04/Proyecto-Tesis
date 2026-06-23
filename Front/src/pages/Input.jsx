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

  const [detectedInterfaces, setDetectedInterfaces] = useState([]);
  const [zipUploadResult, setZipUploadResult] = useState(null);
  const [selectedInterfaceIndex, setSelectedInterfaceIndex] = useState(null);

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

    setDetectedInterfaces([]);
    setZipUploadResult(null);
    setSelectedInterfaceIndex(null);

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
          err?.message ||
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

        if (result?.status === "error" || result?.extraction?.status === "error") {
          setError(
            result?.extraction?.message ||
              result?.message ||
              "No se pudo procesar el archivo ZIP."
          );
          return;
        }

        const interfaces = result?.extraction?.interfaces || [];

        if (interfaces.length > 1) {
          // El ZIP contiene más de una interfaz (más de un archivo HTML).
          // Se le pide al usuario elegir cuál evaluar antes de continuar,
          // en vez de mezclar el código de todas las páginas.
          setZipUploadResult(result);
          setDetectedInterfaces(interfaces);
          setSelectedInterfaceIndex(0);
          return;
        }

        const singleInterfaceHtml = interfaces.length === 1 ? interfaces[0].html_content : "";
        const combinedCode = result?.extraction?.combined_code || "";

        proceedWithZipResult(result, singleInterfaceHtml || combinedCode);
      } catch (err) {
        setError(
          err?.message ||
            "No se pudo procesar el ZIP. Verifique que el backend esté encendido y que el archivo sea válido."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  const proceedWithZipResult = (result, htmlContent, interfaceIndex = null) => {
    const interfaces = result?.extraction?.interfaces || [];
    const selectedName =
      interfaceIndex !== null && interfaces[interfaceIndex]
        ? interfaces[interfaceIndex].file_name
        : zipName;

    const captureResult = {
      agent: "ZipInput",
      status: "completed",
      source_type: "zip",
      url: selectedName || zipName,
      message:
        interfaces.length > 1
          ? `Proyecto ZIP procesado correctamente. Interfaz seleccionada: ${selectedName}.`
          : "Proyecto ZIP procesado correctamente.",
      html_content: htmlContent,
      captures: [],
      total_captures: 0,
      zip_result: result,
    };

    localStorage.setItem("zipResult", JSON.stringify(result));
    localStorage.setItem("captureResult", JSON.stringify(captureResult));

    navigate("/capture");
  };

  const confirmInterfaceSelection = () => {
    if (selectedInterfaceIndex === null || !detectedInterfaces[selectedInterfaceIndex]) {
      setError("Seleccione una interfaz del proyecto ZIP para continuar.");
      return;
    }

    const selectedHtml = detectedInterfaces[selectedInterfaceIndex].html_content || "";

    cleanPreviousAnalysis();
    localStorage.setItem("inputType", "zip");
    localStorage.setItem("inputUrl", "");
    localStorage.setItem("inputZip", zipName);

    proceedWithZipResult(zipUploadResult, selectedHtml, selectedInterfaceIndex);
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
                CSS, JS, JSX o TSX y preparará el artefacto para evaluación. Si
                el proyecto contiene varias páginas HTML, podrá elegir cuál
                interfaz evaluar.
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

              {detectedInterfaces.length > 1 && (
                <div className="interfaces-panel">
                  <h3>
                    Se detectaron {detectedInterfaces.length} interfaces en el
                    proyecto
                  </h3>
                  <p>
                    Seleccione la página HTML que desea evaluar en este
                    análisis. Cada interfaz incluye únicamente su propio CSS
                    y JavaScript asociado.
                  </p>

                  <div className="interfaces-list">
                    {detectedInterfaces.map((iface, index) => (
                      <label
                        className={
                          selectedInterfaceIndex === index
                            ? "interface-option selected"
                            : "interface-option"
                        }
                        key={iface.relative_path || index}
                      >
                        <input
                          type="radio"
                          name="selectedInterface"
                          checked={selectedInterfaceIndex === index}
                          onChange={() => setSelectedInterfaceIndex(index)}
                        />

                        <span className="interface-option-text">
                          <strong>{iface.name || iface.file_name}</strong>
                          <small>{iface.relative_path}</small>
                        </span>
                      </label>
                    ))}
                  </div>

                  <div className="page-actions">
                    <button
                      className="primary-btn"
                      type="button"
                      onClick={confirmInterfaceSelection}
                    >
                      Continuar con interfaz seleccionada
                    </button>
                  </div>
                </div>
              )}
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
              disabled={loading || detectedInterfaces.length > 1}
            >
              {loading ? "Procesando..." : "Iniciar análisis"}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}