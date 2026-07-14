from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://frontmind-frontend.onrender.com/login')
    
    page.fill("input[type='email']", "lrosasm@upao.edu.pe")
    page.fill("input[type='password']", "302004*")
    page.click("button[type='submit']")
    
    page.wait_for_timeout(5000)
    print("Final URL after login:", page.url)
    
    local_storage = page.evaluate("() => JSON.stringify(localStorage)")
    session_storage = page.evaluate("() => JSON.stringify(sessionStorage)")
    
    print("LocalStorage:", local_storage)
    print("SessionStorage:", session_storage)
    
    # Check if links exist on /input
    links = page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)")
    print("Links on page:", links)
    
    # Reload the page to see if it stays logged in
    page.goto(page.url)
    page.wait_for_timeout(3000)
    print("URL after reload:", page.url)
    
    browser.close()
