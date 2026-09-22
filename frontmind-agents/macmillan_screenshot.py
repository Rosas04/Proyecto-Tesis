import time
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.macmillaneducationeverywhere.com/", wait_until="networkidle")
        time.sleep(5) # wait for animations
        page.screenshot(path="macmillan_screenshot.png")
        browser.close()

if __name__ == "__main__":
    test()
