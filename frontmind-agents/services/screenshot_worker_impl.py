import os
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

def take_screenshots(url: str, credentials: dict = None):
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

    from urllib.parse import urlparse, urljoin
    parsed_target = urlparse(url)
    target_origin = f"{parsed_target.scheme}://{parsed_target.netloc}"
    allowed_origins = {target_origin}

    crawled_pages = {}
    global_css_cache = {}

    def handle_response(response):
        try:
            if response.request.resource_type == "stylesheet":
                url_str = response.url
                if url_str not in global_css_cache:
                    global_css_cache[url_str] = response.text()
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = context.new_page()
        page.on("response", handle_response)

        urls_to_visit = []
        visited = set()
        max_pages = 15

        # 1. Automate login sequence if credentials are provided
        if credentials and credentials.get("username_value") and credentials.get("password_value"):
            login_url = credentials.get("login_url") or url
            try:
                page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2000)
                
                # Capture the login page HTML and state before logging in!
                try:
                    login_html = page.content()
                    login_title = page.title() or login_url
                    parsed_login = urlparse(login_url)
                    login_norm = f"{parsed_login.scheme}://{parsed_login.netloc}{parsed_login.path.rstrip('/')}"
                    
                    path_str = parsed_login.path or "/"
                    if not path_str or path_str == "/":
                        file_name = "login.html"
                    else:
                        file_name = path_str.strip("/").replace("/", "_") + ".html"
                        
                    crawled_pages[login_norm] = {
                        "html": login_html,
                        "title": login_title,
                        "url": login_url,
                        "cssom_styles": [],
                        "relative_path": path_str,
                        "file_name": file_name,
                    }
                    visited.add(login_norm)
                    
                    # Extract links from the login page
                    login_links = page.evaluate("""() => {
                        return Array.from(document.querySelectorAll('a'))
                            .map(a => a.href)
                            .filter(href => href && !href.startsWith('javascript:') && !href.startsWith('#'));
                    }""")
                    for link in login_links:
                        abs_link = urljoin(login_url, link)
                        parsed_link = urlparse(abs_link)
                        link_origin = f"{parsed_link.scheme}://{parsed_link.netloc}"
                        link_path = parsed_link.path.lower()

                        is_internal = (link_origin in allowed_origins)
                        is_logout = any(x in link_path or x in parsed_link.query.lower() for x in ["logout", "signout", "exit", "cerrar-sesion"])

                        if is_internal and not is_logout:
                            norm_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path.rstrip('/')}"
                            if norm_link not in visited:
                                urls_to_visit.append(abs_link)
                except Exception as capture_err:
                    print(f"Failed to pre-capture login page: {capture_err}")
                
                # Fill username
                if not credentials.get("username_selector"):
                    try:
                        has_input = page.locator("input[type='email'], input[type='text'], input[name*='user' i]").first.is_visible(timeout=2000)
                        if not has_input:
                            login_btn = page.locator("button:has-text('Log in'), button:has-text('Login'), a:has-text('Log in'), a:has-text('Login'), a[href*='login' i]").first
                            if login_btn.is_visible(timeout=1000):
                                try:
                                    href = login_btn.get_attribute("href")
                                    if href:
                                        from urllib.parse import urljoin
                                        page.goto(urljoin(page.url, href))
                                        page.wait_for_timeout(3000)
                                    else:
                                        login_btn.click(force=True)
                                        page.wait_for_timeout(3000)
                                except Exception: pass
                    except Exception: pass

                user_sel = credentials.get("username_selector")
                if not user_sel:
                    for selector in ["input[type='email']", "input[type='text']", "input[name='username']", "input[name='email']", "input[name='login']", "input[id*='user' i]", "input[id*='email' i]", "input[name*='user' i]"]:
                        try:
                            if page.locator(selector).first.is_visible(timeout=1000):
                                user_sel = selector
                                break
                        except Exception: pass
                
                # Fill password
                pass_sel = credentials.get("password_selector")
                if not pass_sel:
                    for selector in ["input[type='password']", "input[name='password']", "input[name*='pass' i]", "input[id*='pass' i]"]:
                        try:
                            if page.locator(selector).first.is_visible(timeout=1000):
                                pass_sel = selector
                                break
                        except Exception: pass
                            
                if user_sel:
                    page.fill(user_sel, credentials["username_value"])
                    
                    if not pass_sel:
                        page.press(user_sel, "Enter")
                        page.wait_for_timeout(2000)
                        for selector in ["input[type='password']", "input[name='password']", "input[name*='pass' i]", "input[id*='pass' i]"]:
                            try:
                                if page.locator(selector).first.is_visible(timeout=1000):
                                    pass_sel = selector
                                    break
                            except Exception: pass
                    
                    if pass_sel:
                        page.fill(pass_sel, credentials["password_value"])
                        
                        submit_sel = credentials.get("submit_selector")
                        if submit_sel:
                            try: page.click(submit_sel)
                            except Exception: page.press(pass_sel, "Enter")
                        else:
                            submitted = False
                            for selector in ["button[type=submit]", "input[type=submit]", "button:has-text('Iniciar')", "button:has-text('Login')", "button:has-text('Ingresar')"]:
                                try:
                                    if page.locator(selector).first.is_visible(timeout=1000):
                                        page.click(selector)
                                        submitted = True
                                        break
                                except Exception: pass
                            if not submitted:
                                page.press(pass_sel, "Enter")
                            
                    try: 
                        page.wait_for_navigation(timeout=8000)
                    except Exception: 
                        page.wait_for_timeout(5000)
                        
                    # Also wait for a generic 'loading' overlay to disappear if present
                    try:
                        page.wait_for_selector("text=Cargando", state="detached", timeout=3000)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Login failed: {e}")

        # 2. Crawl discovery loop
        post_login_url = page.url
        parsed_post = urlparse(post_login_url)
        post_norm = f"{parsed_post.scheme}://{parsed_post.netloc}{parsed_post.path.rstrip('/')}"
        post_origin = f"{parsed_post.scheme}://{parsed_post.netloc}"
        allowed_origins.add(post_origin)
        
        if post_norm in visited:
            visited.remove(post_norm)
            
        if post_login_url not in urls_to_visit:
            urls_to_visit.insert(0, post_login_url)

        while urls_to_visit and len(visited) < max_pages:
            curr_url = urls_to_visit.pop(0)
            parsed_curr = urlparse(curr_url)
            normalized_url = f"{parsed_curr.scheme}://{parsed_curr.netloc}{parsed_curr.path.rstrip('/')}"

            if normalized_url in visited:
                continue

            visited.add(normalized_url)

            try:
                page.goto(curr_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3500)
                try:
                    # Wait for any session loading screen to disappear
                    page.wait_for_selector("text=Cargando", state="detached", timeout=5000)
                except Exception:
                    pass

                # Check for redirection
                final_url = page.url
                parsed_final = urlparse(final_url)
                final_origin = f"{parsed_final.scheme}://{parsed_final.netloc}"

                # Only extract links if we are still on the same origin (not logged out or external redirected)
                if final_origin not in allowed_origins:
                    continue

                html = page.content()
                title = page.title() or curr_url

                # Get CSSOM styles
                cssom_styles = []
                try:
                    extracted = page.evaluate("""() => {
                        const styles = [];
                        for (const sheet of document.styleSheets) {
                            try {
                                const rules = sheet.cssRules || sheet.rules;
                                if (rules) {
                                    let content = "";
                                    for (const rule of rules) {
                                        content += rule.cssText + "\\n";
                                    }
                                    if (content.trim()) {
                                        styles.push(content);
                                    }
                                }
                            } catch (e) {}
                        }
                        return styles;
                    }""")
                    if isinstance(extracted, list):
                        cssom_styles = extracted
                except Exception:
                    pass

                # Derive file_name and relative_path
                path = parsed_final.path
                frag = parsed_final.fragment
                query = parsed_final.query
                
                full_path = path
                if query: full_path += f"_{query}"
                if frag: full_path += f"_{frag}"
                
                import re
                safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', full_path).strip('_')
                if not safe_name: safe_name = "index"
                file_name = safe_name + ".html"
                relative_path = full_path

                crawled_pages[normalized_url] = {
                    "html": html,
                    "title": title,
                    "url": final_url,
                    "cssom_styles": cssom_styles,
                    "relative_path": relative_path,
                    "file_name": file_name,
                }

                # Expand SPA dropdowns to ensure hidden links are in the DOM
                try:
                    page.evaluate("""() => {
                        const toggles = document.querySelectorAll('button, [role="button"], [aria-expanded], [aria-haspopup], .menu-item, [class*="dropdown"], [class*="nav"], [class*="menu"]');
                        toggles.forEach(t => {
                            try {
                                const text = (t.innerText || '').toLowerCase();
                                if(text.includes('logout') || text.includes('sign out') || text.includes('cerrar sesion') || text.includes('exit')) return;
                                if(text.includes('delete') || text.includes('remove') || text.includes('eliminar')) return;
                                t.click();
                            } catch(e) {}
                        });
                    }""")
                    page.wait_for_timeout(1500)
                except:
                    pass

                # Extract links on page
                links = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(href => href && !href.startsWith('javascript:'));
                }""")

                for link in links:
                    abs_link = urljoin(final_url, link)
                    parsed_link = urlparse(abs_link)
                    link_origin = f"{parsed_link.scheme}://{parsed_link.netloc}"
                    link_path = parsed_link.path.lower()

                    is_internal = (link_origin in allowed_origins)
                    is_logout = any(x in link_path or x in parsed_link.query.lower() for x in ["logout", "signout", "exit", "cerrar-sesion"])

                    if is_internal and not is_logout:
                        query_part = f"?{parsed_link.query}" if parsed_link.query else ""
                        frag_part = f"#{parsed_link.fragment}" if parsed_link.fragment else ""
                        norm_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}{query_part}{frag_part}"
                        
                        if norm_link not in visited and norm_link not in urls_to_visit:
                            urls_to_visit.append(norm_link)
            except Exception as e:
                print(f"Error crawling {curr_url}: {e}")

        # Close discovery page
        page.close()

        # 3. Take screenshots for all discovered pages and viewports
        interfaces_list = []
        parsed_main = urlparse(url)
        main_normalized_url = f"{parsed_main.scheme}://{parsed_main.netloc}{parsed_main.path.rstrip('/')}"

        for norm_url, p_info in crawled_pages.items():
            page_captures = []
            
            for item in viewports:
                vp_page = context.new_page()
                try:
                    vp_page.set_viewport_size({"width": item["width"], "height": item["height"]})
                except Exception:
                    pass
                
                try:
                    vp_page.goto(p_info["url"], wait_until="domcontentloaded", timeout=30000)
                    vp_page.wait_for_timeout(2000)
                    try:
                        # Wait for any session loading screen to disappear
                        vp_page.wait_for_selector("text=Cargando", state="detached", timeout=5000)
                    except Exception:
                        pass
                    
                    try:
                        vp_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        vp_page.wait_for_timeout(500)
                        vp_page.evaluate("window.scrollTo(0, 0)")
                        vp_page.wait_for_timeout(500)
                    except: pass

                    file_name = f"{item['device']}_{timestamp}_{p_info['file_name'].replace('.html', '')}.png"
                    file_path = output_dir / file_name

                    vp_page.screenshot(path=str(file_path), full_page=True)

                    page_captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "file_name": file_name,
                        "file_path": str(file_path),
                        "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                    })
                except Exception as e:
                    page_captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "error": str(e),
                    })
                finally:
                    vp_page.close()

            p_info["captures"] = page_captures
            
            interfaces_list.append({
                "file_name": p_info["file_name"],
                "relative_path": p_info["relative_path"],
                "html_content": p_info["html"],
                "type": "html",
                "captures": page_captures,
                "cssom_styles": p_info["cssom_styles"],
            })

        browser.close()

    main_page_data = crawled_pages.get(main_normalized_url)
    if not main_page_data and crawled_pages:
        first_key = list(crawled_pages.keys())[0]
        main_page_data = crawled_pages[first_key]

    if main_page_data:
        return {
            "html_content": main_page_data["html"],
            "captures": main_page_data["captures"],
            "total_captures": len(main_page_data["captures"]),
            "captured_at": timestamp,
            "css_cache": global_css_cache,
            "cssom_styles": main_page_data["cssom_styles"],
            "interfaces": interfaces_list,
            "source_type": "url",
        }
    else:
        return {
            "html_content": "",
            "captures": [],
            "total_captures": 0,
            "captured_at": timestamp,
            "css_cache": {},
            "cssom_styles": [],
            "interfaces": [],
            "source_type": "url",
        }


def take_screenshots_from_html(html_content: str, label: str = "zip"):
    """Generate viewport screenshots from raw HTML using Playwright set_content()."""
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

    captures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for item in viewports:
            page = browser.new_page(
                viewport={"width": item["width"], "height": item["height"]},
            )

            try:
                page.set_content(html_content, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)

                file_name = f"{label}_{item['device']}_{timestamp}.png"
                file_path = output_dir / file_name

                page.screenshot(path=str(file_path), full_page=True)

                captures.append({
                    "device": item["device"],
                    "width": item["width"],
                    "height": item["height"],
                    "file_name": file_name,
                    "file_path": str(file_path),
                    "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                })

            except Exception as e:
                captures.append({
                    "device": item["device"],
                    "width": item["width"],
                    "height": item["height"],
                    "error": str(e),
                })
            finally:
                page.close()

        browser.close()

    return {
        "captures": captures,
        "total_captures": len(captures),
        "captured_at": timestamp,
    }


def take_screenshots_for_multiple_htmls(htmls: dict, label_prefix: str = "zip"):
    """Generate viewport screenshots from multiple HTML contents using a single Playwright session."""
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for key, html_content in htmls.items():
            if not html_content or not html_content.strip():
                results[key] = []
                continue

            captures = []
            safe_key = re.sub(r'[^a-zA-Z0-9_-]', '_', key)[:30]

            for item in viewports:
                page = browser.new_page(
                    viewport={"width": item["width"], "height": item["height"]},
                )

                try:
                    page.set_content(html_content, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1500)

                    file_name = f"{label_prefix}_{safe_key}_{item['device']}_{timestamp}.png"
                    file_path = output_dir / file_name

                    page.screenshot(path=str(file_path), full_page=True)

                    captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "file_name": file_name,
                        "file_path": str(file_path),
                        "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                    })

                except Exception as e:
                    captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "error": str(e),
                    })
                finally:
                    page.close()

            results[key] = captures

        browser.close()

    return results
