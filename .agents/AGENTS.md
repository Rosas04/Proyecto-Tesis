# Reglas del Espacio de Trabajo: Proyecto-Tesis

## Descripción del Proyecto (FrontMind AI)
Implementar en FrontMind AI un sistema de auditoría integral capaz de procesar aplicaciones públicas y privadas. Para aplicaciones privadas, el sistema deberá autenticarse con credenciales autorizadas, mantener la sesión, descubrir todas las interfaces internas accesibles, capturarlas individualmente en distintas resoluciones, permitir su visualización y selección, generar una réplica HTML independiente por interfaz, ejecutar su evaluación técnica individual y producir un diagnóstico consolidado de la aplicación frontend completa.

El proyecto está compuesto por:

1. **Backend (Python / FastAPI):**
   - Utiliza **Playwright** para la navegación automatizada, web scraping y captura de interfaces (tomando capturas de pantalla responsivas: Escritorio, Tablet, Móvil).
   - Soporta flujos avanzados de autenticación (Formularios, Storage State, MFA/Manual) para poder acceder a interfaces protegidas y realizar extracciones.
   - Todo el servicio está contenerizado mediante **Docker** para su fácil despliegue.

2. **Frontend (React / Vite):**
   - Una aplicación de página única (SPA) construida como sitio estático.
   - Utiliza **Supabase** (para Base de Datos y autenticación de usuarios).

3. **Infraestructura y Despliegue:**
   - Orquestado a través de Render utilizando el archivo `render.yaml`.
   - El Backend corre como un Web Service en Docker, y el Frontend como una aplicación estática conectada al API del Backend.

## Reglas Generales del Proyecto
- **Seguridad primero:** Al manipular Playwright en el backend, se deben manejar las sesiones, credenciales y estados de almacenamiento de manera segura y estricta, cuidando de no exponer contraseñas en logs.
- **Rutas y Crawling Seguro:** Cuando el agente de Playwright descubra enlaces, debe implementar bloqueos y validaciones para evadir rutas destructivas (como `/logout`, `/delete`, etc.).
- **Diseño Moderno (Frontend):** Cualquier interfaz que se trabaje en el Frontend debe tener un diseño premium y responsivo, haciendo uso de mejores prácticas de UX/UI moderno.

# 4.4 Captura completa de aplicaciones privadas con múltiples interfaces

El sistema no debe limitarse a capturar únicamente la pantalla de inicio de sesión, registro o la primera URL proporcionada. Cuando el usuario seleccione la opción **“La aplicación requiere credenciales”**, FrontMind AI deberá utilizar las credenciales proporcionadas para ingresar a la aplicación como un usuario real autorizado y recorrer todas las interfaces internas accesibles desde dicha sesión.

El flujo esperado será:

```text
URL pública o privada
→ Verificación de autenticación
→ Inicio de sesión con correo y contraseña
→ Confirmación de sesión válida
→ Acceso a la página interna inicial
→ Descubrimiento de rutas y vistas internas
→ Captura individual de cada interfaz
→ Visualización en el módulo Captura
→ Selección de interfaz
→ Réplica HTML individual
→ Evaluación ISO/IEC 25010 individual
→ Reporte consolidado del sistema
```

## Comportamiento obligatorio

Cuando la aplicación requiera autenticación, el usuario proporcionará:

```text
URL de la aplicación
URL de login, si es diferente
Correo o nombre de usuario
Contraseña
Selector del campo de usuario
Selector del campo de contraseña
Selector del botón de inicio de sesión
Selector o URL que confirme el acceso correcto
Número máximo de interfaces a recorrer
```

El sistema deberá iniciar sesión de la misma forma en que lo haría un usuario autorizado y mantener la sesión activa durante todo el proceso de descubrimiento y captura.

Después de la autenticación, el agente deberá recorrer todas las vistas internas accesibles mediante:

* enlaces de navegación;
* menú lateral;
* menú superior;
* tarjetas con navegación;
* botones que cambien de ruta sin modificar datos;
* rutas internas de React Router, Vue Router, Angular Router u otros enrutadores;
* enlaces cargados dinámicamente después del inicio de sesión.

No deberá limitarse a la URL inicial ni regresar automáticamente al login.

## Identificación de interfaces

