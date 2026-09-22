from playwright.sync_api import sync_playwright

def main():
    url = "https://sso.upao.edu.pe:449/Account/Login?client_id=canvas_2346&nonce=28640a23d11db09a95dda0a5bcd61f18c26c5352a7e492ff&redirect_uri=https%3A%2F%2Fsso.canvaslms.com%2Flogin%2Foauth2%2Fcallback&response_type=code&scope=openid&state=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhYWNfaWQiOjE3OTc3MDAwMDAwMDAwMDAwNSwibm9uY2UiOiIyODY0MGEyM2QxMWRiMDlhOTVkZGEwYTViY2Q2MWYxOGMyNmM1MzUyYTdlNDkyZmYiLCJob3N0IjoidXBhby5pbnN0cnVjdHVyZS5jb20iLCJleHAiOjE3OTAwNDI0NDh9.yHjtavndJQXUaaellx_3iRyQ5Jn3ejwv4D_kgobdC00"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(2000)
        page.fill("input[name='id_usuario']", "000247856")
        page.fill("input[name='nip']", "302004Jk")
        page.click("input[name='btn_valida']")
        
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        
        print("Final URL:", page.url)
        text = page.evaluate("document.body.innerText")
        print("PAGE TEXT:")
        print(text)
        
        browser.close()
        
if __name__ == "__main__":
    main()
