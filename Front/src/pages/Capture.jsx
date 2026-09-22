import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_URL } from "../services/api";
import { storageService } from "../services/storageService";
import { getInterfaceLabel } from "../utils/interfaceLabel";
import { TypeBadge } from "../components/TypeBadge";
import "./Capture.css";

// Icons
const LinkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
  </svg>
);
const GlobeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="2" y1="12" x2="22" y2="12"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
);
const ImageIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    <circle cx="8.5" cy="8.5" r="1.5"/>
    <polyline points="21 15 16 10 5 21"/>
  </svg>
);
const LayersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
    <polyline points="2 12 12 17 22 12"/>
    <polyline points="2 17 12 22 22 17"/>
  </svg>
);
const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
    <line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/>
    <line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);
const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
);
const DesktopIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
    <line x1="8" y1="21" x2="16" y2="21"/>
    <line x1="12" y1="17" x2="12" y2="21"/>
  </svg>
);
const TabletIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
    <line x1="12" y1="18" x2="12.01" y2="18"/>
  </svg>
);
const MobileIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
    <line x1="12" y1="18" x2="12.01" y2="18"/>
  </svg>
);
const LockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);
const RefreshIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"/>
    <polyline points="1 20 1 14 7 14"/>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
  </svg>
);
const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);
const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);
const AllIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"/>
    <rect x="14" y="3" width="7" height="7"/>
    <rect x="14" y="14" width="7" height="7"/>
    <rect x="3" y="14" width="7" height="7"/>
  </svg>
);

