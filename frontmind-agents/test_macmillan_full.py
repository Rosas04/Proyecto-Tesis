from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://identity.macmillaneducationeverywhere.com/authentication/login')
    
    # Dismiss cookie banner
    try:
        page.locator('button:has-text("Accept all cookies")').click(timeout=5000)
        print("Dismissed cookie banner")
    except Exception as e:
        print("No cookie banner found or failed to click:", e)
        
    try:
        # If there's an explicit login link (like Macmillan)
        page.locator('a[href="/oidc-login"]').click(timeout=5000)
        print("Clicked Log in link")
    except:
        pass
        
    page.wait_for_load_state('networkidle')
    
    username_field = page.get_by_label("Username").or_(page.get_by_placeholder("Email")).or_(page.locator("input[type='email'], input[name='username']")).first
    username_field.fill("AngelBazauri", force=True)
    
    password_field = page.locator("input[type='password']").first
    password_field.fill("Sebastian123", force=True)
    
    submit_btn = page.locator("button[type='submit'], input[type='submit'], button[name='submit']").first
    submit_btn.click(force=True)
    
    page.wait_for_load_state('networkidle', timeout=15000)
    page.wait_for_timeout(3000)
    print("Final URL:", page.url)
    
    browser.close()
