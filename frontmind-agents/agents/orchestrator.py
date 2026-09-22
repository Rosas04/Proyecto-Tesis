import json
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importar nuestras herramientas personalizadas
from agents.tools.auth_tool import autenticar_sistema
from agents.tools.visual_discovery_tool import rastrear_interfaces_visualmente
from agents.tools.capture_tool import capturar_interfaz

def ejecutar_flujo_completo(task_id: str, url_login: str, url_dashboard: str, usuario: str, contrasena: str, open_ai_key: str):
    """
    Orquesta el flujo: Autenticación -> Rastreo Visual -> Captura.
    Usa el motor de LangChain con llamadas a funciones OpenAI.
    """
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=open_ai_key)
    tools = [autenticar_sistema, rastrear_interfaces_visualmente, capturar_interfaz]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres el Orquestador Principal de FrontMind AI. 
        Tu objetivo es documentar visualmente una aplicación privada. Sigue ESTRICTAMENTE este orden:
        
        1. Llama a 'autenticar_sistema' con las credenciales provistas para generar el estado de sesión.
        2. Llama a 'rastrear_interfaces_visualmente' para descubrir rutas internas como un humano, evadiendo botones de logout.
        3. Analiza las rutas descubiertas. Por cada ruta, llama a 'capturar_interfaz' iterativamente para tomar capturas responsivas.
        
        Responde al final con un resumen de todo el trabajo realizado.
        """),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    instruccion = f"""
    Evalúa el sistema para la tarea {task_id}. 
    URL Login: {url_login}
    Usuario: {usuario}
    Contraseña: {contrasena}
    URL Inicial tras Login: {url_dashboard}
    """
    
    resultado = agent_executor.invoke({"input": instruccion})
    return resultado["output"]
