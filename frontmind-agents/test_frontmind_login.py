from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://frontmind-frontend.onrender.com/login')
    
    page.fill("input[type='email']", "lrosasm@upao.edu.pe")
    page.fill("input[type='password']", "302004*")
    page.click("button[type='submit']")
    
    page.wait_for_timeout(5000)
    print("Final URL after login:", page.url)
    
    try:
        error_msg = page.locator('.text-red-500, .error, .alert-danger, [role="alert"]').first.text_content(timeout=1000)
        print("Possible error message found:", error_msg)
    except:
        pass
        
    page.screenshot(path='frontmind_login.png')
    browser.close()
