"""Comparison of capture tools on the same routes (A11-A15).

For every route and tool:
  native  = document.querySelectorAll('*').length in the tool's own DOM after loading the page
  replica = the same count on the replica that HtmlReplicationAgent builds from the tool's HTML,
            always rendered in Playwright/Chromium exactly as in measure_fidelity.py
The reference is the rendered DOM obtained by Playwright/Chromium (the capture agent of FrontMind AI),
so fidelity_tool = replica_tool / native_playwright x 100.

Tools: Playwright 1.60 (reference), Selenium WebDriver (Chromium; idle-equivalent wait and default load-event wait), Puppeteer-core (Chromium),
jsdom executing scripts, and jsdom without scripts (HTML served before JavaScript runs).
All Chromium-based tools use the same Chromium binary installed by Playwright.

Usage: python compare_tools.py <frontmind-agents> <node tools dir> <out.json> <runs> ID=url1,url2 ...
"""
import json, os, subprocess, sys, time

sys.path.insert(0, sys.argv[1])
from playwright.sync_api import sync_playwright  # noqa: E402
from agents.html_replication_agent import HtmlReplicationAgent  # noqa: E402

agent = HtmlReplicationAgent(); agent.fetch_css = lambda u: ""
COUNT_JS = "() => document.querySelectorAll('*').length"
NODE_DIR = os.path.abspath(sys.argv[2])
NODE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "capture_node.js")


def settle(page, timeout=20000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass


def replica_count(browser, html, url):
    ctx = browser.new_context(viewport={"width": 1366, "height": 768}); page = ctx.new_page()
    page.set_content(agent.run(html_content=html, url=url)["html_replicated"], wait_until="domcontentloaded",
                     timeout=60000)
    settle(page); page.wait_for_timeout(500)
    n = page.evaluate(COUNT_JS); ctx.close(); return n


def via_playwright(browser, url):
    ctx = browser.new_context(viewport={"width": 1366, "height": 768}); page = ctx.new_page()
    t0 = time.perf_counter()
    page.goto(url, wait_until="domcontentloaded", timeout=60000); settle(page)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)"); page.wait_for_timeout(300)
    page.evaluate("window.scrollTo(0, 0)"); page.wait_for_timeout(300)
    r = {"count": page.evaluate(COUNT_JS), "html": page.content(), "time_s": time.perf_counter() - t0}
    ctx.close(); return r


IDLE_JS = ("return [document.querySelectorAll('*').length, performance.getEntriesByType('resource').length, "
           "document.readyState]")


def via_selenium(url, exe, idle=True):
    """idle=True: wait until the DOM size and the number of loaded resources stay unchanged for 1 s (up to 20 s),
    the closest equivalent of Playwright's network idleness; idle=False: Selenium's default wait (load event)."""
    from selenium import webdriver
    opts = webdriver.ChromeOptions(); opts.binary_location = exe
    for a in ("--headless=new", "--window-size=1366,768", "--no-sandbox"):
        opts.add_argument(a)
    drv = webdriver.Chrome(options=opts)
    try:
        t0 = time.perf_counter(); drv.set_page_load_timeout(60); drv.get(url)   # returns after the load event
        if idle:
            last, since, start = None, time.time(), time.time()
            while time.time() - start < 20:
                c = drv.execute_script(IDLE_JS)
                if c != last:
                    last, since = c, time.time()
                elif time.time() - since >= 1:
                    break
                time.sleep(0.25)
        drv.execute_script("window.scrollTo(0, document.body.scrollHeight)"); time.sleep(0.3)
        drv.execute_script("window.scrollTo(0, 0)"); time.sleep(0.3)
        return {"count": drv.execute_script("return document.querySelectorAll('*').length"),
                "html": drv.page_source, "time_s": time.perf_counter() - t0}
    finally:
        drv.quit()


def via_node(mode, url, exe):
    out = subprocess.run(["node", NODE_SCRIPT, mode, url, exe], cwd=NODE_DIR, capture_output=True, text=True,
                         encoding="utf-8", timeout=180, env={**os.environ, "NODE_PATH": os.path.join(NODE_DIR, "node_modules")})
    try:
        return json.loads(out.stdout)
    except ValueError:
        return {"error": (out.stderr or "no output")[-300:]}


def main():
    out, runs = sys.argv[3], int(sys.argv[4])
    systems = {a.split("=", 1)[0]: a.split("=", 1)[1].split(",") for a in sys.argv[5:]}
    res = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True); exe = p.chromium.executable_path
        print("Chromium", browser.version, flush=True)
        tools = {"playwright": lambda u: via_playwright(browser, u), "selenium": lambda u: via_selenium(u, exe),
                 "selenium_load": lambda u: via_selenium(u, exe, idle=False),
                 "puppeteer": lambda u: via_node("puppeteer", u, exe), "jsdom": lambda u: via_node("jsdom", u, exe),
                 "jsdom_static": lambda u: via_node("jsdom_static", u, exe)}
        for sid, urls in systems.items():
            res[sid] = {}
            for tool, fn in tools.items():
                res[sid][tool] = []
                for r in range(1, runs + 1):
                    routes = []
                    for u in urls:
                        x = fn(u)
                        if "error" in x:
                            routes.append({"url": u, "error": x["error"]}); continue
                        routes.append({"url": u, "native": x["count"], "replica": replica_count(browser, x["html"], u),
                                       "time_s": round(x["time_s"], 2)})
                    run = {"run": r, "routes": routes,
                           "native": sum(z.get("native", 0) for z in routes),
                           "replica": sum(z.get("replica", 0) for z in routes)}
                    res[sid][tool].append(run)
                    print(sid, tool, r, run["native"], run["replica"], flush=True)
        browser.close()
    json.dump(res, open(out, "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    main()