Cada interfaz descubierta deberá registrarse como una unidad independiente con la siguiente estructura:

```json
{
  "interface_id": "dashboard",
  "name": "Dashboard",
  "route": "/dashboard",
  "absolute_url": "https://aplicacion.com/dashboard",
  "page_title": "Panel principal",
  "status": "completed",
  "capture_time_seconds": 3.18,
  "html_length": 28450,
  "dom_metrics": {},
  "captures": []
}
```

El sistema deberá reconocer y diferenciar vistas como:

* Dashboard
* Usuarios
* Reportes
* Configuración
* Perfil
* Productos
* Pedidos
* Formularios
* Calendarios
* Historial
* Administración
* cualquier otra vista interna accesible

No se debe asumir un número fijo de interfaces. El sistema debe descubrirlas dinámicamente hasta alcanzar el límite configurado.

## Descubrimiento de rutas en SPA

Para aplicaciones React, Vue, Angular, Next.js u otras SPA, el sistema deberá capturar rutas aunque la navegación no provoque una recarga completa del navegador.

Debe contemplar:

* enlaces `<a href>`;
* elementos con `role="link"`;
* botones que ejecuten navegación;
* cambios de URL mediante History API;
* rutas obtenidas desde el sidebar;
* rutas presentes en menús desplegables;
* contenido cargado luego de autenticarse.

El agente debe esperar a que el contenido principal de cada vista termine de renderizar antes de capturarla.

Se debe usar una estrategia combinada:

```text
DOM loaded
+ espera de red estable
+ espera del contenedor principal
+ pausa controlada para contenido asíncrono
```

Ejemplo:

```python
page.goto(route_url, wait_until="domcontentloaded")

try:
    page.wait_for_load_state("networkidle", timeout=10000)
except Exception:
    pass

page.locator("#root, main, [role='main']").first.wait_for(
    state="attached",
    timeout=15000
)

page.wait_for_timeout(1200)
```

## Restricciones de seguridad durante la navegación

El agente podrá navegar únicamente por rutas seguras.

Debe excluir:

```text
/logout
/signout
/logoff
/cerrar-sesion
/delete
/remove
/destroy
/eliminar
/download
/export
/payment
/pay
/checkout
/confirm
/admin/delete
```

También debe evitar hacer clic en botones como:

```text
Eliminar
Guardar
Actualizar
Confirmar
Enviar
Pagar
Cerrar sesión
Desactivar
Borrar
```

La exploración deberá priorizar enlaces de navegación y evitar cualquier acción que modifique información.

## Reutilización del mismo contexto autenticado

La sesión no debe recrearse para cada interfaz. Debe utilizarse un único `BrowserContext` autenticado o un `storage_state` común para todas las rutas.

El flujo correcto es:

```text
Login una sola vez
→ guardar sesión temporal
→ visitar interfaz 1
→ visitar interfaz 2
→ visitar interfaz 3
→ ...
→ finalizar análisis
→ eliminar sesión temporal
```

Esto evita que cada captura vuelva a mostrar el login.

## Captura por interfaz

Para cada interfaz descubierta, el sistema debe generar:

```text
1 captura Desktop
1 captura Tablet
1 captura Mobile
1 HTML renderizado
1 conjunto de métricas DOM
1 registro de tiempo
1 estado de captura
```

Si se descubren seis interfaces, el resultado esperado será:

```text
6 interfaces
18 capturas
6 HTML
6 conjuntos de métricas DOM
```

## Visualización en la sección Captura

La página `Capture.jsx` debe mostrar una lista o cuadrícula de interfaces descubiertas.

Ejemplo:

```text
Interfaces encontradas: 6

[Dashboard]
Desktop | Tablet | Mobile
Estado: Completado
Tiempo: 3.1 s

[Usuarios]
Desktop | Tablet | Mobile
Estado: Completado
Tiempo: 2.8 s

[Reportes]
Desktop | Tablet | Mobile
Estado: Completado
Tiempo: 3.5 s
```

Cada tarjeta debe incluir:

* nombre de la interfaz;
* ruta;
* URL;
* título;
* estado;
* tiempo de captura;
* métricas DOM resumidas;
* miniaturas Desktop, Tablet y Mobile;
* botón “Ver interfaz”;
* botón “Seleccionar para réplica”;
* botón “Evaluar interfaz”.

