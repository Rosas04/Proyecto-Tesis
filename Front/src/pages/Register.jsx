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

      const { data, error: registerError } = await register(email, password);

      if (registerError) {
        if (registerError.message?.toLowerCase().includes("already registered")) {
          setError("Este correo ya está registrado. Intente iniciar sesión.");
        } else {
          setError(registerError.message || "No se pudo crear la cuenta.");
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