import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Ingrese correo y contraseña.");
      return;
    }

    try {
      setLoading(true);

      const { error } = await login(email, password);

      if (error) {
        setError("Correo o contraseña incorrectos.");
        return;
      }

      navigate("/input");
    } catch (err) {
      setError("No se pudo iniciar sesión.");
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

        <form onSubmit={handleLogin}>
          <h2>Iniciar sesión</h2>

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
            placeholder="Ingrese su contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>

          <p className="auth-link">
            ¿Olvidaste tu contraseña? <Link to="/forgot-password">Recuperarla</Link>
          </p>

          <p className="auth-link">
            ¿No tienes cuenta? <Link to="/register">Crear cuenta</Link>
          </p>
        </form>
      </section>
    </main>
  );
}