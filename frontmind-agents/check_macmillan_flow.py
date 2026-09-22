import json
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.macmillaneducationeverywhere.com/", wait_until="networkidle")
        
        # Look for login button
        print("Looking for login button...")
        login_btn = page.get_by_role("link", name="Login").first
        if not login_btn.is_visible():
            login_btn = page.locator("text=Login").first
            
        if login_btn.is_visible():
            print("Found login button, clicking...")
            login_btn.click()
            page.wait_for_load_state("networkidle")
            print("Navigated to:", page.url)
            
            # Check inputs now
            inputs = page.locator("input").element_handles()
            print(f"Found {len(inputs)} inputs after click")
            for i, handle in enumerate(inputs):
                props = page.evaluate("(el) => ({ type: el.type, name: el.name, id: el.id })", handle)
                print(f"Input {i}: {json.dumps(props)}")
        else:
            print("No login button found!")
            
        browser.close()

if __name__ == "__main__":
    test()