## Selección de interfaz

El usuario debe poder elegir una interfaz específica desde la sección Captura.

Al seleccionarla, el sistema deberá guardar:

```text
selected_interface_id
selected_interface_url
selected_interface_html
selected_interface_metrics
selected_interface_captures
```

Luego, el módulo `HtmlReplica.jsx` deberá utilizar exclusivamente el HTML de esa interfaz, no un HTML combinado de todo el sistema.

## Réplica individual por interfaz

El Agente de Réplica debe procesar cada interfaz como una unidad independiente.

Debe evitar:

* mezclar HTML de Dashboard con Usuarios;
* concatenar estilos incompatibles;
* mezclar distintas rutas;
* construir una sola réplica general de toda la aplicación.

El resultado debe ser:

```text
Dashboard → réplica Dashboard
Usuarios → réplica Usuarios
Reportes → réplica Reportes
```

Cada réplica debe conservar:

* DOM;
* estilos disponibles;
* recursos visuales;
* rutas absolutas;
* semántica;
* contenido principal.

## Evaluación individual y consolidada

Cada interfaz deberá evaluarse individualmente.

Ejemplo:

```text
Dashboard:
Puntaje 82
Hallazgos 14

Usuarios:
Puntaje 76
Hallazgos 21

Reportes:
Puntaje 88
Hallazgos 9
```

Después, el sistema debe calcular un resumen global:

```text
Total de interfaces: 6
Puntaje promedio: 82
Total de hallazgos: 67
Interfaz con menor calidad: Usuarios
Interfaz con mayor calidad: Reportes
```

## Estructura JSON esperada

```json
{
  "agent": "CaptureAgent",
  "status": "completed",
  "source_type": "authenticated_url",
  "authentication_mode": "form",
  "start_url": "https://app.com/login",
  "final_url": "https://app.com/dashboard",
  "routes_discovered": 6,
  "total_interfaces": 6,
  "total_captures": 18,
  "interfaces": [
    {
      "interface_id": "dashboard",
      "name": "Dashboard",
      "route": "/dashboard",
      "url": "https://app.com/dashboard",
      "title": "Panel principal",
      "status": "completed",
      "capture_time_seconds": 3.1,
      "html_content": "<html>...</html>",
      "html_length": 28120,
      "dom_metrics": {
        "total_nodes": 615,
        "buttons": 14,
        "links": 28,
        "inputs": 4,
        "images": 8,
        "forms": 1
      },
      "captures": [
        {
          "device": "desktop",
          "success": true,
          "public_url": "/captures/dashboard_desktop.png"
        },
        {
          "device": "tablet",
          "success": true,
          "public_url": "/captures/dashboard_tablet.png"
        },
        {
          "device": "mobile",
          "success": true,
          "public_url": "/captures/dashboard_mobile.png"
        }
      ]
    }
  ]
}
```

## Criterios de aceptación específicos

La funcionalidad se considerará correcta únicamente si:

1. El usuario puede ingresar URL, correo y contraseña.
2. El agente inicia sesión correctamente.
3. La sesión se mantiene al navegar.
4. No vuelve al login en cada ruta.
5. Descubre más de una interfaz interna.
6. Captura todas las vistas accesibles hasta el límite configurado.
7. Excluye logout y acciones destructivas.
8. Genera tres capturas por interfaz.
9. Guarda un HTML independiente por interfaz.
10. Muestra las interfaces en `Capture.jsx`.
11. Permite seleccionar una interfaz.
12. Replica cada interfaz de manera independiente.
13. Evalúa cada interfaz por separado.
14. Genera un resumen consolidado de la aplicación.
15. No almacena ni expone credenciales.
16. No mezcla el HTML de distintas interfaces.
17. Mantiene funcionando la captura pública y la carga ZIP.

---

> **Instrucción Final**: No consideres terminado el módulo si solo captura login, registro o la primera pantalla posterior al acceso. La implementación debe demostrar con una aplicación de prueba que, tras autenticarse, descubre y captura todas las vistas internas accesibles del sistema, manteniendo una separación completa entre sus HTML, capturas, métricas y evaluaciones.
