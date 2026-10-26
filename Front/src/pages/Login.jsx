import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { loginBlockedFor, registerLoginFailure, registerLoginSuccess } from "../utils/loginThrottle";
import AuthLayout, { EyeIcon, LockIcon, MailIcon } from "../components/AuthLayout";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Ingrese correo y contraseña.");
      return;
    }

    const blockedFor = loginBlockedFor();
    if (blockedFor > 0) {
      setError(`Demasiados intentos fallidos. Espere ${blockedFor} segundos e intente nuevamente.`);
      return;
    }

    try {
      setLoading(true);

      const { error } = await login(email, password);

      if (error) {
        // status 0 / "Failed to fetch": el servidor de autenticación no es alcanzable
        if (error.status === 0 || /fetch/i.test(error.message || "")) {
          setError("No se pudo conectar con el servidor de autenticación. Verifique su conexión o la configuración de Supabase.");
          return;
        }
        registerLoginFailure();
        setError(
          error.status === 429
            ? "Demasiados intentos. Intente nuevamente en unos minutos."
            : "Correo o contraseña incorrectos."
        );
        return;
      }

      registerLoginSuccess();
      navigate("/");
    } catch {
      setError("No se pudo iniciar sesión.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Bienvenido de nuevo"
      subtitle="Inicia sesión para continuar mejorando tu frontend con el poder de la IA."
    >
      <form className="split-form" onSubmit={handleLogin}>
        <label htmlFor="login-email">Correo electrónico</label>
        <div className="split-field">
          <MailIcon />
          <input id="login-email" type="email"
            placeholder="correo@ejemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <label htmlFor="login-password">Contraseña</label>
        <div className="split-field">
          <LockIcon />
          <input id="login-password" type={showPassword ? "text" : "password"}
            placeholder="Ingrese su contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="button" className="split-eye"
            aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            onClick={() => setShowPassword((v) => !v)}>
            <EyeIcon off={showPassword} />
          </button>
        </div>

        <div className="split-row">
          <Link to="/forgot-password">¿Olvidaste tu contraseña?</Link>
        </div>

        {error && <div className="split-error">{error}</div>}

        <button type="submit" className="split-submit" disabled={loading}>
          {loading ? "Ingresando..." : "Ingresar →"}
        </button>

        <p className="split-link">
          ¿No tienes cuenta? <Link to="/register">Crear cuenta</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
