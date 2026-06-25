import re
import zipfile
from pathlib import Path
import shutil

# ────────────────────────────────────────────────────────────────
#  EXTENSION CONFIGURATION
# ────────────────────────────────────────────────────────────────

# All file types that may contain visual/structural content
PAGE_EXTENSIONS = {
    # HTML variants
    ".html", ".htm",
    # React / React-Native
    ".jsx", ".tsx",
    # TypeScript / JavaScript with templates
    ".ts", ".js", ".mjs",
    # Vue.js
    ".vue",
    # Svelte
    ".svelte",
    # Astro
    ".astro",
    # ASP.NET Razor / Blazor
    ".cshtml", ".razor",
    # PHP templates
    ".php", ".phtml",
    # Laravel Blade
    ".blade.php",
    # Ruby / Rails ERB
    ".erb", ".html.erb",
    # Handlebars / Mustache
    ".hbs", ".handlebars", ".mustache",
    # EJS (Embedded JavaScript)
    ".ejs",
    # Pug / Jade
    ".pug", ".jade",
    # Nunjucks / Jinja2
    ".njk", ".jinja", ".jinja2", ".j2",
    # Angular
    ".component.html", ".ng.html",
    # Twig (Symfony/PHP)
    ".twig",
    # Liquid (Shopify / Jekyll)
    ".liquid",
}

# Style files — collected separately and inlined
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less", ".styl"}

# Combined set of all allowed extensions
ALLOWED_EXTENSIONS = PAGE_EXTENSIONS | STYLE_EXTENSIONS

# Directory names to always skip
IGNORED_DIRS = {
    "node_modules", "dist", "venv", ".git", "build",
    "__pycache__", ".next", "coverage", "uploads", "captures",
    "extracted_projects", ".cache", "out", "vendor", "bower_components",
    ".svn", ".hg", "bin", "obj", "packages", ".nuget",
}

# File name fragments that signal non-page files
SKIP_FILE_PATTERNS = {
    "test", "spec", "story", "stories", "mock", "fixture",
    ".d.ts", ".min.", ".map", ".config.", "webpack", "rollup",
    "vite.config", "jest", "babel", "eslint", "prettier",
    "tsconfig", "package", "dockerfile", "docker-compose",
}

# Extensions treated as page/interface files (have visual content worth extracting)
VISUAL_EXTENSIONS = {
    ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro",
    ".cshtml", ".razor", ".php", ".phtml", ".blade.php",
    ".erb", ".html.erb", ".hbs", ".handlebars", ".mustache",
    ".ejs", ".pug", ".jade", ".njk", ".jinja", ".jinja2", ".j2",
    ".twig", ".liquid",
}

# Extensions treated as script files (may contain HTML only if they have template literals)
SCRIPT_EXTENSIONS = {".ts", ".js", ".mjs"}


# ────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ────────────────────────────────────────────────────────────────

def extract_zip_project(zip_file_path: str):
    extract_dir = Path("../extracted_projects_temp").resolve()
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # OPTIMIZATION: Only extract valid frontend files to save disk I/O and time!
            for member in zip_ref.infolist():
                if member.is_dir():
                    continue
                
                parts = Path(member.filename).parts
                if any(d in parts for d in IGNORED_DIRS):
                    continue
                
                ext = _get_extension(Path(member.filename))
                if ext not in ALLOWED_EXTENSIONS:
                    continue
                
                zip_ref.extract(member, extract_dir)
    except zipfile.BadZipFile:
        return {
            "status": "error",
            "message": "El archivo enviado no es un ZIP válido.",
            "total_files": 0,
            "interfaces": [],
            "combined_html": "",
            "project_type": "unknown",
        }

    all_files = _collect_files(extract_dir)

    if not all_files:
        return {
            "status": "error",
            "message": "No se encontraron archivos de código frontend en el ZIP.",
            "total_files": 0,
            "interfaces": [],
            "combined_html": "",
            "project_type": "unknown",
        }

    project_type = _detect_project_type(all_files)

    # Gather all CSS/SCSS/LESS and compile into one combined stylesheet
    style_files = [f for f in all_files.values() if f["extension"] in STYLE_EXTENSIONS]
    combined_css = _build_combined_css(style_files)

    interfaces = _build_interfaces(all_files, combined_css, project_type)
    combined_html = _build_combined_html(interfaces, combined_css, project_type)

    file_list = [
        {
            "file_name": f["file_name"],
            "relative_path": f["relative_path"],
            "extension": f["extension"],
            "size": f["size"],
        }
        for f in all_files.values()
    ]

    return {
        "status": "extracted",
        "message": f"Proyecto '{project_type}' analizado. {len(interfaces)} interfaces detectadas.",
        "total_files": len(all_files),
        "project_type": project_type,
        "interfaces": interfaces,
        "combined_html": combined_html,
        "files": file_list,
        "combined_code": combined_css,  # backwards compat
    }


