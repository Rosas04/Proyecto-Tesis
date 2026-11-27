"""Protocol equivalence and structural correspondence on A11-A15.

1. Framework capture: runs the capture worker of FrontMind AI itself
   (frontmind-agents/services/screenshot_worker_impl.take_screenshots: its own route discovery,
   waits, container wait, tracker blocking, scroll and three viewports) from the start URL of each
   system, and records for every captured route the element count it reports (dom_metrics.total_nodes)
   and the element count of the replica built from its HTML.
2. Measurement procedure: the procedure of measure_fidelity.py on the same routes.
3. Structural correspondence (measurement procedure): besides the counts, compares the rendered page
   and its replica by
     - body tree: the sequence of (depth, tag) of every body element in document order, excluding
       script and noscript; identical sequences mean that every parent-child relation and the order of
       siblings are preserved;
     - identifiers and classes: the same sequence including the id and class list of every element;
     - body text: the normalized text of the DOM of the body (text nodes outside script, style, noscript and
       template, concatenated and with whitespace runs collapsed; independent of CSS, unlike innerText);
     - gross change per tag: elements removed and elements added by the replica (net loss = removed - added).

Usage: python verify_protocol.py <frontmind-agents> <out.json> ID=start_url|route1,route2 ...
(The worker blocks private hosts and discards private routes; for the local builds of A14-A15 both checks are
relaxed for 127.0.0.1 only.)
"""
import json, os, subprocess, sys
from collections import Counter

AGENTS = os.path.abspath(sys.argv[1])
sys.path.insert(0, AGENTS)

STRUCT_JS = """() => {
  const skip = new Set(['SCRIPT', 'NOSCRIPT']); const seq = [], seqAttr = [];
  const walk = (el, d) => { for (const c of el.children) { if (skip.has(c.tagName)) continue;
      const t = c.tagName.toLowerCase(); seq.push(d + ':' + t);
      seqAttr.push(d + ':' + t + '#' + (c.id || '') + '.' + [...c.classList].sort().join('.')); walk(c, d + 1); } };
  walk(document.body, 0);
  // text of the DOM (independent of CSS), excluding script, style, noscript and template content
  const parts = []; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (n.parentElement && n.parentElement.closest('script,style,noscript,template')) continue;
    parts.push(n.nodeValue); }
  const tags = {}; for (const e of document.querySelectorAll('*')) { const t = e.tagName.toLowerCase(); tags[t] = (tags[t] || 0) + 1; }
  return {count: document.querySelectorAll('*').length, seq, seqAttr,
          text: parts.join('').replace(/\\s+/g, ' ').trim(), tags};
}"""


def framework_capture(start_url, out_path):
    """Child process: run the framework capture worker and dump route URLs, counts and HTML."""
    os.chdir(os.path.dirname(out_path))
    from services import screenshot_worker_impl as W
    host_check = W.is_host_allowed
    W.is_host_allowed = lambda h: h == "127.0.0.1" or host_check(h)
    url_check = W.validate_url
    W.validate_url = lambda u: u.startswith("http://127.0.0.1:") or url_check(u)
    r = W.take_screenshots(url=start_url, auth=None, max_pages=10)
    json.dump([{"url": i["url"], "total_nodes": i.get("dom_metrics", {}).get("total_nodes"), "html": i["html_content"]}
               for i in r["interfaces"]], open(out_path, "w", encoding="utf-8"))


def key(u):
    u = u.split("#")[0].rstrip("/")
    return u


def main():
    from playwright.sync_api import sync_playwright
    from agents.html_replication_agent import HtmlReplicationAgent
    agent = HtmlReplicationAgent(); agent.fetch_css = lambda u: ""
    out = sys.argv[2]; tmp = os.path.join(os.path.dirname(os.path.abspath(out)), "_fw_tmp.json")
    systems = {}
    for a in sys.argv[3:]:
        sid, rest = a.split("=", 1); start, routes = rest.split("|")
        systems[sid] = (start, routes.split(","))
    res = {}
    for sid, (start, routes) in systems.items():
        subprocess.run([sys.executable, os.path.abspath(__file__), AGENTS, "--framework", start, tmp], check=True)
        res[sid] = {"start_url": start, "framework": json.load(open(tmp, encoding="utf-8")), "routes": routes}
    os.remove(tmp)

    def replica(browser, html, url):
        ctx = browser.new_context(viewport={"width": 1366, "height": 768}); p = ctx.new_page()
        p.set_content(agent.run(html_content=html, url=url)["html_replicated"], wait_until="domcontentloaded", timeout=60000)
        try:
            p.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        p.wait_for_timeout(500); s = p.evaluate(STRUCT_JS); ctx.close(); return s

    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        for sid, d in res.items():
            for fr in d["framework"]:
                fr["replica"] = replica(b, fr.pop("html"), fr["url"])["count"]
            meas = []
            for u in d["routes"]:
                ctx = b.new_context(viewport={"width": 1366, "height": 768}); p = ctx.new_page()
                p.goto(u, wait_until="domcontentloaded", timeout=60000)
                try:
                    p.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
                p.evaluate("window.scrollTo(0, document.body.scrollHeight)"); p.wait_for_timeout(300)
                p.evaluate("window.scrollTo(0, 0)"); p.wait_for_timeout(300)
                o = p.evaluate(STRUCT_JS); html = p.content(); final = p.url; ctx.close()
                r = replica(b, html, final)
                diff = Counter(o["tags"]); diff.subtract(Counter(r["tags"]))
                meas.append({"url": u, "final_url": final, "original": o["count"], "replica": r["count"],
                             "removed_by_tag": {k: v for k, v in diff.items() if v > 0},
                             "added_by_tag": {k: -v for k, v in diff.items() if v < 0},
                             "body_elements": len(o["seq"]), "body_tree_identical": o["seq"] == r["seq"],
                             "body_ids_classes_identical": o["seqAttr"] == r["seqAttr"],
                             "body_text_chars": len(o["text"]), "body_text_identical": o["text"] == r["text"]})
            d["measurement"] = meas
            fw = {key(f["url"]): f for f in d["framework"]}
            d["matched"] = [{"url": m["url"], "measurement": [m["original"], m["replica"]],
                             "framework": [fw[key(m["final_url"])]["total_nodes"], fw[key(m["final_url"])]["replica"]]
                             if key(m["final_url"]) in fw else None} for m in meas]
            print(sid, "framework routes:", [(f["url"], f["total_nodes"], f["replica"]) for f in d["framework"]], flush=True)
            for m, mm in zip(meas, d["matched"]):
                print("  ", m["url"], "meas", mm["measurement"], "fw", mm["framework"], "tree", m["body_tree_identical"],
                      "attrs", m["body_ids_classes_identical"], "text", m["body_text_identical"], "rem", m["removed_by_tag"], "add", m["added_by_tag"], flush=True)
        b.close()
    json.dump(res, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--framework":
        framework_capture(sys.argv[3], os.path.abspath(sys.argv[4]))
    else:
        main()
