import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAnalysis } from "../context/AnalysisContext";
import { getCaptureProgress } from "../services/api";
import "./Input.css";

export default function Input() {
  const { loading, error, setError, startAnalysis, cancelAnalysis } = useAnalysis();

  const [activeTab, setActiveTab] = useState(() => localStorage.getItem("inputType") || "url");
  const [url, setUrl] = useState(() => localStorage.getItem("inputUrl") || "");
  const [zipFile, setZipFile] = useState(null);
  const [zipName, setZipName] = useState(() => localStorage.getItem("inputZip") || "");
  const [logs, setLogs] = useState([]);

  // Real-time logs polling
  useEffect(() => {
    if (!loading) {
      setLogs([{ time: new Date().toLocaleTimeString(), type: "INFO", message: "Agente listo. Esperando inicio de análisis..." }]);
      return;
    }

    setLogs([{ time: new Date().toLocaleTimeString(), type: "INFO", message: "Agente iniciado. Obteniendo logs..." }]);
    
    const interval = setInterval(async () => {
      try {
        const data = await getCaptureProgress();
        if (data && data.logs && data.logs.length > 0) {
          setLogs([
            { time: new Date().toLocaleTimeString(), type: "INFO", message: "Agente iniciado." },
            ...data.logs
          ]);
        }
      } catch (err) {
        // Ignorar errores de red para no interrumpir el polling
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [loading]);

  // Credentials state
  const [useCredentials, setUseCredentials] = useState(false);
  const [loginUrl, setLoginUrl] = useState("");
  const [usernameSelector, setUsernameSelector] = useState("");
  const [usernameValue, setUsernameValue] = useState("");
  const [passwordSelector, setPasswordSelector] = useState("");
  const [passwordValue, setPasswordValue] = useState("");
  const [submitSelector, setSubmitSelector] = useState("");
  const [showAdvancedLogin, setShowAdvancedLogin] = useState(false);
  const [maxPages, setMaxPages] = useState(10);

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

  const handleStart = () => {
    const credentials = useCredentials ? {
      mode: "form",
      login_url: loginUrl.trim() || url.trim(),
      username_selector: usernameSelector.trim() || null,
      username: usernameValue,
      password_selector: passwordSelector.trim() || null,
      password: passwordValue,
      submit_selector: submitSelector.trim() || null,
    } : null;

    startAnalysis({
      activeTab,
      url,
      zipFile,
      zipName,
      useCredentials,
      credentials,
      maxPages
    });
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="input-main new-design">
        <header className="page-header eval-header">
          <div className="eval-header-left">
            <div>
              <h1 className="page-title">{activeTab === "url" ? "Analizar interfaz por URL" : "Analizar proyecto frontend comprimido"}</h1>
            </div>
          </div>
        </header>

        <div className="tabs-header-container">
          <div className="tabs-container">
            <button
              className={`tab-btn ${activeTab === "url" ? "active" : ""}`}
              onClick={() => handleTabChange("url")}
              type="button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
              Analizar por URL
            </button>
            <button
              className={`tab-btn ${activeTab === "zip" ? "active" : ""}`}
              onClick={() => handleTabChange("zip")}
              type="button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line></svg>
              Proyecto ZIP
            </button>
          </div>
        </div>

        <section className="input-grid">
          <div className="input-card card">
            {/* ── URL panel ────────────────────────────── */}
            {activeTab === "url" && (
              <div className="input-panel">
                <div className="form-group">
                  <label className="field-label">URL de la interfaz</label>
                  <div className="input-with-icon">
                    <svg className="input-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    <input
                      className="form-input has-icon"
                      type="url"
                      placeholder="https://www.urlexample.com"
                      value={url}
                      onChange={(event) => setUrl(event.target.value)}
                      disabled={loading}
                    />
                  </div>
                </div>

                <div className="credentials-box">
                  <div className="credentials-header">
                    <label className="checkbox-label-custom">
                      <input
                        type="checkbox"
                        checked={useCredentials}
                        onChange={(e) => setUseCredentials(e.target.checked)}
                        disabled={loading}
                      />
                      <span className="checkbox-custom">
                        {useCredentials && <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
                      </span>
                      <span className="checkbox-text">¿Requiere inicio de sesión (Credenciales)?</span>
                    </label>
                  </div>

                  {useCredentials && (
                    <div className="credentials-content">
                      <div className="credentials-section-title">
                        <h3>Datos de autenticación</h3>
                        <p>Ingresa las credenciales para iniciar sesión en la plataforma.</p>
                      </div>
                      <div className="credentials-grid">
                        <div>
                          <label className="field-label-small">Usuario / Correo</label>
                          <input
                            className="form-input-small"
                            type="text"
                            placeholder="usuario@ejemplo.com"
                            value={usernameValue}
                            onChange={(e) => setUsernameValue(e.target.value)}
                            disabled={loading}
                          />
                        </div>
                        <div>
                          <label className="field-label-small">Contraseña</label>
                          <input
                            className="form-input-small filled"
                            type="password"
                            placeholder="••••••••"
                            value={passwordValue}
                            onChange={(e) => setPasswordValue(e.target.value)}
                            disabled={loading}
                          />
                        </div>
                      </div>

                      <button
                        type="button"
                        className="advanced-btn-link"
                        onClick={() => setShowAdvancedLogin(!showAdvancedLogin)}
                        disabled={loading}
                      >
                        {showAdvancedLogin ? "▼" : "▶"} Opciones avanzadas (Selectores personalizados / URL de login)
                      </button>

                      {showAdvancedLogin && (
                        <div className="advanced-options-grid">
                          <div className="full-width-col">
                            <label className="field-label-small">URL del Login (Opcional)</label>
                            <input
                              className="form-input-small"
                              type="url"
                              placeholder="https://ejemplo.com/login"
                              value={loginUrl}
                              onChange={(e) => setLoginUrl(e.target.value)}
                              disabled={loading}
                            />
                          </div>
                          <div>
                            <label className="field-label-small">Selector Usuario</label>
                            <input
                              className="form-input-small"
                              type="text"
                              placeholder="input[type=email]"
                              value={usernameSelector}
                              onChange={(e) => setUsernameSelector(e.target.value)}
                              disabled={loading}
                            />
                          </div>
                          <div>
                            <label className="field-label-small">Selector Contraseña</label>
                            <input
                              className="form-input-small"
                              type="text"
                              placeholder="input[type=password]"
                              value={passwordSelector}
                              onChange={(e) => setPasswordSelector(e.target.value)}
                              disabled={loading}
                            />
                          </div>
                          <div className="full-width-col">
                            <label className="field-label-small">Selector Botón Enviar</label>
                            <input
                              className="form-input-small"
                              type="text"
                              placeholder="button[type=submit]"
                              value={submitSelector}
                              onChange={(e) => setSubmitSelector(e.target.value)}
                              disabled={loading}
                            />
                          </div>
                          <div className="full-width-col">
                            <label className="field-label-small">Max Interfaces</label>
                            <input
                              className="form-input-small number-input"
                              type="number"
                              min="1"
                              max="50"
                              value={maxPages}
                              onChange={(e) => setMaxPages(Math.max(1, Math.min(50, parseInt(e.target.value) || 10)))}
                              disabled={loading}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="considerations-box">
                  <div className="considerations-header">
                    <div className="considerations-title">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                      <strong>Consideraciones importantes</strong>
                    </div>
                    <svg className="chevron-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                  <ul className="considerations-list">
                    <li>La URL debe ser pública o accesible desde el entorno de evaluación.</li>
                    <li>Si requiere autenticación, asegúrate de tener las credenciales correctas.</li>
                    <li>El análisis se enfoca en el frontend (estilos, diseño, usabilidad, accesibilidad y rendimiento).</li>
                  </ul>
                </div>
              </div>
            )}

            {/* ── ZIP panel ────────────────────────────── */}
            {activeTab === "zip" && (
              <div className="input-panel">
                <label className={`upload-box ${loading ? 'disabled' : ''}`}>
                  <input
                    type="file"
                    accept=".zip"
                    onChange={handleZipChange}
                    hidden
                    disabled={loading}
                  />
                  <span className="upload-icon">ZIP</span>
                  <div>
                    <strong>
                      {zipName || "Seleccione un archivo .zip del proyecto"}
                    </strong>
                    <small>
                      No incluya node_modules, venv, dist, uploads ni capturas.
                    </small>
                  </div>
                </label>
              </div>
            )}

            {/* ── Error ───────────────────────── */}
            {error && <div className="error-box">{error}</div>}

            {/* ── Action ───────────────────────────────── */}
            <div className="page-actions-full">
              <div style={{ display: "flex", gap: "16px", width: "100%" }}>
                <button
                  className={`primary-btn-blue full-width-btn ${loading ? 'processing-btn' : ''}`}
                  type="button"
                  onClick={handleStart}
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="white" stroke="white" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                  {loading ? "Procesando..." : "Iniciar análisis"}
                </button>
                {loading && (
                  <button 
                    type="button" 
                    onClick={cancelAnalysis} 
                    className="cancel-btn-red"
                    style={{ padding: "0 24px" }}
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </div>
          </div>
          
          {/* Right Sidebar Info */}
          <div className="info-sidebar">
            <div className="info-card side-card">
              <div className="info-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                <h3>¿Qué se evalúa?</h3>
              </div>
              <p className="info-text">La interfaz será analizada en base a los criterios de la norma ISO/IEC 25010, considerando:</p>
              <ul className="criteria-list-vertical">
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Adecuación funcional</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Eficiencia de desempeño</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Usabilidad</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Accesibilidad</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Mantenibilidad</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Compatibilidad</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Seguridad</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg> Portabilidad</li>
              </ul>
            </div>
            
            <div className="terminal-card">
              <div className="terminal-header">
                <div className="terminal-title">
                  <span className="terminal-icon">{">_"}</span>
                  <h3>Flujo de Agente</h3>
                </div>
                <div className="terminal-controls">
                  <span className="terminal-control-btn">{">_"}</span>
                </div>
              </div>
              <div className="terminal-body">
                {logs.map((log, index) => (
                  <div key={index} className="terminal-log-line">
                    <span className="log-date">[{log.time}]</span>{" "}
                    <span className={`log-${log.type.toLowerCase()}`}>[{log.type}]</span>{" "}
                    {log.message}
                  </div>
                ))}
                {loading && <div className="terminal-log-line blink-cursor">_</div>}
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}