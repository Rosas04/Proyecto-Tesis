import json
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://frontmind-frontend.onrender.com/login", wait_until="networkidle")
        
        inputs = page.locator("input").element_handles()
        print(f"Found {len(inputs)} inputs")
        for i, handle in enumerate(inputs):
            props = page.evaluate("(el) => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder })", handle)
            print(f"Input {i}: {json.dumps(props)}")
            
        buttons = page.locator("button, input[type='submit']").element_handles()
        print(f"Found {len(buttons)} buttons")
        for i, handle in enumerate(buttons):
            props = page.evaluate("(el) => ({ text: el.innerText, type: el.type, name: el.name, id: el.id })", handle)
            print(f"Button {i}: {json.dumps(props)}")
            
        browser.close()

if __name__ == "__main__":
    test()