# ────────────────────────────────────────────────────────────────
#  FILE COLLECTION
# ────────────────────────────────────────────────────────────────

def _collect_files(extract_dir: Path) -> dict:
    all_files = {}

    for file_path in sorted(extract_dir.rglob("*")):
        if not file_path.is_file():
            continue

        # Skip ignored directories
        parts = file_path.parts
        if any(d in parts for d in IGNORED_DIRS):
            continue

        ext = _get_extension(file_path)
        if ext not in ALLOWED_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue

            rel_path = str(file_path.relative_to(extract_dir))

            all_files[rel_path] = {
                "file_name": file_path.name,
                "path": str(file_path),
                "relative_path": rel_path,
                "extension": ext,
                "content": content,
                "size": len(content),
            }
        except Exception:
            pass

    return all_files


def _get_extension(file_path: Path) -> str:
    """Return the meaningful extension, handling multi-part extensions like .blade.php."""
    name = file_path.name.lower()
    for multi_ext in (".blade.php", ".html.erb", ".component.html", ".ng.html"):
        if name.endswith(multi_ext):
            return multi_ext
    return file_path.suffix.lower()


# ────────────────────────────────────────────────────────────────
#  PROJECT TYPE DETECTION
# ────────────────────────────────────────────────────────────────

def _detect_project_type(all_files: dict) -> str:
    extensions = {f["extension"] for f in all_files.values()}
    file_names  = {f["file_name"].lower() for f in all_files.values()}

    if ".vue" in extensions:
        return "vue"
    if ".svelte" in extensions:
        return "svelte"
    if ".astro" in extensions:
        return "astro"
    if ".razor" in extensions or ".cshtml" in extensions:
        return "blazor-razor"
    if ".blade.php" in extensions:
        return "laravel-blade"
    if ".twig" in extensions:
        return "twig"
    if ".tsx" in extensions:
        return "react-tsx"
    if ".jsx" in extensions:
        return "react-jsx"
    if ".erb" in extensions or ".html.erb" in extensions:
        return "rails-erb"
    if ".php" in extensions or ".phtml" in extensions:
        return "php"
    if ".hbs" in extensions or ".handlebars" in extensions or ".mustache" in extensions:
        return "handlebars"
    if ".ejs" in extensions:
        return "ejs"
    if ".pug" in extensions or ".jade" in extensions:
        return "pug"
    if ".njk" in extensions or ".jinja" in extensions or ".jinja2" in extensions:
        return "nunjucks-jinja"
    if ".liquid" in extensions:
        return "liquid"
    if ".html" in extensions or ".htm" in extensions:
        return "vanilla"
    if ".ts" in extensions:
        return "typescript"
    return "mixed"


# ────────────────────────────────────────────────────────────────
#  CSS AGGREGATION
# ────────────────────────────────────────────────────────────────

def _build_combined_css(style_files: list) -> str:
    """Combine all style files into one CSS string (SCSS/LESS: strip non-standard syntax best-effort)."""
    parts = []
    for f in style_files:
        content = f["content"]
        if f["extension"] in (".scss", ".sass"):
            content = _scss_to_css_besteff(content)
        elif f["extension"] == ".less":
            content = _less_to_css_besteff(content)
        parts.append(f"/* === {f['relative_path']} === */\n{content}")
    return "\n\n".join(parts)


