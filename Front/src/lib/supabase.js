import { createClient } from "@supabase/supabase-js";

// URL y clave publishable del proyecto actual (valores públicos por diseño).
const DEFAULT_URL = "https://lpdwuzmhybjxjtsggdnn.supabase.co";
const DEFAULT_KEY = "sb_publishable_KRk1hCm0C_HSuoTXpcK_bg_MFGLjjOI";
// Proyecto anterior (eliminado): si el entorno aún lo trae, se usa el actual.
const DEAD_REF = "eytmbhfdjccvxmpjvidq";

const envUrl = import.meta.env.VITE_SUPABASE_URL;
const stale = !envUrl || envUrl.includes(DEAD_REF);
const supabaseUrl = stale ? DEFAULT_URL : envUrl;
const supabaseKey = stale ? DEFAULT_KEY : import.meta.env.VITE_SUPABASE_ANON_KEY || DEFAULT_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error(
    "Faltan las variables de entorno VITE_SUPABASE_URL o VITE_SUPABASE_ANON_KEY. " +
    "Asegúrese de configurar el archivo .env o las variables en producción."
  );
}

export const supabase = createClient(supabaseUrl, supabaseKey);