import { NavLink, useNavigate, useLocation } from "react-router-dom";
import "./Sidebar.css";
import { useAuth } from "../context/AuthContext";
import { useAnalysis } from "../context/AnalysisContext";
import logoImg from "../assets/logo.png";

const steps = [
  {
    path: "/input",
    number: "01",
    title: "Entrada",
    description: "URL o ZIP",
  },
  {
    path: "/capture",
    number: "02",
    title: "Captura",
    description: "Evidencia visual",
  },
  {
    path: "/html",
    number: "03",
    title: "Código",
    description: "Réplica de código",
  },
  {
    path: "/evaluation",
    number: "04",
    title: "Evaluación",
    description: "ISO/IEC 25010",
  },
  {
    path: "/report",
    number: "05",
    title: "Reporte",
    description: "Informe técnico",
  },
];

export default function Sidebar() {
  const { logout, user } = useAuth();
  const { loading } = useAnalysis();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  let currentStepIndex = steps.findIndex((s) => s.path === location.pathname);

  // If the user is not on a step page (e.g. they are on /history)
  // determine the active step based on state/localStorage so they can click to return.
  if (currentStepIndex === -1 && location.pathname !== "/" && location.pathname !== "/history") {
    if (loading) {
      currentStepIndex = 0; // "/input" is the active step while loading
    } else {
      if (localStorage.getItem("htmlToEvaluate")) {
        currentStepIndex = 3; // "/evaluation"
      } else if (localStorage.getItem("htmlReplicaResult")) {
        currentStepIndex = 2; // "/html"
      } else if (localStorage.getItem("captureResult")) {
        currentStepIndex = 1; // "/capture"
      } else if (localStorage.getItem("inputUrl") || localStorage.getItem("inputZip")) {
        currentStepIndex = 0; // "/input"
      }
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <img src={logoImg} alt="FrontMind AI" className="brand-icon" />

        <div>
          <h1>FrontMind AI</h1>
          <p>Framework agéntico</p>
        </div>
      </div>

      <nav className="sidebar-top-nav">
        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive ? "sidebar-link active-home" : "sidebar-link"
          }
        >
          <span className="home-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </span>
          <span className="flow-text">
            <strong>Inicio</strong>
          </span>
        </NavLink>
      </nav>

      <div className="sidebar-section">
        <span>FLUJO DE AUDITORÍA</span>
      </div>

      <div className="sidebar-flow">
        {steps.map((step, index) => {
          let status = "pending";
          if (currentStepIndex !== -1) {
            if (index < currentStepIndex) status = "completed";
            else if (index === currentStepIndex) status = "active";
          }

          const isClickable = status === "active" || status === "completed";

          return (
            <div 
              key={step.path} 
              className={`flow-item ${status === 'active' ? 'active-flow' : ''}`}
              onClick={() => {
                if (isClickable) {
                  navigate(step.path);
                }
              }}
              style={{ cursor: isClickable ? "pointer" : "default" }}
            >
              <span className="flow-step-icon">
                {step.number}
              </span>
              <span className="flow-text">
                <strong>{step.title}</strong>
                <small>{step.description}</small>
              </span>
            </div>
          );
        })}
      </div>

      <div className="sidebar-section">
        <span>CONSULTAS</span>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/history"
          className={({ isActive }) =>
            isActive ? "sidebar-link active-flow" : "sidebar-link"
          }
        >
          <span className="flow-step-icon doc-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </span>

          <span className="flow-text">
            <strong>Historial</strong>
            <small>Análisis anteriores</small>
          </span>
        </NavLink>
      </nav>

      <div className="sidebar-user">
        <div className="user-info-row">
          <div className="mail-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2" ry="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
          </div>
          <div className="user-text">
            <small>Sesión activa</small>
            <strong>{user?.email || "lrosasm@upao.edu.pe"}</strong>
          </div>
        </div>

        <button type="button" onClick={handleLogout}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '8px'}}>
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}