def _scss_to_css_besteff(scss: str) -> str:
    """Strip SCSS-specific syntax for best-effort CSS compatibility."""
    # Remove single-line comments
    css = re.sub(r'//.*', '', scss)
    # Remove @use, @forward, @import with quotes (Sass modules)
    css = re.sub(r'@(?:use|forward)\s+[\'"][^\'"]+[\'"]\s*(?:as\s+\*\s*)?;', '', css)
    # Convert $variables to their literal values isn't feasible, just remove declarations
    css = re.sub(r'\$[\w-]+\s*:.*?;', '', css)
    # Remove & nesting markers (keep content)
    css = re.sub(r'&:?:?[\w-]*', '*', css)
    return css


def _less_to_css_besteff(less: str) -> str:
    """Strip LESS-specific syntax."""
    css = re.sub(r'//.*', '', less)
    css = re.sub(r'@[\w-]+\s*:.*?;', '', css)
    return css


# ────────────────────────────────────────────────────────────────
#  INTERFACE BUILDING — DISPATCHER
# ────────────────────────────────────────────────────────────────

def _build_interfaces(all_files: dict, combined_css: str, project_type: str) -> list:
    interfaces = []

    SKIP_DIRS = {"context", "contexts", "routes", "router", "providers", "services", "lib", "utils"}
    ENTRY_POINTS = {"app.jsx", "app.tsx", "main.jsx", "main.tsx", "index.jsx", "index.tsx", "index.js", "index.ts"}

    for rel_path, f in sorted(all_files.items()):
        ext = f["extension"]
        fname_lower = f["file_name"].lower()

        # Skip obvious non-page files
        if any(p in fname_lower for p in SKIP_FILE_PATTERNS):
            continue

        # Skip boilerplate/non-page directories
        parts = Path(rel_path).parts
        if any(d in parts for d in SKIP_DIRS):
            continue

        # Skip SPA index.html
        if fname_lower == "index.html" and project_type != "html":
            continue

        # Skip SPA entry points
        if fname_lower in ENTRY_POINTS and project_type != "html":
            continue

        # Style files are aggregated, not turned into pages
        if ext in STYLE_EXTENSIONS:
            continue

        # Script files: only if they have template literals with HTML
        if ext in SCRIPT_EXTENSIONS:
            html = _build_html_from_script(f["content"], f["file_name"], combined_css)
            if html:
                interfaces.append(_make_iface(f, html, ext.lstrip(".")))
            continue

        # ── Visual page files ──────────────────────────────────
        html = _dispatch_visual(f, combined_css)
        if html:
            interfaces.append(_make_iface(f, html, _type_label(ext)))

    # Fallback: if nothing produced, include raw combined code
    if not interfaces:
        combined_code = "\n\n".join(
            f"<!-- {info['relative_path']} -->\n{info['content']}"
            for info in all_files.values()
            if info["extension"] not in STYLE_EXTENSIONS
        )
        if combined_code.strip():
            interfaces.append({
                "file_name": "Paquete completo",
                "relative_path": "combined",
                "html_content": _wrap_in_html(
                    f"<pre style='padding:16px;white-space:pre-wrap;font-size:12px;'>{combined_code[:30000]}</pre>",
                    "Paquete completo",
                    combined_css,
                ),
                "type": "combined",
                "size": len(combined_code),
            })

    return interfaces


def _make_iface(f: dict, html: str, type_label: str) -> dict:
    return {
        "file_name": f["file_name"],
        "relative_path": f["relative_path"],
        "html_content": html,
        "type": type_label,
        "size": f["size"],
    }


def _type_label(ext: str) -> str:
    mapping = {
        ".html": "html", ".htm": "html",
        ".jsx": "jsx",  ".tsx": "tsx",
        ".vue": "vue",  ".svelte": "svelte", ".astro": "astro",
        ".cshtml": "cshtml", ".razor": "razor",
        ".blade.php": "blade", ".php": "php", ".phtml": "php",
        ".erb": "erb", ".html.erb": "erb",
        ".hbs": "hbs", ".handlebars": "hbs", ".mustache": "mustache",
        ".ejs": "ejs", ".pug": "pug", ".jade": "pug",
        ".njk": "njk", ".jinja": "jinja", ".jinja2": "jinja", ".j2": "jinja",
        ".twig": "twig", ".liquid": "liquid",
        ".ts": "ts", ".js": "js", ".mjs": "js",
    }
    return mapping.get(ext, ext.lstrip("."))


