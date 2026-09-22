import json
import logging
import os
from typing import Optional

from playwright.sync_api import Page

logger = logging.getLogger(__name__)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not api_key:
        return None
    try:
        import openai
        if base_url:
            return openai.OpenAI(api_key=api_key, base_url=base_url)
        return openai.OpenAI(api_key=api_key)
    except ImportError:
        logger.warning("openai library is not installed")
        return None

def extract_simplified_dom(page: Page) -> str:
    return page.evaluate("""
        () => {
            function cleanNode(node) {
                if (node.nodeType === Node.TEXT_NODE) {
                    return node.textContent.trim() ? node.textContent.trim() : null;
                }
                if (node.nodeType !== Node.ELEMENT_NODE) return null;
                const tag = node.tagName.toLowerCase();
                if (['script', 'style', 'noscript', 'meta', 'link', 'svg'].includes(tag)) return null;
                const style = window.getComputedStyle(node);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return null;
                const obj = { tag };
                if (node.id) obj.id = node.id;
                if (node.className && typeof node.className === 'string') obj.class = node.className;
                ['type', 'name', 'placeholder', 'value', 'href', 'role', 'aria-label'].forEach(attr => {
                    if (node.hasAttribute(attr)) obj[attr] = node.getAttribute(attr);
                });
                const children = [];
                node.childNodes.forEach(child => {
                    const clean = cleanNode(child);
                    if (clean) children.push(clean);
                });
                if (children.length > 0) obj.children = children;
                if (Object.keys(obj).length === 1 && children.length === 1 && typeof children[0] === 'string') {
                    return children[0];
                }
                return obj;
            }
            return JSON.stringify(cleanNode(document.body));
        }
    """)

def llm_find_login_selectors(page: Page, url: str) -> Optional[dict]:
    client = get_openai_client()
    if not client:
        return None
    try:
        dom_json = extract_simplified_dom(page)
        if len(dom_json) > 30000:
            dom_json = dom_json[:30000] + "..."
            
        prompt = f"""
Analiza este DOM simplificado de la página {url}.
Tu tarea es identificar los selectores CSS precisos para:
1. El campo de nombre de usuario/correo (username_selector)
2. El campo de contraseña (password_selector)
3. El botón de enviar/iniciar sesión (submit_selector)

Devuelve SOLO un JSON con las claves exactas, sin formato markdown:
{{
  "username_selector": "...",
  "password_selector": "...",
  "submit_selector": "..."
}}
Si no puedes identificar alguno, su valor debe ser null.

DOM:
{dom_json}
"""
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "Eres un experto en automatización web QA y selectores Playwright."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error in llm_find_login_selectors: {e}")
        return None

def llm_discover_interactive_elements(page: Page, url: str) -> list[str]:
    client = get_openai_client()
    if not client:
        return []
    try:
        dom_json = extract_simplified_dom(page)
        if len(dom_json) > 40000:
            dom_json = dom_json[:40000] + "..."
            
        prompt = f"""
Analiza este DOM de la página post-login {url}.
Tu tarea es identificar selectores CSS de botones o menús que podrían desplegar navegación, abrir paneles, o enlaces clave del sistema que no sean <a> tags tradicionales. 
Ignora botones destructivos como Logout, Delete, Remove, Cerrar sesión, Pagar, Enviar.

Devuelve SOLO un JSON con una lista de selectores CSS en la clave "selectors":
{{
  "selectors": ["...", "..."]
}}

DOM:
{dom_json}
"""
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "Eres un asistente de web scraping. Devuelve un JSON con selectores CSS."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("selectors", [])
    except Exception as e:
        logger.error(f"Error in llm_discover_interactive_elements: {e}")
        return []
