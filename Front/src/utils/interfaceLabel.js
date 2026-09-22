/**
 * Genera un label legible para una interfaz descubierta.
 *
 * Prioriza el `name` proporcionado por el backend (si existe y no es genérico).
 * Si no hay name útil, intenta inferir uno a partir de la URL.
 */
export const getInterfaceLabel = (url, name) => {
  // If the backend already provided a meaningful name, use it directly
  if (name && name.trim() && name.toLowerCase() !== "home" && name.toLowerCase() !== "general") {
    return name;
  }

  if (!url) return name || "General";

  const lowerUrl = url.toLowerCase();

  // Authentication
  if (lowerUrl.includes('login') || lowerUrl.includes('auth') || lowerUrl.includes('signin')) return "Autenticación";
  // Dashboard
  if (lowerUrl.includes('dashboard') || lowerUrl.includes('panel')) return "Panel Principal";
  // Users / Profile
  if (lowerUrl.includes('profile') || lowerUrl.includes('perfil')) return "Perfil de Usuario";
  if (lowerUrl.includes('users') || lowerUrl.includes('usuarios')) return "Usuarios";
  // Settings
  if (lowerUrl.includes('settings') || lowerUrl.includes('config') || lowerUrl.includes('preferencias')) return "Configuración";
  // Reports
  if (lowerUrl.includes('report') || lowerUrl.includes('reporte') || lowerUrl.includes('analytics')) return "Reportes";
  // Products / Store
  if (lowerUrl.includes('product') || lowerUrl.includes('producto')) return "Productos";
  if (lowerUrl.includes('cart') || lowerUrl.includes('carrito')) return "Carrito";
  if (lowerUrl.includes('checkout')) return "Checkout";
  // Orders
  if (lowerUrl.includes('order') || lowerUrl.includes('pedido')) return "Pedidos";
  // Calendar
  if (lowerUrl.includes('calendar') || lowerUrl.includes('calendario')) return "Calendario";
  // History
  if (lowerUrl.includes('history') || lowerUrl.includes('historial')) return "Historial";
  // Admin
  if (lowerUrl.includes('admin')) return "Administración";
  // Forms
  if (lowerUrl.includes('form') || lowerUrl.includes('formulario')) return "Formularios";
  // Messages / Notifications
  if (lowerUrl.includes('message') || lowerUrl.includes('mensaje') || lowerUrl.includes('inbox')) return "Mensajes";
  if (lowerUrl.includes('notification') || lowerUrl.includes('notificacion')) return "Notificaciones";
  // Search
  if (lowerUrl.includes('search') || lowerUrl.includes('buscar')) return "Búsqueda";
  // Help / Support
  if (lowerUrl.includes('help') || lowerUrl.includes('ayuda') || lowerUrl.includes('support') || lowerUrl.includes('soporte')) return "Ayuda";
  // Error
  if (lowerUrl.includes('error') || lowerUrl.includes('404') || lowerUrl.includes('not-found')) return "Página de Error";

  // Home detection
  const isHome = lowerUrl.endsWith('/') || lowerUrl.endsWith('/home') || lowerUrl.endsWith('/index');
  if (isHome) return "Página de Inicio";

  // Fallback: extract the last path segment and format it
  try {
    const pathname = new URL(url).pathname;
    const lastSegment = pathname.split('/').filter(Boolean).pop();
    if (lastSegment) {
      return lastSegment
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
    }
  } catch {
    // url might not be a valid URL (e.g., a filename)
  }

  return name || "General";
};
