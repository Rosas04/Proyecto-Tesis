/**
 * Limitador de intentos de login en el navegador:
 * 5 intentos fallidos por minuto y bloqueo progresivo (60 s, 120 s, 240 s… máx. 1 h).
 *
 * Es una capa de UX/defensa adicional. El límite autoritativo lo aplica
 * Supabase Auth en el servidor (Authentication → Rate Limits).
 */
const KEY = "fm_login_throttle";
const MAX_ATTEMPTS = 5;
const WINDOW_MS = 60_000;
const BASE_BLOCK_MS = 60_000;
const MAX_BLOCK_MS = 3_600_000;

function read() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || { attempts: [], strikes: 0, until: 0 };
  } catch {
    return { attempts: [], strikes: 0, until: 0 };
  }
}

function write(state) {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    // almacenamiento no disponible: el límite de Supabase sigue aplicando
  }
}

/** Segundos restantes de bloqueo (0 si puede intentar). */
export function loginBlockedFor() {
  const { until } = read();
  return Math.max(0, Math.ceil((until - Date.now()) / 1000));
}

export function registerLoginFailure() {
  const now = Date.now();
  const state = read();
  state.attempts = state.attempts.filter((t) => now - t < WINDOW_MS);
  state.attempts.push(now);
  if (state.attempts.length >= MAX_ATTEMPTS) {
    state.strikes += 1;
    state.until = now + Math.min(BASE_BLOCK_MS * 2 ** (state.strikes - 1), MAX_BLOCK_MS);
    state.attempts = [];
  }
  write(state);
}

export function registerLoginSuccess() {
  write({ attempts: [], strikes: 0, until: 0 });
}
