import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { storageService } from "../services/storageService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  useEffect(() => {
    if (!supabase) {
      setLoadingAuth(false);
      return;
    }

    const loadSession = async () => {
      const { data, error } = await supabase.auth.getSession();

      if (!error) {
        setSession(data.session);
        setUser(data.session?.user || null);
      }

      setLoadingAuth(false);
    };

    loadSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (event, currentSession) => {
        // Al cerrar sesión (o expirar el refresh token) se borran los datos
        // del análisis guardados en el navegador.
        if (event === "SIGNED_OUT") storageService.clearAll();
        setSession(currentSession);
        setUser(currentSession?.user || null);
      }
    );

    return () => {
      if (listener?.subscription) {
        listener.subscription.unsubscribe();
      }
    };
  }, []);

  const register = async (email, password, metadata) => {
    if (!supabase) throw new Error("Base de datos (Supabase) no configurada.");
    return await supabase.auth.signUp({
      email,
      password,
      options: metadata ? { data: metadata } : undefined,
    });
  };

  const login = async (email, password) => {
    if (!supabase) throw new Error("Base de datos (Supabase) no configurada.");
    return await supabase.auth.signInWithPassword({
      email,
      password,
    });
  };

  const logout = async () => {
    if (!supabase) return;
    // scope "global": revoca los refresh tokens de todas las sesiones del usuario
    await supabase.auth.signOut({ scope: "global" });
    storageService.clearAll();
    setUser(null);
    setSession(null);
  };

  const resetPassword = async (email, redirectTo) => {
    if (!supabase) throw new Error("Base de datos (Supabase) no configurada.");
    return await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: redirectTo,
    });
  };

  const updatePassword = async (newPassword) => {
    if (!supabase) throw new Error("Base de datos (Supabase) no configurada.");
    return await supabase.auth.updateUser({
      password: newPassword,
    });
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loadingAuth,
        register,
        login,
        logout,
        resetPassword,
        updatePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}