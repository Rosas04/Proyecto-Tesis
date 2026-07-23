import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Register.css";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

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

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("El formato del correo electrónico es inválido.");
      return;
    }

    if (password.includes(" ")) {
      setError("La contraseña no debe contener espacios en blanco.");
      return;
    }

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setLoading(true);

      // Verificación profunda con Abstract API
      try {
        const apiKey = "3d9886d76ee943e88062f6f57efec810";
        const res = await fetch(`https://emailreputation.abstractapi.com/v1/?api_key=${apiKey}&email=${email.trim()}`);
        if (res.ok) {
          const apiData = await res.json();
          const status = apiData.deliverability || apiData.email_deliverability?.status || "";
          const isMxValid = apiData.is_mx_found?.value ?? apiData.email_deliverability?.is_mx_valid;
          
          // Si el estado no es estrictamente 'deliverable' o el MX es inválido, lo rechazamos.
          if (isMxValid === false || status.toLowerCase() === "undeliverable" || status.toLowerCase() === "unknown" || status.toLowerCase() === "risky") {
            setError(`El correo no parece ser válido o seguro (Estado: ${status}). Intente con otro.`);
            setLoading(false);
            return;
          }
        } else {
          console.error("Error de la API:", res.status);
          setError("Servicio de verificación de correos inactivo (Error " + res.status + "). Intente más tarde.");
          setLoading(false);
          return;
        }
      } catch (apiErr) {
        console.error("Fallo al conectar con Abstract API:", apiErr);
        setError("Fallo de conexión al verificar el correo (posible bloqueo por AdBlocker o CORS). Revise la consola (F12).");
        setLoading(false);
        return;
      }

      const { data, error: registerError } = await register(email, password);

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
    } catch (err) {
      setError("No se pudo crear la cuenta. Intente nuevamente.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">FM</div>
          <h1>FrontMind AI</h1>
          <p>Framework agéntico de evaluación frontend</p>
        </div>

        <form onSubmit={handleRegister}>
          <h2>Crear cuenta</h2>

          <label>Correo electrónico</label>
          <input
            type="email"
            placeholder="correo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Contraseña</label>
          <input
            type="password"
            placeholder="Mínimo 6 caracteres"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>Confirmar contraseña</label>
          <input
            type="password"
            placeholder="Repita su contraseña"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Creando cuenta..." : "Crear cuenta"}
          </button>

          <p className="auth-link">
            ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
          </p>
        </form>
      </section>
    </main>
  );
}