import json
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://frontmind-frontend.onrender.com/login", wait_until="networkidle")
        
        # Fill email
        email = page.locator("input[type='email']").first
        email.focus()
        email.fill("lrosasm@upao.edu.pe")
        email.evaluate("node => node.dispatchEvent(new Event('change', { bubbles: true }))")
        
        # Fill password
        password = page.locator("input[type='password']").first
        password.focus()
        password.fill("302004*")
        password.evaluate("node => node.dispatchEvent(new Event('change', { bubbles: true }))")
        
        # Click login
        submit = page.locator("button[type='submit']").first
        submit.click()
        
        page.wait_for_timeout(3000)
        print("URL after login:", page.url)
        
        # Print visible errors
        errors = page.locator(".text-red-500, [role='alert']").element_handles()
        for e in errors:
            print("Error text:", e.inner_text())
            
        browser.close()

if __name__ == "__main__":
    test()
