from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://frontmind-frontend.onrender.com')
    page.wait_for_timeout(3000)
    print('Initial URL:', page.url)
    page.fill("input[type='email']", 'lrosasm@upao.edu.pe')
    page.fill("input[type='password']", '1234567') # assuming 1234567 for testing
    page.click("button[type='submit']")
    page.wait_for_timeout(5000)
    print('Final URL:', page.url)
    try:
        error_msg = page.locator('.auth-error').text_content(timeout=1000)
        print('Auth Error on page:', error_msg)
    except Exception as e:
        print('No auth error visible.')
    
    # Dump links
    links = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a')).map(a => a.href);
    }""")
    print("Links on page:", links)
    browser.close()
