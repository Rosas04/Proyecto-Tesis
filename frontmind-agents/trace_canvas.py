from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to upao.instructure.com...")
        page.goto("https://upao.instructure.com/")
        page.wait_for_timeout(3000)
        print("Redirected URL:", page.url)
        browser.close()
        
if __name__ == "__main__":
    main()
