import { createClient } from "@supabase/supabase-js";

// URL y clave publishable del proyecto actual (valores públicos por diseño).
const DEFAULT_URL = "https://xivbtmxybnvolkfqzood.supabase.co";
const DEFAULT_KEY = "sb_publishable_Uw5SSw9xr_O9-44NoQ-R_g_qUW1RJ5o";
// Proyectos anteriores (pausados): si el entorno aún los trae, se usa el actual.
const DEAD_REFS = ["eytmbhfdjccvxmpjvidq", "lpdwuzmhybjxjtsggdnn"];

const envUrl = import.meta.env.VITE_SUPABASE_URL;
const stale = !envUrl || DEAD_REFS.some((ref) => envUrl.includes(ref));
const supabaseUrl = stale ? DEFAULT_URL : envUrl;
const supabaseKey = stale ? DEFAULT_KEY : import.meta.env.VITE_SUPABASE_ANON_KEY || DEFAULT_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error(
    "Faltan las variables de entorno VITE_SUPABASE_URL o VITE_SUPABASE_ANON_KEY. " +
    "Asegúrese de configurar el archivo .env o las variables en producción."
  );
}

export const supabase = createClient(supabaseUrl, supabaseKey);