from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://frontmind-frontend.onrender.com/", wait_until="networkidle")
        print("Redirected to:", page.url)
        browser.close()

if __name__ == "__main__":
    test()
