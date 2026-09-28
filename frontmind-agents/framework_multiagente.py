import asyncio
import json
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. ESQUEMAS DE SALIDA ESTRUCTURADA (JSON SCHEMA)
# ---------------------------------------------------------------------------

class Hallazgo(BaseModel):
    id_hallazgo: str = Field(description="ID único del hallazgo, ej. WCAG-001, DOM-002")
    caracteristica_iso: str = Field(description="Característica ISO/IEC 25010 afectada")
    subcaracteristica_iso: str = Field(description="Subcaracterística ISO/IEC 25010")
    criterio_referencia: str = Field(description="Criterio WCAG 2.1 o regla técnica incumplida")
    selector_css: str = Field(description="Selector CSS o elemento HTML afectado")
    descripcion_error: str = Field(description="Descripción técnica detallada del defecto")
    linea_o_snippet: str = Field(description="Fragmento de código donde ocurre el fallo")
    sugerencia_remediacion: str = Field(description="Solución técnica sugerida")

class ReporteAgenteEspecialista(BaseModel):
    agente_emisor: str
    hallazgos: list[Hallazgo]
    observaciones_generales: str

class ReporteFinalISO(BaseModel):
    resumen_ejecutivo: str
    total_defectos_validados: int
    cobertura_normativa_pct: float
    hallazgos_confirmados: list[Hallazgo]
    puntuacion_calidad_iso: dict[str, float]  # Puntuación 0-100 por característica

# ---------------------------------------------------------------------------
# 2. DEFINICIÓN DEL FRAMEWORK MULTIAGENTE
# ---------------------------------------------------------------------------