def _dispatch_visual(f: dict, combined_css: str) -> str:
    """Route a visual file to the right converter."""
    ext = f["extension"]
    content = f["content"]
    name = f["file_name"]

    # HTML / HTM
    if ext in (".html", ".htm"):
        if _is_empty_html_shell(content):
            return ""
        return _build_html_from_html_file(content, combined_css)

    # JSX / TSX
    if ext in (".jsx", ".tsx"):
        return _build_html_from_jsx(content, name, combined_css)

    # Vue
    if ext == ".vue":
        return _build_html_from_vue(content, name, combined_css)

    # Svelte
    if ext == ".svelte":
        return _build_html_from_svelte(content, name, combined_css)

    # Astro
    if ext == ".astro":
        return _build_html_from_astro(content, name, combined_css)

    # Razor / Blazor (.cshtml / .razor)
    if ext in (".cshtml", ".razor"):
        return _build_html_from_razor(content, name, combined_css)

    # Blade
    if ext == ".blade.php":
        return _build_html_from_blade(content, name, combined_css)

    # PHP / PHTML
    if ext in (".php", ".phtml"):
        return _build_html_from_php(content, name, combined_css)

    # ERB (Ruby on Rails)
    if ext in (".erb", ".html.erb"):
        return _build_html_from_erb(content, name, combined_css)

    # Handlebars / Mustache
    if ext in (".hbs", ".handlebars", ".mustache"):
        return _build_html_from_handlebars(content, name, combined_css)

    # EJS
    if ext == ".ejs":
        return _build_html_from_ejs(content, name, combined_css)

    # Pug / Jade
    if ext in (".pug", ".jade"):
        return _build_html_from_pug(content, name, combined_css)

    # Nunjucks / Jinja
    if ext in (".njk", ".jinja", ".jinja2", ".j2"):
        return _build_html_from_jinja(content, name, combined_css)

    # Twig
    if ext == ".twig":
        return _build_html_from_twig(content, name, combined_css)

    # Liquid
    if ext == ".liquid":
        return _build_html_from_liquid(content, name, combined_css)

    return ""


# ────────────────────────────────────────────────────────────────
#  CONVERTER FUNCTIONS — one per format
# ────────────────────────────────────────────────────────────────

def _is_empty_html_shell(html: str) -> bool:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style", "meta", "link"]):
            tag.decompose()
        return len(soup.get_text(strip=True)) < 40
    except Exception:
        return False


def _build_html_from_html_file(html: str, combined_css: str) -> str:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "Interfaz"
        inline_styles = "\n".join(s.get_text() for s in soup.find_all("style"))
        body = soup.find("body")
        body_content = body.decode_contents() if body else soup.decode_contents()
        return _wrap_in_html(body_content, title, inline_styles + "\n" + combined_css)
    except Exception:
        return _wrap_in_html(html, "Interfaz", combined_css)


# ── Vue.js ─────────────────────────────────────────────────────
def _build_html_from_vue(content: str, name: str, combined_css: str) -> str:
    # Extract <template> block
    template_match = re.search(r'<template[^>]*>([\s\S]*?)</template>', content, re.IGNORECASE)
    if not template_match:
        return ""
    template_html = template_match.group(1).strip()
    if len(template_html) < 20:
        return ""

    # Extract <style> block
    style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', content, re.IGNORECASE)
    component_css = style_match.group(1) if style_match else ""

    # Convert Vue-specific syntax
    html = _vue_to_html(template_html)
    title = re.sub(r'\.(vue)$', '', name)
    return _wrap_in_html(html, title, combined_css + "\n" + component_css)


