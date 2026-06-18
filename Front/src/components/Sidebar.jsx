import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const steps = [
  {
    path: "/input",
    number: "01",
    title: "Entrada",
    description: "URL, ZIP o código",
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
    title: "HTML",
    description: "Réplica evaluable",
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

      <nav className="sidebar-nav">
        {steps.map((step) => (
          <NavLink
            key={step.path}
            to={step.path}
            className={({ isActive }) =>
              isActive ? "sidebar-link active" : "sidebar-link"
            }
          >
            <span className="step-number">{step.number}</span>

            <span className="step-text">
              <strong>{step.title}</strong>
              <small>{step.description}</small>
            </span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span>ISO/IEC 25010</span>
        <p>Evaluación técnica automatizada de interfaces frontend.</p>
      </div>
    </aside>
  );
}