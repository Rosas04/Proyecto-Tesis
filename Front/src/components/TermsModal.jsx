import { useEffect } from "react";
import "./TermsModal.css";

// Versión vigente de los términos; se guarda junto con la aceptación del usuario.
export const TERMS_VERSION = "1.0";

export default function TermsModal({ onClose, onAccept }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="terms-overlay" onClick={onClose}>
      <div
        className="terms-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="terms-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="terms-title">Términos y condiciones</h2>
        <p className="terms-version">Versión {TERMS_VERSION}</p>

        <div className="terms-body">
          <h3>1. Datos que se procesan</h3>
          <p>
            Al utilizar FrontMind AI, usted registra su correo electrónico y
            proporciona información para el análisis: capturas de pantalla,
            código HTML/CSS, URL evaluadas y los resultados y reportes generados.
          </p>

          <h3>2. Almacenamiento en la nube</h3>
          <p>
            Toda la información registrada y utilizada en la plataforma se sube
            y almacena en servidores y servicios en la nube de terceros, con el
            fin de procesarla, conservar su historial y mostrársela en sus
            reportes. Usted acepta que sin este almacenamiento en la nube el
            servicio no puede funcionar.
          </p>

          <h3>3. Finalidad</h3>
          <p>
            Los datos se utilizan únicamente para prestar el servicio de
            evaluación de interfaces y, en el contexto académico de este
            proyecto, para su validación y análisis de resultados.
          </p>

          <h3>4. Su responsabilidad</h3>
          <p>
            Usted declara tener derecho a subir el contenido que analiza y se
            compromete a no cargar información confidencial, personal de
            terceros o protegida sin autorización.
          </p>

          <h3>5. Sus derechos</h3>
          <p>
            Puede solicitar el acceso, la rectificación o la eliminación de sus
            datos y de su cuenta en cualquier momento, contactando al
            responsable del proyecto.
          </p>

          <h3>6. Aceptación obligatoria</h3>
          <p>
            La creación de la cuenta requiere aceptar estos términos. Si no los
            acepta, no podrá registrarse ni utilizar la plataforma.
          </p>
        </div>

        <div className="terms-actions">
          <button type="button" className="terms-btn-secondary" onClick={onClose}>
            Cerrar
          </button>
          <button type="button" className="terms-btn-primary" onClick={onAccept}>
            Acepto los términos
          </button>
        </div>
      </div>
    </div>
  );
}