def _vue_to_html(vue: str) -> str:
    html = vue
    # Remove Vue event bindings: @click="..." v-on:click="..."
    html = re.sub(r'\s*(?:@|v-on:)[\w.]+\s*=\s*["\'][^"\']*["\']', '', html)
    html = re.sub(r'\s*(?:@|v-on:)[\w.]+\s*=\s*\{[^}]*\}', '', html)
    # v-bind: attr -> attr / :attr -> attr
    html = re.sub(r'\s*:(\w[\w-]*)\s*=\s*["\'][^"\']*["\']', r' \1=""', html)
    html = re.sub(r'\s*v-bind:(\w[\w-]*)\s*=\s*["\'][^"\']*["\']', r' \1=""', html)
    # v-model -> value
    html = re.sub(r'\s*v-model(?:\.[\w]+)*\s*=\s*["\'][^"\']*["\']', ' value=""', html)
    # v-if / v-else / v-show -> keep element, remove directive
    html = re.sub(r'\s*v-(?:if|else-if|else|show)(?:\s*=\s*["\'][^"\']*["\'])?', '', html)
    # v-for -> keep element
    html = re.sub(r'\s*v-for\s*=\s*["\'][^"\']*["\']', '', html)
    # Remove remaining v- directives
    html = re.sub(r'\s*v-[\w-]+(?:\s*=\s*["\'][^"\']*["\'])?', '', html)
    # {{ expression }} -> [dynamic]
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)
    # Custom component tags -> div
    html = re.sub(r'<([A-Z][A-Za-z0-9-]*)[^>]*/>', lambda m: f'<div class="vue-{m.group(1).lower()}"></div>', html)
    html = re.sub(r'<([A-Z][A-Za-z0-9-]*)[^>]*>', lambda m: f'<div class="vue-{m.group(1).lower()}">', html)
    html = re.sub(r'</[A-Z][A-Za-z0-9-]*>', '</div>', html)
    return html


# ── Svelte ────────────────────────────────────────────────────
def _build_html_from_svelte(content: str, name: str, combined_css: str) -> str:
    # Remove <script> blocks
    html = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    # Extract <style> block
    style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', html, re.IGNORECASE)
    component_css = style_match.group(1) if style_match else ""
    html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html, flags=re.IGNORECASE)

    # Convert Svelte-specific syntax
    # {#if ...} / {/if} / {#each ...} / {/each}
    html = re.sub(r'\{#(?:if|each|await)[^}]*\}', '', html)
    html = re.sub(r'\{:(?:else|then|catch)[^}]*\}', '', html)
    html = re.sub(r'\{/(?:if|each|await)\}', '', html)
    # on:event={...}
    html = re.sub(r'\s*on:[\w:]+\s*=\s*\{[^}]*\}', '', html)
    # bind:value={...}
    html = re.sub(r'\s*bind:[\w]+\s*=\s*\{[^}]*\}', ' value=""', html)
    # {expression} -> [dynamic]
    html = re.sub(r'\{[^}]+\}', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.svelte$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css + "\n" + component_css)


# ── Astro ─────────────────────────────────────────────────────
def _build_html_from_astro(content: str, name: str, combined_css: str) -> str:
    # Remove frontmatter (--- ... ---)
    html = re.sub(r'^---[\s\S]*?---\n?', '', content, flags=re.MULTILINE)
    # Remove <style> and <script> blocks
    style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', html, re.IGNORECASE)
    component_css = style_match.group(1) if style_match else ""
    html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    # {expression} -> [dynamic]
    html = re.sub(r'\{[^}]+\}', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.astro$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css + "\n" + component_css)


