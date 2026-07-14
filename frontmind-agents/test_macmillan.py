from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://identity.macmillaneducationeverywhere.com/authentication/login', wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    
    page.screenshot(path='macmillan_page.png')
    with open('macmillan_page.html', 'w', encoding='utf-8') as f:
        f.write(page.content())
        
    browser.close()
