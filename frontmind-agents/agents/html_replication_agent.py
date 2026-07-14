from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HtmlReplicationAgent:
    def run(self, html_content: str = "", url: str = "", css_cache: dict = None, cssom_styles: list = None):
        if html_content and len(html_content.strip()) > 50:
            replicated = self.build_full_html(html_content, url, css_cache, cssom_styles)
            source = "HTML real enriquecido con estilos"
        else:
            replicated = self.generate_base_html(url)
            source = "HTML replicado base desde evidencia visual"

        return {
            "agent": "HtmlReplicationAgent",
            "status": "completed",
            "source": source,
            "html_replicated": replicated,
            "html_length": len(replicated),
        }

    def build_full_html(self, html_content: str, url: str, css_cache: dict = None, cssom_styles: list = None):
        css_cache = css_cache or {}
        cssom_styles = cssom_styles or []
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else "Interfaz evaluada"

        css_blocks = []
        external_css = []

        for style in soup.find_all("style"):
            css_blocks.append(style.get_text())

        injected_urls = set()

        for link in soup.find_all("link"):
            rel = link.get("rel") or []
            if isinstance(rel, str):
                rel = [rel]
            href = link.get("href")
            as_attr = link.get("as")

            is_css = "stylesheet" in rel or ("preload" in rel and as_attr == "style")

            if href and is_css:
                css_url = urljoin(url, href)
                
                # Check cache first
                css_content = css_cache.get(css_url)
                
                # Fallback to requests if not cached
                if not css_content:
                    css_content = self.fetch_css(css_url)

                if css_content:
                    css_content = self.fix_css_urls(css_content, css_url)
                    external_css.append(f"\n/* CSS externo: {css_url} */\n{css_content}")
                    injected_urls.add(css_url)

        # Inject any remaining CSS from cache that was loaded dynamically
        for css_url, css_content in css_cache.items():
            if css_url not in injected_urls and css_content:
                fixed_content = self.fix_css_urls(css_content, css_url)
                external_css.append(f"\n/* CSS dinamico de red: {css_url} */\n{fixed_content}")
                injected_urls.add(css_url)

        # Inject dynamic styles from CSSOM (CSS-in-JS)
        for i, style_text in enumerate(cssom_styles):
            if style_text and style_text.strip():
                external_css.append(f"\n/* Estilos dinamicos CSSOM #{i+1} */\n{style_text}")

        for tag in soup.find_all(["script", "noscript"]):
            tag.decompose()

        body = soup.body
        body_attrs_str = ""

        if body:
            for k, v in body.attrs.items():
                if isinstance(v, list):
                    v = " ".join(v)
                body_attrs_str += f' {k}="{v}"'
            
            self.convert_relative_paths(body, url)
            body_content = body.decode_contents()
        else:
            self.convert_relative_paths(soup, url)
            body_content = soup.decode_contents()

        final_css = "\n\n".join(external_css + css_blocks)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
    }}

    img {{
      max-width: 100%;
      height: auto;
    }}

    {final_css}
  </style>
</head>
<body{body_attrs_str}>
{body_content}
</body>
</html>"""

    def fetch_css(self, css_url: str):
        try:
            response = requests.get(
                css_url,
                timeout=10,
                verify=False,  # Bypass SSL certificate errors
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
            )

            if response.status_code == 200:
                return response.text

        except Exception:
            return ""

        return ""

    def fix_css_urls(self, css_content: str, css_url: str):
        def replace_url(match):
            raw_url = match.group(1).strip().strip("\"'")

            if raw_url.startswith("data:"):
                return f"url({raw_url})"

            if raw_url.startswith("#"):
                return f"url({raw_url})"

            absolute_url = urljoin(css_url, raw_url)
            return f"url({absolute_url})"

        return re.sub(r"url\((.*?)\)", replace_url, css_content)

    def convert_relative_paths(self, soup, base_url: str):
        attributes = {
            "img": ["src", "srcset"],
            "a": ["href"],
            "link": ["href"],
            "source": ["src", "srcset"],
            "video": ["src", "poster"],
            "audio": ["src"],
        }

        for tag_name, attrs in attributes.items():
            for tag in soup.find_all(tag_name):
                for attr in attrs:
                    value = tag.get(attr)

                    if not value:
                        continue

                    if attr == "srcset":
                        tag[attr] = self.convert_srcset(value, base_url)
                    else:
                        tag[attr] = urljoin(base_url, value)

    def convert_srcset(self, srcset: str, base_url: str):
        parts = []

        for item in srcset.split(","):
            item = item.strip()

            if not item:
                continue

            pieces = item.split()
            src = pieces[0]
            descriptor = " ".join(pieces[1:])
            absolute_url = urljoin(base_url, src)

            if descriptor:
                parts.append(f"{absolute_url} {descriptor}")
            else:
                parts.append(absolute_url)

        return ", ".join(parts)

    def generate_base_html(self, url: str):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Interfaz replicada</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f8fafc;
      color: #111827;
    }}

    header {{
      background: #ffffff;
      border-bottom: 1px solid #e5e7eb;
      padding: 20px 48px;
    }}

    main {{
      padding: 64px 48px;
    }}

    section {{
      max-width: 960px;
      margin: auto;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 16px;
      padding: 40px;
    }}

    h1 {{
      margin-top: 0;
      font-size: 36px;
    }}

    p {{
      color: #4b5563;
      line-height: 1.6;
    }}

    button {{
      background: #2563eb;
      color: white;
      border: none;
      padding: 14px 22px;
      border-radius: 8px;
      font-weight: bold;
      cursor: pointer;
    }}

    footer {{
      padding: 24px 48px;
      color: #6b7280;
      font-size: 14px;
    }}
  </style>
</head>
<body>
  <header>
    <strong>Interfaz replicada</strong>
  </header>

  <main>
    <section>
      <h1>Interfaz replicada desde evidencia visual</h1>
      <p>
        Esta estructura fue generada como representación evaluable para aplicar
        reglas de calidad frontend bajo ISO/IEC 25010.
      </p>
      <button>Acción principal</button>
    </section>
  </main>

  <footer>
    <p>Fuente evaluada: {url}</p>
  </footer>
</body>
</html>"""