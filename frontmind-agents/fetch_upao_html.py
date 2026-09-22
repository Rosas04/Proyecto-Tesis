from playwright.sync_api import sync_playwright

def main():
    url = "https://sso.upao.edu.pe:449/Account/Login?client_id=canvas_2346&nonce=28640a23d11db09a95dda0a5bcd61f18c26c5352a7e492ff&redirect_uri=https%3A%2F%2Fsso.canvaslms.com%2Flogin%2Foauth2%2Fcallback&response_type=code&scope=openid&state=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhYWNfaWQiOjE3OTc3MDAwMDAwMDAwMDAwNSwibm9uY2UiOiIyODY0MGEyM2QxMWRiMDlhOTVkZGEwYTViY2Q2MWYxOGMyNmM1MzUyYTdlNDkyZmYiLCJob3N0IjoidXBhby5pbnN0cnVjdHVyZS5jb20iLCJleHAiOjE3OTAwNDI0NDh9.yHjtavndJQXUaaellx_3iRyQ5Jn3ejwv4D_kgobdC00"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        print("Page title:", page.title())
        html = page.content()
        with open("upao_login.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()
        
if __name__ == "__main__":
    main()
