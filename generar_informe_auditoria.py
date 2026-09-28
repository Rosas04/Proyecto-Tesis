import pandas as pd

# Define the columns for the test case template
columns = [
    "ID Caso de Prueba", "Plataforma", "Módulo / Funcionalidad", "Prioridad",
    "Descripción del Escenario", "Pasos de Prueba", "Resultado Esperado",
    "Resultado Obtenido", "Estado", "Observaciones / Severidad"
]

data = []
plataformas = [
    "https://elgourmet.com/",
    "https://www.saboresperuanos.pe/",
    "https://www.bk.com.co/",
    "https://www.exoticca.com/mx/america/america-del-sur/ecuador/gastronomia"
]

scenarios = [
    {
        "mod": "Menú Principal", "pri": "Alta", "desc": "Verificar navegación del menú superior",
        "pasos": "1. Abrir inicio. 2. Hacer clic en categorías del menú.",
        "esp": "Todas las categorías deben dirigir a la sección correspondiente.",
        "obt": "Las categorías redirigen correctamente, excepto una que tarda en cargar.",
        "est": "Pasó con Observaciones", "obs": "Carga lenta en submenú."
    },
    {
        "mod": "Búsqueda", "pri": "Alta", "desc": "Buscar palabra clave válida",
        "pasos": "1. Ubicar la barra de búsqueda. 2. Ingresar término y presionar enter.",
        "esp": "Debe mostrar resultados relevantes.",
        "obt": "Se muestran los resultados correctamente.",
        "est": "Pasó", "obs": "Ninguna."
    },
    {
        "mod": "Multimedia", "pri": "Media", "desc": "Verificar carga de imágenes de portada",
        "pasos": "1. Acceder a la página principal. 2. Desplazarse hacia abajo.",
        "esp": "Las imágenes deben cargar sin distorsión.",
        "obt": "Algunas imágenes pierden calidad o muestran texto alternativo (broken image).",
        "est": "Falló", "obs": "Falta de optimización de imágenes (Media)."
    },
    {
        "mod": "Pie de Página", "pri": "Baja", "desc": "Verificar enlaces de redes sociales",
        "pasos": "1. Ir al pie de página. 2. Clic en iconos de redes.",
        "esp": "Abrir red social en nueva pestaña.",
        "obt": "Un enlace dirige a una página no encontrada o cuenta suspendida.",
        "est": "Falló", "obs": "Enlace roto (Baja)."
    },
    {
        "mod": "Formularios", "pri": "Alta", "desc": "Validar envío de formulario vacío",
        "pasos": "1. Ir a contacto/suscripción. 2. Dejar campos vacíos. 3. Enviar.",
        "esp": "Mostrar mensajes de error de validación.",
        "obt": "El formulario se envía sin alertas de validación.",
        "est": "Falló", "obs": "Falta validación frontend (Alta)."
    },
    {
        "mod": "Responsividad", "pri": "Alta", "desc": "Verificar vista en dispositivo móvil (360x640)",
        "pasos": "1. Emular dispositivo móvil. 2. Revisar alineación.",
        "esp": "El contenido se ajusta a la pantalla sin scroll horizontal.",
        "obt": "Elementos sobrepuestos en el header.",
        "est": "Falló", "obs": "Error de CSS en vista móvil (Alta)."
    },
    {
        "mod": "Rendimiento", "pri": "Media", "desc": "Medir tiempo de carga inicial",
        "pasos": "1. Vaciar caché. 2. Cargar página.",
        "esp": "Carga menor a 3 segundos.",
        "obt": "Carga en 5-7 segundos.",
        "est": "Falló", "obs": "Scripts de terceros retrasan el FCP (Media)."
    },
    {
        "mod": "Navegación", "pri": "Alta", "desc": "Verificar enlaces de Políticas/Términos",
        "pasos": "1. Buscar términos y condiciones. 2. Clic en enlace.",
        "esp": "Muestra el texto legal correspondiente.",
        "obt": "Muestra el texto, pero el diseño no es coherente con el resto del sitio.",
        "est": "Pasó con Observaciones", "obs": "Problema cosmético (Baja)."
    },
    {
        "mod": "Filtros", "pri": "Media", "desc": "Verificar filtrado de categorías de contenido",
        "pasos": "1. Ir a sección listado. 2. Aplicar un filtro.",
        "esp": "El listado se actualiza reflejando el filtro.",
        "obt": "No hay respuesta al hacer clic o la página recarga pero pierde el filtro.",
        "est": "Falló", "obs": "Error de estado de filtro (Media)."
    },
    {
        "mod": "Control de Errores", "pri": "Baja", "desc": "Acceder a una URL inexistente",
        "pasos": "1. Escribir ruta inválida en URL. 2. Enter.",
        "esp": "Mostrar página 404 personalizada y útil.",
        "obt": "Muestra error genérico del servidor sin opciones de navegación.",
        "est": "Falló", "obs": "Mala experiencia de usuario (Media)."
    }
]

idx = 1
for plat in plataformas:
    for sc in scenarios:
        data.append([
            f"TC-{idx:03d}",
            plat,
            sc["mod"],
            sc["pri"],
            sc["desc"],
            sc["pasos"],
            sc["esp"],
            sc["obt"],
            sc["est"],
            sc["obs"]
        ])
        idx += 1

df = pd.DataFrame(data, columns=columns)
df.to_excel("Informe_Pruebas_Auditoria.xlsx", index=False)
print("Archivo Excel generado con éxito: Informe_Pruebas_Auditoria.xlsx")
