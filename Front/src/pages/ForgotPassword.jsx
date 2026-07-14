import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css"; // Reuse the same styles

export default function ForgotPassword() {
  const { resetPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const handleReset = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    if (!email.trim()) {
      setError("Ingrese su correo electrónico.");
      return;
    }

    try {
      setLoading(true);
      // Supabase needs the URL to redirect back to. We can point to the new reset page.
      const redirectUrl = `${window.location.origin}/reset-password`;
      const { error } = await resetPassword(email, redirectUrl);

      if (error) {
        setError(error.message || "Error al enviar el correo.");
        return;
      }

      setMessage("Se ha enviado un enlace de recuperación a su correo.");
    } catch (err) {
      setError("No se pudo solicitar la recuperación.");
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
          <p>Recuperar contraseña</p>
        </div>

        <form onSubmit={handleReset}>
          <h2>Ingresa tu correo</h2>
          <p style={{marginBottom: "1rem", color: "var(--text-dim)"}}>
            Te enviaremos un enlace para restablecer tu contraseña.
          </p>

          <label>Correo electrónico</label>
          <input
            type="email"
            placeholder="correo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          {error && <div className="auth-error">{error}</div>}
          {message && <div style={{ color: "var(--color-primary)", marginBottom: "1rem", fontSize: "0.9rem" }}>{message}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Enviando..." : "Enviar enlace"}
          </button>

          <p className="auth-link" style={{ marginTop: "1rem" }}>
            <Link to="/login">Volver al inicio de sesión</Link>
          </p>
        </form>
      </section>
    </main>
  );
}