# ── ASP.NET Razor / Blazor (.cshtml / .razor) ─────────────────
def _build_html_from_razor(content: str, name: str, combined_css: str) -> str:
    html = content
    # Remove Razor code blocks: @{ ... }
    html = re.sub(r'@\{[\s\S]*?\}', '', html)
    # Remove @using / @model / @inject / @page directives
    html = re.sub(r'@(?:using|model|inject|page|layout|section|inherits|addTagHelper|removeTagHelper)[^\n]*\n?', '', html)
    # Remove @functions{} blocks
    html = re.sub(r'@(?:functions|code)\s*\{[\s\S]*?\}', '', html)
    # Razor tag helpers: asp-*, keep element
    html = re.sub(r'\s*asp-[\w-]+\s*=\s*"[^"]*"', '', html)
    # @(...) inline expressions -> [dynamic]
    html = re.sub(r'@\([^)]*\)', '[dynamic]', html)
    # @variable -> [dynamic]
    html = re.sub(r'@[\w.]+(?:\([^)]*\))?', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.(cshtml|razor)$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Laravel Blade ─────────────────────────────────────────────
def _build_html_from_blade(content: str, name: str, combined_css: str) -> str:
    html = content
    # Remove PHP blocks
    html = re.sub(r'<\?php[\s\S]*?\?>', '', html)
    html = re.sub(r'<\?=[\s\S]*?\?>', '[dynamic]', html)
    # Blade directives: @extends, @section, @yield, @include, etc.
    html = re.sub(r'@(?:extends|section|endsection|yield|include|component|slot|endslot|push|endpush|stack|isset|endisset|empty|endempty|auth|endauth|guest|endguest|can|endcan|cannot|endcannot|php|endphp)\s*(?:\([^)]*\))?', '', html)
    # @if / @else / @endif
    html = re.sub(r'@(?:if|elseif|else|endif|foreach|endforeach|for|endfor|while|endwhile|forelse|empty|endforelse)\s*(?:\([^)]*\))?', '', html)
    # {{ expression }} -> [dynamic]
    html = re.sub(r'\{!!\s*[^}]+\s*!!\}', '[dynamic]', html)
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.blade\.php$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── PHP / PHTML ───────────────────────────────────────────────
def _build_html_from_php(content: str, name: str, combined_css: str) -> str:
    html = content
    # Remove PHP blocks
    html = re.sub(r'<\?php[\s\S]*?\?>', '', html)
    html = re.sub(r'<\?=[\s\S]*?\?>', '[dynamic]', html)
    html = re.sub(r'<\?[\s\S]*?\?>', '', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.(php|phtml)$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Ruby ERB ──────────────────────────────────────────────────
def _build_html_from_erb(content: str, name: str, combined_css: str) -> str:
    html = content
    # Remove ERB tags: <% ... %> and <%= ... %>
    html = re.sub(r'<%=\s*[\s\S]*?%>', '[dynamic]', html)
    html = re.sub(r'<%[\s\S]*?%>', '', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.(html\.)?erb$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Handlebars / Mustache ─────────────────────────────────────
def _build_html_from_handlebars(content: str, name: str, combined_css: str) -> str:
    html = content
    # {{{unescaped}}} -> [dynamic]
    html = re.sub(r'\{\{\{[^}]+\}\}\}', '[dynamic]', html)
    # {{#block}} / {{/block}} helpers
    html = re.sub(r'\{\{[#/^!][^}]+\}\}', '', html)
    # {{expression}} -> [dynamic]
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.(hbs|handlebars|mustache)$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── EJS ───────────────────────────────────────────────────────
def _build_html_from_ejs(content: str, name: str, combined_css: str) -> str:
    html = content
    html = re.sub(r'<%=\s*[\s\S]*?%>', '[dynamic]', html)
    html = re.sub(r'<%[\s\S]*?%>', '', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.ejs$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Pug / Jade ───────────────────────────────────────────────
def _build_html_from_pug(content: str, name: str, combined_css: str) -> str:
    """Best-effort Pug → HTML conversion (indentation-based)."""
    lines = content.split('\n')
    html_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//-') or stripped.startswith('//'):
            continue
        # Block statements
        if re.match(r'^(?:if|else|each|for|unless|case|when|default|mixin|include|extends|block)\b', stripped):
            continue
        # Variable declarations
        if stripped.startswith('-') or stripped.startswith('='):
            continue
        # Tag lines: div.class#id(attrs) content
        tag_match = re.match(r'^([a-zA-Z][a-zA-Z0-9-]*)([.#][\w.-]*)?(?:\([^)]*\))?\s*(.*)?$', stripped)
        if tag_match:
            tag = tag_match.group(1)
            text = (tag_match.group(3) or '').strip()
            html_lines.append(f'<{tag}>{text if text else ""}</{tag}>')
        else:
            html_lines.append(stripped)

    body = '\n'.join(html_lines)
    if len(body.strip()) < 20:
        return ""

    title = re.sub(r'\.(pug|jade)$', '', name)
    return _wrap_in_html(body, title, combined_css)


# ── Nunjucks / Jinja2 / J2 ────────────────────────────────────
def _build_html_from_jinja(content: str, name: str, combined_css: str) -> str:
    html = content
    # Remove block tags: {% ... %}
    html = re.sub(r'\{%-?\s*(?:block|endblock|extends|include|import|from|for|endfor|if|elif|else|endif|macro|endmacro|call|endcall|filter|endfilter|set|raw|endraw|with|endwith|trans|endtrans)\b[^%]*-?%\}', '', html)
    html = re.sub(r'\{%-?[^%]*-?%\}', '', html)
    # {{ expression }} -> [dynamic]
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)
    # {# comment #}
    html = re.sub(r'\{#[\s\S]*?#\}', '', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.(njk|jinja2?|j2)$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Twig ──────────────────────────────────────────────────────
def _build_html_from_twig(content: str, name: str, combined_css: str) -> str:
    html = content
    html = re.sub(r'\{%-?\s*[^%]*-?%\}', '', html)
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)
    html = re.sub(r'\{#[\s\S]*?#\}', '', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.twig$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── Liquid ────────────────────────────────────────────────────
def _build_html_from_liquid(content: str, name: str, combined_css: str) -> str:
    html = content
    html = re.sub(r'\{%-?\s*[^%]*-?%\}', '', html)
    html = re.sub(r'\{\{[^}]+\}\}', '[dynamic]', html)

    if len(html.strip()) < 20:
        return ""

    title = re.sub(r'\.liquid$', '', name)
    return _wrap_in_html(html.strip(), title, combined_css)


# ── JSX / TSX ─────────────────────────────────────────────────
def _build_html_from_jsx(jsx_content: str, file_name: str, combined_css: str) -> str:
    jsx_block = _extract_jsx_return(jsx_content)
    if not jsx_block or len(jsx_block.strip()) < 20:
        return ""
    html_body = _jsx_to_html(jsx_block)
    title = re.sub(r'\.(jsx|tsx|js|ts)$', '', file_name)
    return _wrap_in_html(html_body, title, combined_css)


# ── Script files (JS / TS) ────────────────────────────────────
def _build_html_from_script(content: str, file_name: str, combined_css: str) -> str:
    """Extract HTML from template literals in JS/TS files."""
    html_matches = re.findall(r'`([\s\S]*?<[a-zA-Z][\s\S]*?)`', content)
    if not html_matches:
        # Also try JSX return blocks
        return _build_html_from_jsx(content, file_name, combined_css)
    body = "\n".join(html_matches[:5])
    if len(body.strip()) < 30:
        return ""
    title = re.sub(r'\.(ts|js|mjs)$', '', file_name)
    return _wrap_in_html(body, title, combined_css)


# ────────────────────────────────────────────────────────────────
#  JSX EXTRACTION + CONVERSION
# ────────────────────────────────────────────────────────────────

def _extract_jsx_return(code: str) -> str:
    candidates = []
    for match in re.finditer(r'\breturn\s*\(', code):
        start = match.end() - 1
        result = _extract_balanced(code, start, '(', ')')
        if result and '<' in result:
            candidates.append(result)
    for match in re.finditer(r'\breturn\s+(<[A-Za-z])', code):
        start = match.start(1)
        jsx = _extract_single_jsx(code, start)
        if jsx and len(jsx) > 20:
            candidates.append(jsx)
    if not candidates:
        return ""
    return max(candidates, key=len)


def _extract_balanced(code: str, start: int, open_c: str, close_c: str) -> str:
    if start >= len(code) or code[start] != open_c:
        return ""
    depth = 0
    for i in range(start, len(code)):
        if code[i] == open_c:
            depth += 1
        elif code[i] == close_c:
            depth -= 1
            if depth == 0:
                return code[start + 1:i]
    return ""


def _extract_single_jsx(code: str, start: int) -> str:
    m = re.match(r'<([A-Za-z][A-Za-z0-9.]*)', code[start:])
    if not m:
        return code[start:start + 2000]
    tag = m.group(1)
    limit = min(start + 50000, len(code))
    i = start
    while i < limit:
        close = re.search(r'</' + re.escape(tag) + r'\s*>', code[i:])
        if close:
            return code[start:i + close.end()]
        i += 100
    return code[start:start + 5000]


def _jsx_to_html(jsx: str) -> str:
    html = jsx
    html = re.sub(r'\{/\*.*?\*/\}', '', html, flags=re.DOTALL)
    html = html.replace('className=', 'class=')
    html = html.replace('htmlFor=', 'for=')
    html = html.replace('defaultValue=', 'value=')
    html = html.replace('tabIndex=', 'tabindex=')
    html = re.sub(r'\bon[A-Z][a-zA-Z]+\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}', '', html)
    html = re.sub(r'style\s*=\s*\{\{[^}]*\}\}', 'style=""', html, flags=re.DOTALL)
    html = re.sub(r'=\{`([^`]*)`\}', r'="\1"', html)
    html = re.sub(r'=\{"([^"]*)"\}', r'="\1"', html)
    html = re.sub(r"=\{'([^']*)'\}", r"='\1'", html)
    html = re.sub(r'\b(\w[\w-]*)\s*=\s*\{true\}', r'\1', html)
    html = re.sub(r'\b(\w[\w-]*)\s*=\s*\{false\}', '', html)
    html = re.sub(r'=\{[^{}]*\}', '=""', html)
    html = re.sub(r'\{[^{}]+\}', '[…]', html)
    html = re.sub(r'<([A-Z][A-Za-z0-9.]*)[^>]*/\s*>', lambda m: f'<div class="jsx-{m.group(1).lower()}"></div>', html)
    html = re.sub(r'<([A-Z][A-Za-z0-9.]*)[^>]*>', lambda m: f'<div class="jsx-{m.group(1).lower()}">', html)
    html = re.sub(r'</[A-Z][A-Za-z0-9.]*>', '</div>', html)
    html = html.replace('<>', '<div>').replace('</>', '</div>')
    return html


# ────────────────────────────────────────────────────────────────
#  COMBINED HTML
# ────────────────────────────────────────────────────────────────

def _build_combined_html(interfaces: list, combined_css: str, project_type: str) -> str:
    if not interfaces:
        return _wrap_in_html(
            "<p style='padding:24px;color:#6b7280;'>No se encontró contenido evaluable.</p>",
            "Paquete combinado",
            combined_css,
        )
    if len(interfaces) == 1:
        return interfaces[0]["html_content"]

    try:
        from bs4 import BeautifulSoup
        sections = []
        for iface in interfaces:
            soup = BeautifulSoup(iface["html_content"], "html.parser")
            body = soup.find("body")
            content = body.decode_contents() if body else iface["html_content"]
            sections.append(
                f'<section class="iface-section" data-file="{iface["file_name"]}">'
                f'<div class="iface-label">{iface["type"].upper()} — {iface["file_name"]}</div>'
                f'{content}'
                f'</section>'
            )
    except Exception:
        sections = [iface["html_content"] for iface in interfaces]

    section_css = """
    .iface-section {
        border: 2px solid #e5e7eb; border-radius: 8px;
        margin: 20px 0; overflow: hidden;
    }
    .iface-label {
        background: #f1f5f9; color: #374151; font-family: monospace;
        font-size: 11px; font-weight: 700; padding: 5px 12px;
        border-bottom: 1px solid #e5e7eb; letter-spacing: 0.05em;
    }
    """
    return _wrap_in_html(
        "\n".join(sections),
        f"Paquete completo — {len(interfaces)} interfaces",
        section_css + "\n" + combined_css,
    )


# ────────────────────────────────────────────────────────────────
#  UTILITY
# ────────────────────────────────────────────────────────────────

def _wrap_in_html(body_content: str, title: str, css: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; }}
    img {{ max-width: 100%; height: auto; }}
    {css}
  </style>
</head>
<body>
{body_content}
</body>
</html>"""