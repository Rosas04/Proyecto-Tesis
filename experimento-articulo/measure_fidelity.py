"""DOM capture fidelity of FrontMind AI (measurement procedure of the article).

Original nodes = document.querySelectorAll('*').length on the rendered page, as in
                 collect_dom_metrics of the capture agent.
Captured nodes = the same count on the replica produced by HtmlReplicationAgent
                 (frontmind-agents), rendered in Chromium.
Both counts are summed over all routes of a system.

Fixed parameters: headless Chromium, 1366 x 768 viewport, navigation with
wait_until="domcontentloaded" (60 s timeout), network idle (20 s timeout),
scroll to the bottom and back to the top (300 ms pauses), 500 ms settle on the replica.
The CSS download of the replication agent is disabled because stylesheet content
does not change the number of element nodes.

For every route the script also records the element count per tag name in the
original page and in the replica, so the removed nodes are classified by tag
automatically (no human judgement involved).

Usage:
  python measure_fidelity.py <frontmind-agents dir> <out.json> <runs> ID=url1,url2 [ID=url ...]
"""
import json
import sys
import time
from collections import Counter

sys.path.insert(0, sys.argv[1])
from playwright.sync_api import sync_playwright  # noqa: E402
from agents.html_replication_agent import HtmlReplicationAgent  # noqa: E402

agent = HtmlReplicationAgent()
agent.fetch_css = lambda css_url: ""

COUNT_JS = "() => document.querySelectorAll('*').length"
TAGS_JS = ("() => { const c = {}; for (const e of document.querySelectorAll('*')) "
           "{ const t = e.tagName.toLowerCase(); c[t] = (c[t] || 0) + 1; } return c; }")
VIEWPORT = {"width": 1366, "height": 768}


def settle(page, timeout=20000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass


def measure_route(browser, url):
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    t0 = time.perf_counter()
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    settle(page)
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
    except Exception:
        pass
    original = page.evaluate(COUNT_JS)
    tags_original = page.evaluate(TAGS_JS)
    html = page.content()
    elapsed = time.perf_counter() - t0
    final_url = page.url
    replica = agent.run(html_content=html, url=final_url)["html_replicated"]
    rpage = ctx.new_page()
    rpage.set_content(replica, wait_until="domcontentloaded", timeout=60000)
    settle(rpage)
    rpage.wait_for_timeout(500)
    captured = rpage.evaluate(COUNT_JS)
    tags_replica = rpage.evaluate(TAGS_JS)
    ctx.close()
    diff = Counter(tags_original)
    diff.subtract(Counter(tags_replica))
    removed_by_tag = {k: v for k, v in sorted(diff.items()) if v != 0}
    return {"url": url, "final_url": final_url, "original": original, "captured": captured,
            "removed_by_tag": removed_by_tag, "time_s": round(elapsed, 2)}


def main():
    out, runs = sys.argv[2], int(sys.argv[3])
    systems = {}
    for arg in sys.argv[4:]:
        name, urls = arg.split("=", 1)
        systems[name] = urls.split(",")
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        print("Chromium", browser.version, flush=True)
        for name, urls in systems.items():
            results[name] = []
            for r in range(1, runs + 1):
                routes = [measure_route(browser, u) for u in urls]
                o = sum(x["original"] for x in routes)
                c = sum(x["captured"] for x in routes)
                t = round(sum(x["time_s"] for x in routes), 2)
                run = {"run": r, "routes": routes, "original": o, "captured": c, "time_s": t,
                       "fidelity": round(c / o * 100, 2) if o else None}
                results[name].append(run)
                print(f"{name} run {r}: original={o} captured={c} fidelity={run['fidelity']}% time={t}s",
                      flush=True)
        browser.close()
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
