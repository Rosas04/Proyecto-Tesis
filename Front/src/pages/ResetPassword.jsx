import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logoImgWebp from "../assets/logo.webp";
import logoImgPng from "../assets/logo.png";
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
    
    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
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
    } catch {
      setError("No se pudo actualizar la contraseña.");
      
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <picture><source srcSet={logoImgWebp} type="image/webp" /><img src={logoImgPng} alt="FrontMind AI" className="auth-logo"  /></picture>
          <h1>FrontMind AI</h1>
          <p>Nueva contraseña</p>
        </div>

        <form onSubmit={handleUpdate}>
          <h2>Restablecer</h2>

          <label>Nueva contraseña</label>
          <input
            type="password"
            placeholder="Mínimo 8 caracteres"
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
