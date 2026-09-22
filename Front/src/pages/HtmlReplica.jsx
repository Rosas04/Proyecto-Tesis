import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { replicateHtmlFromContent } from "../services/api";
import { storageService } from "../services/storageService";
import { getInterfaceLabel } from "../utils/interfaceLabel";
import { TypeBadge } from "../components/TypeBadge";
import "./HtmlReplica.css";

export default function HtmlReplica() {
  const navigate = useNavigate();
  const tabsRef = useRef(null);

  const [captureResult, setCaptureResult] = useState(null);
  const [replicaResult, setReplicaResult] = useState(null);
  const [htmlPreview, setHtmlPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedIface, setSelectedIface] = useState(null);
  const [replicatedCache, setReplicatedCache] = useState({});

  const inputType = localStorage.getItem("inputType") || "url";
  const inputUrl = localStorage.getItem("inputUrl") || "";


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
      const parsedReplica = storageService.getHtmlReplicaResult();

      if (parsedReplica) {
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

  async function initialGenerate(htmlContent, iface, captureData) {
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
      // Bypass localStorage for massive HTML replicas to avoid QuotaExceededError
      // storageService.setHtmlReplicaResult(result);
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

  const previewHtmlWithBase = useMemo(() => {
    if (!htmlPreview) return "";
    let sourceUrl = selectedIface?.url || captureResult?.url || inputUrl;
    
    // Validate if it's a valid URL
    if (!sourceUrl || !sourceUrl.startsWith('http')) return htmlPreview;

    // If it already has a base tag, do nothing
    if (htmlPreview.includes('<base ')) return htmlPreview;

    const baseTag = `<base href="${sourceUrl}">`;
    if (htmlPreview.includes('<head>')) {
      return htmlPreview.replace('<head>', `<head>\n  ${baseTag}`);
    } else if (htmlPreview.includes('<html>')) {
      return htmlPreview.replace('<html>', `<html>\n<head>\n  ${baseTag}\n</head>`);
    } else {
      return `${baseTag}\n${htmlPreview}`;
    }
  }, [htmlPreview, selectedIface, captureResult, inputUrl]);

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
      if (!storageService.setHtmlToEvaluate(htmlPreview)) {
        // Fallback for quota limit
        console.warn("Quota exceeded, cleaning older storage...");
        storageService.removeItem("zipResult");
        storageService.removeItem("captureResult");
        storageService.removeItem("htmlReplicaResult");
        
        if (!storageService.setHtmlToEvaluate(htmlPreview)) {
          setError("El HTML es demasiado grande para guardarse en el almacenamiento.");
          return;
        }
      }
      navigate("/evaluation");
    } catch (e) {
      console.error(e);
    }
  };

  const goBack = () => {
    navigate("/capture");
  };

  return (
    <div className="layout">
      <Sidebar />

      <main className="html-main">
        <header className="page-header replica-header">
          <div className="replica-header-left">
            <div className="replica-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
              </svg>
            </div>
            <div>
              <h1 className="page-title">HTML real o replicado</h1>
              <p className="page-description" style={{ margin: "6px 0 0" }}>Verificación de la autenticidad del contenido HTML para identificar si es una réplica de la interfaz original.</p>
            </div>
          </div>
          <div className="replica-header-right">
            <span>Informe de evaluación</span>
            <strong>FrontMind</strong>
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loading-box">
            Generando réplica HTML evaluable. Espere unos segundos...
          </div>
        )}

        {!loading && captureResult && (
          <>
            <section className="source-summary-card">
              <div className="source-summary-left">
                <span className="label">Fuente</span>
                <strong>
                  {captureResult.url || inputUrl || "No especificada"}
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "4px" }}>
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </strong>
                <span className="sub">URL analizada</span>
              </div>
              
              <div className="source-summary-stats">
                <div className="stat-item">
                  <span>Tipo</span>
                  <strong>{inputType.toUpperCase()}</strong>
                </div>
                <div className="stat-item">
                  <span>Características</span>
                  <strong>{combinedHtmlStats.characters}</strong>
                </div>
                <div className="stat-item">
                  <span>Etiquetas</span>
                  <strong>{combinedHtmlStats.tags}</strong>
                </div>
                <div className="stat-item">
                  <span>Líneas</span>
                  <strong>{combinedHtmlStats.lines}</strong>
                </div>
                <div className="stat-item">
                  <span>Imágenes</span>
                  <strong>{combinedHtmlStats.images}</strong>
                </div>
                <div className="stat-item">
                  <span>Enlaces</span>
                  <strong>{combinedHtmlStats.links}</strong>
                </div>
                <div className="stat-item">
                  <span>Botones</span>
                  <strong>{combinedHtmlStats.buttons}</strong>
                </div>
              </div>
            </section>

            {interfaces.length > 0 && (
              <section className="interfaces-tabs-section card" style={{ padding: "24px", marginBottom: "24px" }}>
                <div className="section-icon-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                    <polyline points="2 17 12 22 22 17"></polyline>
                    <polyline points="2 12 12 17 22 12"></polyline>
                  </svg>
                  <h2>Interfaces detectadas</h2>
                </div>
                <p style={{ color: "#6b7280", fontSize: "14px", margin: "0 0 16px 0" }}>Selecciona una interfaz para revisar su réplica HTML independiente.</p>
                
                <div className="tabs-wrapper">
                  <button 
                    className="tabs-scroll-btn" 
                    onClick={() => tabsRef.current?.scrollBy({ left: -200, behavior: "smooth" })}
                  >
                    &#8592;
                  </button>
                  <nav className="tabs-navigation" ref={tabsRef} style={{ gap: '8px', paddingBottom: '8px', alignItems: 'center', borderBottom: 'none', marginBottom: '0' }}>
                    <button
                      type="button"
                      className={`tab-button ${!selectedIface ? 'active' : ''}`}
                      style={{
                        padding: '8px 16px',
                        borderRadius: '8px',
                        border: !selectedIface ? 'none' : '1px solid #d1d5db',
                        background: !selectedIface ? '#1e3a8a' : '#fff',
                        cursor: 'pointer',
                        fontWeight: !selectedIface ? 'bold' : 'normal',
                        color: !selectedIface ? '#fff' : '#374151',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        whiteSpace: 'nowrap'
                      }}
                      onClick={() => handleTabChange(null)}
                    >
                      {!selectedIface && (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="3" y1="9" x2="21" y2="9"></line>
                          <line x1="9" y1="21" x2="9" y2="9"></line>
                        </svg>
                      )}
                      <span>Todas</span>
                    </button>

                    {interfaces.map((iface, i) => {
                      const isSelected = selectedIface?.file_name === iface.file_name;
                      const rawName = iface.file_name || `interfaz-${i}`;
                      const ext = rawName.split('.').pop().toLowerCase();
                      
                      return (
                        <button
                          key={i}
                          type="button"
                          className={`tab-button ${isSelected ? 'active' : ''}`}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '8px',
                            border: isSelected ? 'none' : '1px solid #d1d5db',
                            background: isSelected ? '#1e3a8a' : '#fff',
                            cursor: 'pointer',
                            fontWeight: isSelected ? 'bold' : 'normal',
                            color: isSelected ? '#fff' : '#374151',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            whiteSpace: 'nowrap'
                          }}
                          onClick={() => handleTabChange(iface)}
                        >
                          <TypeBadge type={iface.type || ext} />
                          <span>{iface.name || getInterfaceLabel(iface.url || rawName, iface.name)}</span>
                        </button>
                      );
                    })}
                  </nav>
                  <button 
                    className="tabs-scroll-btn" 
                    onClick={() => tabsRef.current?.scrollBy({ left: 200, behavior: "smooth" })}
                  >
                    &#8594;
                  </button>
                </div>
              </section>
            )}

            <section className="html-workspace">
              <article className="html-code-panel card" style={{ padding: "24px" }}>
                <div className="section-icon-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  <h2>Código HTML evaluable</h2>
                </div>
                <p style={{ color: "#6b7280", fontSize: "14px", margin: "0 0 16px 0" }}>Contenido generado por el agente de Réplica para ser analizado por el Agente ISO/IEC 25010.</p>
                
                <div className="editor-container">
                  <div className="editor-header">
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="16 18 22 12 16 6"></polyline>
                        <polyline points="8 6 2 12 8 18"></polyline>
                      </svg>
                      HTML
                    </div>
                    <button className="editor-copy-btn" onClick={() => navigator.clipboard.writeText(htmlPreview)}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                      </svg>
                      Copiar
                    </button>
                  </div>
                  <textarea
                    className="html-code"
                    style={{ border: "none", borderRadius: "0" }}
                    value={htmlPreview}
                    onChange={(event) => setHtmlPreview(event.target.value)}
                    spellCheck="false"
                  />
                </div>
              </article>

              <article className="html-preview-panel card" style={{ padding: "24px" }}>
                <div className="section-icon-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <h2>Vista previa</h2>
                </div>
                <p style={{ color: "#6b7280", fontSize: "14px", margin: "0 0 16px 0" }}>Renderización aproximada del HTML replicado para validar su estructura visual.</p>

                <div className="browser-mockup">
                  <div className="browser-header">
                    <div className="browser-dots">
                      <span></span><span></span><span></span>
                    </div>
                    <div className="browser-url-bar">
                      {selectedIface?.url || captureResult?.url || inputUrl || "https://interfaz-evaluada.com"}
                    </div>
                  </div>
                  <div className="preview-frame-wrapper" style={{ border: "none", borderRadius: "0" }}>
                    {htmlPreview ? (
                      <iframe
                        title="Vista previa HTML"
                        className="preview-frame"
                        srcDoc={previewHtmlWithBase}
                        sandbox="allow-same-origin"
                      />
                    ) : (
                      <div className="empty-preview">No existe HTML para mostrar.</div>
                    )}
                  </div>
                </div>
              </article>
            </section>



            <div className="page-actions" style={{ justifyContent: "flex-start", gap: "16px", padding: "0" }}>
              <button className="secondary-btn" type="button" onClick={goBack} style={{ width: "auto" }}>
                ← Volver
              </button>

              <button
                className="primary-btn"
                type="button"
                onClick={continueToEvaluation}
                disabled={!htmlPreview.trim()}
                style={{ width: "auto", background: "#3b4369" }}
              >
                ↻ Evaluar con ISO/IEC 25010
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}