class FrameworkMultiagenteISO:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
        # System Prompts asignados
        self.prompt_dom = """Eres el "Agente Inspector DOM y Estructura", un experto en arquitectura Frontend y estándares W3C.
Tu función es analizar el código fuente HTML/CSS/DOM de una interfaz web e identificar defectos estructurales y de mantenibilidad según la norma ISO/IEC 25010 (subcaracterísticas: Modularidad, Analizabilidad y Reusabilidad).

INSTRUCCIONES DE AUDITORÍA:
1. Analiza la jerarquía de etiquetas HTML y verifica el uso correcto de etiquetas semánticas (<header>, <nav>, <main>, <section>, <article>, <footer>).
2. Detecta la presencia de 'DOM sobrecargado' (anidación excesiva de divs sin sentido semántico).
3. Identifica el uso de manipulación directa e imperativa del DOM o presencia de atributos inline innecesarios.
4. Evalúa la estructura de componentes y la limpieza de clases CSS/Tailwind.

Regla estricta: Limítate a reportar fallas reales sustentadas en el código fuente proporcionado. No inventes elementos ni supongas comportamiento dinámico no presente. Responde únicamente en el formato JSON especificado."""

        self.prompt_wcag = """Eres el "Agente Auditor de Accesibilidad WCAG", especialista en las pautas W3C/WCAG 2.1 (Niveles A y AA) y el atributo de Capacidad de Interacción (ISO/IEC 25010).
Tu objetivo es examinar el código frontend e identificar barreras de accesibilidad para usuarios con discapacidad o tecnologías de asistencia.

INSTRUCCIONES DE AUDITORÍA:
1. Principio Perceptible: Verifica etiquetas , contraste de color implícito, presencia de atributos ARIA (aria-label, aria-expanded) y subtítulos/textos alternativos.
2. Principio Operable: Evalúa la navegación por teclado (tabindex, focus visible), la presencia de enlaces con textos descriptivos ("click aquí" es un defecto) y la detección de elementos interactivos (<button> vs <div onClick>).
3. Principio comprensible: verifica etiquetas <label> asociadas correctamente a inputs de formulario (id/for) y atributis 'lang' en el documento.
4. Principio robusto: comprueba la validez de IDs unicos y uso correcto de roles ARI.

Para cada hallazgo, especifica el selector CSS afectado, el criterio WCAG 2.1 incumplido (ej. 1.1.1, 2.4.4) y la recomendación técnica de solución."""

        self.prompt_operabilidad = """Eres el "Agente Evaluador de Operabilidad y Protección contra Errores", enfocado en las subcaracterísticas de Operabilidad, Protección frente a errores de usuario y Adecuación Funcional de la norma ISO/IEC 25010.

INSTRUCCIONES DE AUDITORÍA:
1. Protección contra Errores: Verifica la presencia de validaciones en formularios (atributos HTML5 como required, pattern, type, min/max) y la existencia de mensajes de feedback/error visibles y claros.
2. Facilidad de Uso y Consistencia: Identifica elementos interactivos engañosos, botones de acción sin estado disabled durante el procesamiento o falta de confirmaciones para acciones destructivas (ej. eliminar).
3. Reconocibilidad de Adecuación: Evalúa si los controles visuales (placeholders, tooltips, iconos) indican claramente la función de cada módulo.

Genera un reporte objetivo basado exclusivamente en la estructura del código entregado."""

        self.prompt_sintetizador = """Eres el "Agente Sintetizador e Inspector de Calidad ISO/IEC 25010". Tu función es recibir los reportes individuales generados por los agentes especializados (DOM, WCAG y Operabilidad), realizar una verificación cruzada contra el código fuente real y consolidar el Informe Técnico Final de Calidad.

INSTRUCCIONES DE SÍNTESIS Y FILTRADO:
1. Verificación Cruzada (Eliminación de Alucinaciones): Para cada hallazgo reportado por los agentes previos, verifica si el selector CSS y el código mostrado existen realmente en el código fuente de la interfaz. Descarta cualquier hallazgo inexistente o Falso Positivo.
2. Deduplicación: Si dos agentes reportaron el mismo error bajo distinta métrica, unifícalos en un solo hallazgo cruzado.
3. Mapeo ISO/IEC 25010: Clasifica cada hallazgo validado dentro de la característica y subcaracterística correspondiente de la norma ISO/IEC 25010 (Adecuación Funcional, Capacidad de Interacción, Mantenibilidad, etc.).
4. Cálculo de Métricas: Determina el índice de calidad porcentual por subcaracterística y genera las sugerencias de remediación consolidadas."""

    async def _invocar_agente(self, model_name: str, system_prompt: str, prompt_usuario: str, response_schema):
        """Método auxiliar para llamadas asíncronas a Gemini API"""
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=model_name,
            contents=prompt_usuario,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1 # Baja temperatura para máxima consistencia y cero alucinación
            )
        )
        return json.loads(response.text)

    async def evaluar_interfaz_frontend(self, codigo_frontend_html_css: str) -> dict:
        """
        Ejecuta la evaluación multiagente paralela + sintesis cruzada
        """
        print("🚀 Iniciando evaluación técnica multiagente...")
        prompt_input = f"Código Frontend a evaluar:\n```html\n{codigo_frontend_html_css}\n```"

        # PASO 1: Ejecución Asíncrona Paralela de Agentes Especialistas
        # Gemini 1.5 Flash para tareas de parser DOM / Gemini 1.5 Pro para razonamiento complejo
        tarea_dom = self._invocar_agente(
            'gemini-1.5-flash', self.prompt_dom, prompt_input, ReporteAgenteEspecialista
        )
        tarea_wcag = self._invocar_agente(
            'gemini-1.5-pro', self.prompt_wcag, prompt_input, ReporteAgenteEspecialista
        )
        tarea_operabilidad = self._invocar_agente(
            'gemini-1.5-pro', self.prompt_operabilidad, prompt_input, ReporteAgenteEspecialista
        )

        # Esperar la finalización simultánea de los 3 agentes
        res_dom, res_wcag, res_oper = await asyncio.gather(tarea_dom, tarea_wcag, tarea_operabilidad)
        print("✅ Agentes especialistas han completado la inspección.")

        # PASO 2: Sintetización y Verificación Cruzada (Agente Sintetizador ISO)
        prompt_sintesis = f"""
        Código Frontend Original:
        ```html
        {codigo_frontend_html_css}
        ```
        
        Reportes Recibidos de los Agentes Especialistas:
        - Reporte DOM: {json.dumps(res_dom)}
        - Reporte WCAG: {json.dumps(res_wcag)}
        - Reporte Operabilidad: {json.dumps(res_oper)}
        
        Realiza la verificación cruzada, elimina falsos positivos/alucinaciones y genera el ReporteFinalISO.
        """

        reporte_final = await self._invocar_agente(
            'gemini-1.5-pro', self.prompt_sintetizador, prompt_sintesis, ReporteFinalISO
        )
        print("🎯 Sintetizador ISO ha completado la verificación cruzada.")

        return reporte_final

# ---------------------------------------------------------------------------
# 3. EJEMPLO DE EJECUCIÓN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    API_KEY_GEMINI = "TU_API_KEY_AQUÍ"
    
    # Fragmento HTML/CSS de prueba
    codigo_prueba = """
    <div>
        <span>Usuario:</span>
        <input type="text" />
        <div onClick="submitForm()">Enviar</div>
    </div>
    """
    
    framework = FrameworkMultiagenteISO(api_key=API_KEY_GEMINI)
    # Ejecutar evento asíncrono
    resultado = asyncio.run(framework.evaluar_interfaz_frontend(codigo_prueba))
    
    # Imprimir reporte formateado
    print("\n" + "="*60)
    print("INFORME FINAL DE CALIDAD ISO/IEC 25010")
    print("="*60)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