export default function Capture() {
  const navigate = useNavigate();
  const tabsRef = useRef(null);

  const [captureResult, setCaptureResult] = useState(null);
  const [error, setError]                 = useState("");
  const [activeTab, setActiveTab] = useState("Todas");
  const [search, setSearch] = useState("");
  const [selectedIface, setSelectedIface] = useState(null); // null = combined

  useEffect(() => {
    const savedCapture = storageService.getCaptureResult();
    if (!savedCapture) {
      setError("No se encontró una captura previa. Inicie un nuevo análisis.");
      return;
    }
    setCaptureResult(savedCapture);
  }, []);

  const inputType = localStorage.getItem("inputType") || "url";
  const url = selectedIface ? selectedIface.url : (captureResult?.url || "https://ejemplo.com");
  
  // Format Date
  const dateObj = captureResult?.created_at ? new Date(captureResult.created_at) : new Date();
  const dateStr = `${dateObj.getDate()} ${dateObj.toLocaleString('es', { month: 'short' })} ${dateObj.getFullYear()}, ${dateObj.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })}`;

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

  const interfacesCount = interfaces.length || (captures.length > 0 ? 1 : 0);

  const filteredCaptures = useMemo(() => {
    let filtered = captures;
    if (activeTab !== "Todas") {
      filtered = filtered.filter(c => c.device.toLowerCase() === activeTab.toLowerCase());
    }
    if (search) {
      filtered = filtered.filter(c => c.device.toLowerCase().includes(search.toLowerCase()));
    }
    return filtered;
  }, [captures, activeTab, search]);

  // The HTML that will be forwarded to HtmlReplica
  const activeHtml = selectedIface
    ? selectedIface.html_content
    : captureResult?.html_content || "";

  const continueToHtml = () => {
    if (activeHtml) {
      const updated = {
        ...captureResult,
        html_content: activeHtml,
        ...(selectedIface ? {
          cssom_styles: selectedIface.cssom_styles || captureResult.cssom_styles,
          selected_interface: {
            name: selectedIface.name,
            url: selectedIface.url,
            route_index: selectedIface.route_index,
            dom_metrics: selectedIface.dom_metrics,
            captures: selectedIface.captures,
          },
        } : {}),
      };
      try {
        localStorage.setItem("captureResult", JSON.stringify(updated));
      } catch (e) {
        window.globalCaptureResult = updated;
      }
      localStorage.removeItem("htmlReplicaResult");
      localStorage.removeItem("isoEvaluation");
      localStorage.removeItem("technicalReport");
    }
    navigate("/html");
  };

  const goBack = () => navigate("/input");

  const getImageSource = (item) => {
    if (item.public_url) {
      return item.public_url.replace(/http:\/\/127\.0\.0\.1:\d+/, API_URL);
    }
    if (item.file_name) return `${API_URL}/captures/${item.file_name}`;
    return "";
  };

  const getDeviceIcon = (device) => {
    if (device === "desktop") return <DesktopIcon />;
    if (device === "tablet") return <TabletIcon />;
    if (device === "mobile") return <MobileIcon />;
    return <DesktopIcon />;
  };

  const getDeviceName = (device) => {
    if (device === "desktop") return "Desktop";
    if (device === "tablet") return "Tablet";
    if (device === "mobile") return "Mobile";
    return "Vista";
  };
  
  const getDeviceRes = (device) => {
    if (device === "desktop") return "1366 x 768";
    if (device === "tablet") return "768 x 1024";
    if (device === "mobile") return "390 x 844";
    return "";
  };

  const getDeviceDesc = (device) => {
    if (device === "desktop") return { title: "Vista completa", text: "Se detecta la interfaz principal de registro en vista de escritorio." };
    if (device === "tablet") return { title: "Vista adaptada", text: "Interfaz correctamente responsive en vista de tablet." };
    if (device === "mobile") return { title: "Vista móvil", text: "Interfaz adaptada correctamente a dispositivos móviles." };
    return { title: "Vista capturada", text: "Captura de la interfaz seleccionada." };
  };

  return (
    <div className="home-layout">
      <Sidebar />

      <main className="capture-main">
        <section className="capture-header-text">
          <h1>Interfaces detectadas</h1>
          <p>A continuación se muestran las interfaces encontradas en el proyecto analizado. Puedes revisarlas por dispositivo y tipo de vista.</p>
        </section>

        {error && <div className="error-box">{error}</div>}

        {!error && captureResult && (
          <>
            {/* ── Summary ─────────────────────────────────── */}
            <div className="capture-summary-row">
              <div className="summary-item">
                <div className="summary-icon"><LinkIcon /></div>
                <div className="summary-info">
                  <span className="summary-label">Fuente evaluada</span>
                  <span className="summary-value" title={url}>{url}</span>
                </div>
              </div>
              <div className="summary-item">
                <div className="summary-icon"><GlobeIcon /></div>
                <div className="summary-info">
                  <span className="summary-label">Tipo</span>
                  <span className="summary-value">{inputType.toUpperCase()}</span>
                </div>
              </div>
              <div className="summary-item">
                <div className="summary-icon"><ImageIcon /></div>
                <div className="summary-info">
                  <span className="summary-label">Capturas</span>
                  <span className="summary-value">{captures.length}</span>
                </div>
              </div>
              <div className="summary-item">
                <div className="summary-icon"><LayersIcon /></div>
                <div className="summary-info">
                  <span className="summary-label">Interfaces</span>
                  <span className="summary-value">{interfacesCount}</span>
                </div>
              </div>
              <div className="summary-item">
                <div className="summary-icon"><CalendarIcon /></div>
                <div className="summary-info">
                  <span className="summary-label">Última evaluación</span>
                  <span className="summary-value">{dateStr}</span>
                </div>
              </div>
            </div>

            {/* ── Interfaces Tabs ─────────────────────────── */}
            {interfaces.length > 0 && (
              <section className="interfaces-tabs-section card" style={{ marginBottom: "2rem", padding: "16px", borderRadius: "12px", background: "white", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.02)" }}>
                <div className="tabs-wrapper" style={{ display: 'flex', alignItems: 'center' }}>
                  <button 
                    className="tabs-scroll-btn" 
                    onClick={() => tabsRef.current?.scrollBy({ left: -200, behavior: "smooth" })}
                    title="Desplazar a la izquierda"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0 8px', fontSize: '18px', color: '#64748b' }}
                  >
                    &#8592;
                  </button>
                  <div className="tabs-navigation" ref={tabsRef} style={{ display: 'flex', overflowX: 'auto', gap: '8px', alignItems: 'center', scrollbarWidth: 'none', flex: 1, paddingBottom: '4px' }}>
                    <button
                      className={`tab-button ${!selectedIface ? 'active' : ''}`}
                      style={{
                        padding: '8px 16px',
                        borderRadius: '8px',
                        border: !selectedIface ? 'none' : '1px solid #d1d5db',
                        background: !selectedIface ? '#1e293b' : '#fff',
                        cursor: 'pointer',
                        fontWeight: !selectedIface ? 'bold' : 'normal',
                        color: !selectedIface ? '#fff' : '#374151',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        whiteSpace: 'nowrap',
                        transition: 'all 0.2s'
                      }}
                      onClick={() => setSelectedIface(null)}
                    >
                      <TypeBadge type="combined" />
                      Vista combinada
                    </button>
                    
                    {interfaces.map((iface, idx) => {
                      const isSelected = selectedIface === iface;
                      const rawName = iface.file_name || iface.url || `interfaz-${idx + 1}`;
                      const hasExt = rawName.includes('.') && !rawName.startsWith('http');
                      const ext = hasExt ? rawName.split('.').pop().toLowerCase() : "route";
                      const fileName = iface.name || getInterfaceLabel(iface.url || rawName, iface.name);
                      
                      return (
                        <button
                          key={idx}
                          className={`tab-button ${isSelected ? 'active' : ''}`}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '8px',
                            border: isSelected ? 'none' : '1px solid #d1d5db',
                            background: isSelected ? '#1e293b' : '#fff',
                            cursor: 'pointer',
                            fontWeight: isSelected ? 'bold' : 'normal',
                            color: isSelected ? '#fff' : '#374151',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            whiteSpace: 'nowrap',
                            transition: 'all 0.2s'
                          }}
                          onClick={() => setSelectedIface(iface)}
                        >
                          <TypeBadge type={ext} />
                          {fileName}
                        </button>
                      );
                    })}
                  </div>
                  <button 
                    className="tabs-scroll-btn" 
                    onClick={() => tabsRef.current?.scrollBy({ left: 200, behavior: "smooth" })}
                    title="Desplazar a la derecha"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0 8px', fontSize: '18px', color: '#64748b' }}
                  >
                    &#8594;
                  </button>
                </div>
              </section>
            )}

            {/* ── Toolbar ─────────────────────────── */}
            <div className="capture-toolbar">
              <div className="device-tabs">
                <button className={`device-tab ${activeTab === "Todas" ? "active" : ""}`} onClick={() => setActiveTab("Todas")}>
                  <AllIcon /> Todas
                </button>
                <button className={`device-tab ${activeTab === "Desktop" ? "active" : ""}`} onClick={() => setActiveTab("Desktop")}>
                  <DesktopIcon /> Desktop
                </button>
                <button className={`device-tab ${activeTab === "Tablet" ? "active" : ""}`} onClick={() => setActiveTab("Tablet")}>
                  <TabletIcon /> Tablet
                </button>
                <button className={`device-tab ${activeTab === "Mobile" ? "active" : ""}`} onClick={() => setActiveTab("Mobile")}>
                  <MobileIcon /> Mobile
                </button>
              </div>
              
            </div>

            {/* ── Captures grid ───────────────────────────── */}
            {filteredCaptures.length > 0 ? (
              <div className="capture-grid">
                {filteredCaptures.map((item, index) => {
                  const desc = getDeviceDesc(item.device);
                  const isError = item.error;
                  return (
                    <article className="capture-card" key={index}>
                      <div className="capture-card-header">
                        <div className="capture-card-title">
                          {getDeviceIcon(item.device)}
                          <div>
                            <h3>{getDeviceName(item.device)}</h3>
                            <p>{item.width ? `${item.width} x ${item.height}` : getDeviceRes(item.device)}</p>
                          </div>
                        </div>
                        <span className="status-badge" style={isError ? {background: '#fef2f2', color: '#ef4444'} : {}}>
                          {isError ? "Error" : "OK"}
                        </span>
                      </div>

                      <div className="browser-frame">
                        <div className="browser-header">
                          <div className="browser-dots">
                            <div className="browser-dot red"></div>
                            <div className="browser-dot yellow"></div>
                            <div className="browser-dot green"></div>
                          </div>
                          <div className="browser-url-bar">
                            <LockIcon /> {url} <RefreshIcon />
                          </div>
                        </div>
                        <div className={`browser-content ${item.device}`}>
                          {!isError && getImageSource(item) ? (
                            <img src={getImageSource(item)} alt={`Captura ${item.device}`} />
                          ) : (
                            <div style={{padding: '20px', textAlign: 'center', color: '#94a3b8', fontSize: '12px'}}>
                              {isError ? item.error : "Sin imagen"}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="capture-info-box">
                        <ShieldIcon />
                        <div className="capture-info-text">
                          <strong>{desc.title}</strong>
                          <p>{desc.text}</p>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                No se encontraron capturas para este filtro.
              </div>
            )}

            {/* ── Actions ─────────────────────────────────── */}
            <div className="capture-page-actions">
              <button className="btn-volver" onClick={goBack}>Volver</button>
              <button className="btn-continuar" onClick={continueToHtml}>Continuar a Réplica</button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}