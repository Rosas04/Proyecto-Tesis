import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import TermsModal, { TERMS_VERSION } from "../components/TermsModal";
import AuthLayout, { EyeIcon, LockIcon, MailIcon } from "../components/AuthLayout";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [showTerms, setShowTerms] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRegister = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError("Complete todos los campos para crear su cuenta.");
      return;
    }

    if (!acceptedTerms) {
      setError("Debe aceptar los términos y condiciones para crear su cuenta.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("El formato del correo electrónico es inválido.");
      return;
    }

    if (password.includes(" ")) {
      setError("La contraseña no debe contener espacios en blanco.");
      return;
    }

    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setLoading(true);

      // Verificación de email vía nuestro propio Backend (CRIT-03)
      try {
        const { verifyEmail } = await import("../services/api");
        const verifyData = await verifyEmail(email.trim());

        // Sólo se bloquea ante un veredicto negativo; "UNKNOWN" no impide el registro
        if (!["DELIVERABLE", "UNKNOWN"].includes(verifyData.deliverability)) {
          setError(`El correo no parece ser válido o seguro (Estado: ${verifyData.deliverability}). Intente con otro.`);
          setLoading(false);
          return;
        }
      } catch (apiErr) {
        const message = apiErr?.message || "";
        // Exceso de intentos: se respeta el bloqueo
        if (message.startsWith("Demasiadas")) {
          setError(message);
          setLoading(false);
          return;
        }
        // Servicio de verificación no disponible/no configurado: se continúa,
        // Supabase igualmente exige confirmar el correo por enlace.
        console.warn("Verificación de correo no disponible; se continúa con el registro.", apiErr);
      }

      const { data, error: registerError } = await register(email, password, {
        accepted_terms: true,
        accepted_terms_version: TERMS_VERSION,
        accepted_terms_at: new Date().toISOString(),
      });

      if (registerError) {
        const errorMsg = registerError.message || "";
        if (errorMsg === "{}" || !errorMsg) {
          setError("No se pudo enviar el correo de verificación. Es posible que el correo no exista o haya sido rechazado por el servidor.");
        } else if (errorMsg.toLowerCase().includes("already registered")) {
          setError("Este correo ya está registrado. Intente iniciar sesión.");
        } else if (errorMsg.toLowerCase().includes("rate limit")) {
          setError("Se ha superado el límite de registros. Por favor, intente más tarde.");
        } else {
          setError(errorMsg || "No se pudo crear la cuenta.");
        }
        return;
      }

      // Si Supabase ya entrega una sesión activa (confirmación de email
      // desactivada), el usuario puede continuar directamente al sistema.
      if (data?.session) {
        navigate("/input");
        return;
      }

      // Si Supabase requiere confirmación de correo, no hay sesión todavía.
      setSuccess(
        "Cuenta creada correctamente. Revise su correo para confirmar la cuenta y luego inicie sesión."
      );
      setEmail("");
      setPassword("");
      setConfirmPassword("");
      setAcceptedTerms(false);
    } catch {
      setError("No se pudo crear la cuenta. Intente nuevamente.");
      
    } finally {
      setLoading(false);
    }
  };

  const eyeButton = (
    <button type="button" className="split-eye"
      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
      onClick={() => setShowPassword((v) => !v)}>
      <EyeIcon off={showPassword} />
    </button>
  );

  return (
    <AuthLayout
      title="Crear cuenta"
      subtitle="Regístrate para empezar a evaluar y mejorar tu frontend con IA."
    >
      <form className="split-form" onSubmit={handleRegister}>
        <label htmlFor="reg-email">Correo electrónico</label>
        <div className="split-field">
          <MailIcon />
          <input id="reg-email" type="email"
            placeholder="correo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <label htmlFor="reg-password">Contraseña</label>
        <div className="split-field">
          <LockIcon />
          <input id="reg-password" type={showPassword ? "text" : "password"}
            placeholder="Mínimo 8 caracteres"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {eyeButton}
        </div>

        <label htmlFor="reg-confirm">Confirmar contraseña</label>
        <div className="split-field">
          <LockIcon />
          <input id="reg-confirm" type={showPassword ? "text" : "password"}
            placeholder="Repita su contraseña"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        <label className="split-check">
          <input type="checkbox"
            checked={acceptedTerms}
            onChange={(e) => setAcceptedTerms(e.target.checked)}
          />
          <span>
            He leído y acepto los{" "}
            <button type="button" className="split-textlink" onClick={() => setShowTerms(true)}>
              términos y condiciones
            </button>
            , incluido el almacenamiento de mis datos en la nube.
          </span>
        </label>

        {error && <div className="split-error">{error}</div>}
        {success && <div className="split-success">{success}</div>}

        <button type="submit" className="split-submit" disabled={loading || !acceptedTerms}>
          {loading ? "Creando cuenta..." : "Crear cuenta →"}
        </button>

        <p className="split-link">
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </form>

      {showTerms && (
        <TermsModal
          onClose={() => setShowTerms(false)}
          onAccept={() => { setAcceptedTerms(true); setShowTerms(false); }}
        />
      )}
    </AuthLayout>
  );
}
