// Captures a page with Puppeteer (Chromium) or jsdom and prints JSON {count, html, time_s}.
// Usage: node capture_node.js <puppeteer|jsdom|jsdom_static> <url> [chromium executable for puppeteer]
const mode = process.argv[2], url = process.argv[3], exe = process.argv[4];
const COUNT = "document.querySelectorAll('*').length";
const sleep = ms => new Promise(r => setTimeout(r, ms));
// page scripts that jsdom cannot run (e.g. dynamic import()) must not abort the capture
process.on("unhandledRejection", () => {}); process.on("uncaughtException", () => {});

async function stable(getCount, maxMs) {            // wait until the element count is unchanged for 1 s
  let last = -1, since = Date.now(); const t0 = Date.now();
  while (Date.now() - t0 < maxMs) {
    const c = await getCount();
    if (c !== last) { last = c; since = Date.now(); } else if (Date.now() - since >= 1000) break;
    await sleep(250);
  }
}

async function viaPuppeteer() {
  const puppeteer = require("puppeteer-core");
  const browser = await puppeteer.launch({ executablePath: exe, headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 768 });
  const t0 = Date.now();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  try { await page.waitForNetworkIdle({ idleTime: 500, timeout: 20000 }); } catch (e) { }
  await page.evaluate("window.scrollTo(0, document.body.scrollHeight)"); await sleep(300);
  await page.evaluate("window.scrollTo(0, 0)"); await sleep(300);
  const count = await page.evaluate(COUNT); const html = await page.content();
  await browser.close();
  return { count, html, time_s: (Date.now() - t0) / 1000 };
}

async function viaJsdom(runScripts) {
  const { JSDOM, VirtualConsole } = require("jsdom");
  const vc = new VirtualConsole();                    // silence page errors
  const t0 = Date.now();
  const opts = { pretendToBeVisual: true, virtualConsole: vc };
  if (runScripts) { opts.runScripts = "dangerously"; opts.resources = "usable"; }
  const dom = await JSDOM.fromURL(url, opts);
  await new Promise(r => { if (dom.window.document.readyState === "complete") r(); else dom.window.addEventListener("load", r); setTimeout(r, 20000); });
  if (runScripts) await stable(async () => dom.window.document.querySelectorAll("*").length, 10000);
  const count = dom.window.document.querySelectorAll("*").length; const html = dom.serialize();
  dom.window.close();
  return { count, html, time_s: (Date.now() - t0) / 1000 };
}

(async () => {
  try {
    const r = mode === "puppeteer" ? await viaPuppeteer() : await viaJsdom(mode === "jsdom");
    process.stdout.write(JSON.stringify(r));
  } catch (e) { process.stdout.write(JSON.stringify({ error: String(e) })); }
  process.exit(0);
})();
