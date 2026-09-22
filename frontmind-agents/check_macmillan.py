import json
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.macmillaneducationeverywhere.com/", wait_until="networkidle")
        
        # Check if login is inside an iframe
        iframes = page.frames
        print(f"Found {len(iframes)} frames")
        
        inputs = page.locator("input").element_handles()
        print(f"Found {len(inputs)} inputs in main frame")
        for i, handle in enumerate(inputs):
            props = page.evaluate("(el) => ({ type: el.type, name: el.name, id: el.id, placeholder: el.placeholder, isVisible: el.offsetParent !== null })", handle)
            print(f"Input {i}: {json.dumps(props)}")
            
        browser.close()

if __name__ == "__main__":
    test()
