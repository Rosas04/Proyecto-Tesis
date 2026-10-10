import { useState, useEffect, useRef, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import { useAnalysis } from "../context/AnalysisContext";
import { getCaptureProgress } from "../services/api";
import "./Input.css";

const EXCLUDED_FOLDERS = ["node_modules", "venv", "dist", "uploads", "capturas"];

const ZIP_STEPS = [
  { key: "upload", label: "Cargando", sublabel: "Archivo recibido" },
  { key: "validate", label: "Validando", sublabel: "Estructura y contenido" },
  { key: "analyze", label: "Analizando", sublabel: "Estructura del proyecto" },
  { key: "report", label: "Generando reporte", sublabel: "Resultados del análisis" },
];

function formatFileSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
}

export default function Input() {
  const { loading, error, setError, startAnalysis, cancelAnalysis } = useAnalysis();

  const [activeTab, setActiveTab] = useState(() => localStorage.getItem("inputType") || "url");
  const [url, setUrl] = useState(() => localStorage.getItem("inputUrl") || "");
  const [zipFile, setZipFile] = useState(null);
  const [zipName, setZipName] = useState(() => localStorage.getItem("inputZip") || "");
  const [zipSize, setZipSize] = useState(0);
  const [logs, setLogs] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [zipProgress, setZipProgress] = useState(0);
  const [zipStepIndex, setZipStepIndex] = useState(0);
  const fileInputRef = useRef(null);

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

  const processZipFile = useCallback((file) => {
    if (!file) {
      setZipFile(null);
      setZipName("");
      setZipSize(0);
      return;
    }

    if (!file.name.toLowerCase().endsWith(".zip")) {
      setError("Debe seleccionar un archivo con extensión .zip.");
      setZipFile(null);
      setZipName("");
      setZipSize(0);
      return;
    }

    setZipFile(file);
    setZipName(file.name);
    setZipSize(file.size);
    setError("");
  }, [setError]);

  const handleZipChange = (event) => {
    processZipFile(event.target.files[0]);
  };

  const handleZipRemove = () => {
    setZipFile(null);
    setZipName("");
    setZipSize(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleZipReplace = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  // Drag and drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (loading) return;
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processZipFile(files[0]);
    }
  };

  // Simulate progress for ZIP loading state
  useEffect(() => {
    if (!loading || activeTab !== "zip") {
      setZipProgress(0);
      setZipStepIndex(0);
      return;
    }

    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 8 + 2;
      if (progress > 95) progress = 95;
      setZipProgress(Math.round(progress));

      if (progress < 20) setZipStepIndex(0);
      else if (progress < 45) setZipStepIndex(1);
      else if (progress < 80) setZipStepIndex(2);
      else setZipStepIndex(3);
    }, 800);

    return () => clearInterval(interval);
  }, [loading, activeTab]);

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
              <div className="input-panel zip-panel-redesigned">
                {/* Hidden file input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  aria-label="Archivo ZIP del proyecto"
                  accept=".zip"
                  onChange={handleZipChange}
                  hidden
                  disabled={loading}
                />

                {/* Upload area + Selected file */}
                <div className="zip-upload-row">
                  {/* Drop zone */}
                  <div
                    className={`zip-drop-zone ${isDragging ? "dragging" : ""} ${loading ? "disabled" : ""}`}
                    onClick={() => !loading && fileInputRef.current?.click()}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                  >
                    <div className="zip-drop-icon">
                      <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
                        <rect x="12" y="8" width="40" height="48" rx="4" fill="#dbeafe" stroke="#93c5fd" strokeWidth="2"/>
                        <rect x="20" y="16" width="24" height="4" rx="1" fill="#93c5fd"/>
                        <rect x="20" y="24" width="24" height="4" rx="1" fill="#93c5fd"/>
                        <rect x="20" y="32" width="16" height="4" rx="1" fill="#93c5fd"/>
                        <text x="32" y="50" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#2563eb">ZIP</text>
                      </svg>
                      <div className="zip-drop-badge">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                          <path d="M12 4v16m-8-8h16" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                        </svg>
                      </div>
                    </div>
                    <p className="zip-drop-title">Arrastra tu proyecto aquí</p>
                    <p className="zip-drop-subtitle">o selecciona un archivo</p>
                  </div>

                  {/* Selected file info */}
                  <div className={`zip-file-info ${zipName ? "has-file" : ""}`}>
                    {zipName ? (
                      <>
                        <h4 className="zip-file-header">Archivo seleccionado</h4>
                        <div className="zip-file-detail">
                          <div className="zip-file-icon-small">
                            <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
                              <rect x="8" y="4" width="36" height="44" rx="3" fill="#dbeafe" stroke="#93c5fd" strokeWidth="1.5"/>
                              <text x="26" y="32" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#2563eb">ZIP</text>
                            </svg>
                          </div>
                          <div className="zip-file-meta">
                            <p className="zip-file-name">{zipName}</p>
                            <p className="zip-file-size">{formatFileSize(zipSize)} · ZIP</p>
                          </div>
                          <div className="zip-file-actions">
                            <button
                              type="button"
                              className="zip-action-btn"
                              onClick={handleZipReplace}
                              disabled={loading}
                              title="Reemplazar archivo"
                            >
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="1 4 1 10 7 10"/>
                                <polyline points="23 20 23 14 17 14"/>
                                <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                              </svg>
                            </button>
                            <button
                              type="button"
                              className="zip-action-btn delete"
                              onClick={handleZipRemove}
                              disabled={loading}
                              title="Eliminar archivo"
                            >
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                              </svg>
                            </button>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="zip-file-empty">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        <p>Ningún archivo seleccionado</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Exclusion validations */}
                <div className="zip-exclusions">
                  <div className="zip-exclusions-label">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" fill="#10b981"/>
                      <polyline points="8 12 11 15 16 9" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <div>
                      <strong>Validaciones de exclusión</strong>
                      <span>Se excluirán las carpetas que no son necesarias para el análisis.</span>
                    </div>
                  </div>
                  <div className="zip-exclusion-badges">
                    {EXCLUDED_FOLDERS.map((folder) => (
                      <span key={folder} className="zip-exclusion-badge">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                          <circle cx="12" cy="12" r="10" fill="#10b981"/>
                          <polyline points="8 12 11 15 16 9" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        {folder}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Progress section - only during loading */}
                {loading && activeTab === "zip" && (
                  <div className="zip-progress-section">
                    <div className="zip-progress-header">
                      <div className="zip-progress-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
                        </svg>
                        <strong>Analizando estructura del proyecto</strong>
                        <span className="zip-progress-pct">· {zipProgress}%</span>
                      </div>
                      <div className="zip-progress-time">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="10"/>
                          <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <span>Tiempo estimado: 1–2 minutos</span>
                      </div>
                    </div>
                    <div className="zip-progress-bar-track">
                      <div className="zip-progress-bar-fill" style={{ width: `${zipProgress}%` }}/>
                    </div>
                    <div className="zip-stepper">
                      {ZIP_STEPS.map((step, idx) => (
                        <div key={step.key} className={`zip-step ${idx < zipStepIndex ? "completed" : ""} ${idx === zipStepIndex ? "active" : ""} ${idx > zipStepIndex ? "pending" : ""}`}>
                          <div className="zip-step-indicator">
                            {idx < zipStepIndex ? (
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                <circle cx="12" cy="12" r="10" fill="#10b981"/>
                                <polyline points="8 12 11 15 16 9" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            ) : idx === zipStepIndex ? (
                              <div className="zip-step-active-dot">
                                <div className="zip-step-pulse"/>
                              </div>
                            ) : (
                              <div className="zip-step-number">{idx + 1}</div>
                            )}
                          </div>
                          {idx < ZIP_STEPS.length - 1 && <div className={`zip-step-line ${idx < zipStepIndex ? "filled" : ""}`}/>}
                          <p className="zip-step-label">{step.label}</p>
                          <p className="zip-step-sublabel">{step.sublabel}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Error ───────────────────────── */}
            {error && <div className="error-box">{error}</div>}

            {/* ── Action ───────────────────────────────── */}
            <div className="page-actions-full">
              <div className="zip-actions-row">
                <button
                  className={`primary-btn-blue full-width-btn ${loading ? 'processing-btn' : ''}`}
                  type="button"
                  onClick={handleStart}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <svg className="spin-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                      </svg>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="white" stroke="white" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                      Iniciar análisis
                    </>
                  )}
                </button>
                {loading && (
                  <button
                    type="button"
                    onClick={cancelAnalysis}
                    className="cancel-btn-outline"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="3" y="3" width="18" height="18" rx="2"/>
                    </svg>
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