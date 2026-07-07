import { NavLink, useNavigate, useLocation } from "react-router-dom";
import "./Sidebar.css";
import { useAuth } from "../context/AuthContext";

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
    description: "Réplica de Código",
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
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const currentStepIndex = steps.findIndex((s) => s.path === location.pathname);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">FM</div>

        <div>
          <h1>FrontMind AI</h1>
          <p>Framework agéntico</p>
        </div>
      </div>

      <div className="sidebar-section">
        <span>Flujo de auditoría</span>
      </div>

      <div className="sidebar-flow">
        {steps.map((step, index) => {
          let status = "pending";
          if (currentStepIndex !== -1) {
            if (index < currentStepIndex) status = "completed";
            else if (index === currentStepIndex) status = "active";
          }

          return (
            <div key={step.path} className={`flow-item ${status} ${status === 'active' && step.path === '/report' ? 'no-pulse' : ''}`}>
              <span className="flow-step-icon">
                {status === "completed" ? (
                  "✓"
                ) : status === "active" ? (
                  step.path === "/report" ? "✓" : <span className="spinner-icon">⏳</span>
                ) : (
                  step.number
                )}
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
        <span>Consultas</span>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/history"
          className={({ isActive }) =>
            isActive ? "sidebar-link active" : "sidebar-link"
          }
        >
          <span className="step-number">HS</span>

          <span className="step-text">
            <strong>Historial</strong>
            <small>Análisis anteriores</small>
          </span>
        </NavLink>
      </nav>
      <div className="sidebar-user">
        <small>Sesión activa</small>
        <strong>{user?.email}</strong>

        <button type="button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}