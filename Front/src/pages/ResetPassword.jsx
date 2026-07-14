import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Login.css";

export default function ResetPassword() {
  const navigate = useNavigate();
  const { updatePassword } = useAuth();
  
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpdate = async (event) => {
    event.preventDefault();
    setError("");

    if (!password.trim() || !confirmPassword.trim()) {
      setError("Ingrese y confirme su nueva contraseña.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    
    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres.");
      return;
    }

    try {
      setLoading(true);
      const { error } = await updatePassword(password);

      if (error) {
        setError(error.message || "Error al actualizar la contraseña.");
        return;
      }

      // Si tiene éxito, redirigimos a la página de inicio (o login)
      navigate("/input");
    } catch (err) {
      setError("No se pudo actualizar la contraseña.");
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
          <p>Crear nueva contraseña</p>
        </div>

        <form onSubmit={handleUpdate}>
          <h2>Restablecer</h2>

          <label>Nueva contraseña</label>
          <input
            type="password"
            placeholder="Mínimo 6 caracteres"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label>Confirmar contraseña</label>
          <input
            type="password"
            placeholder="Repita la nueva contraseña"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar contraseña"}
          </button>
        </form>
      </section>
    </main>
  );
}
