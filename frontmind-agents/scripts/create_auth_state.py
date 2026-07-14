import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def create_auth_state(url: str, output_path: str = "playwright/.auth/session.json"):
    print(f"Starting browser. Please login manually on the opened page: {url}")
    print(f"Once you have successfully logged in, close the browser window to save the state.")
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        
        # Wait for the page to be closed by the user
        try:
            page.wait_for_event("close", timeout=0)
        except Exception as e:
            print("Finished waiting.")
            
        print(f"Saving authentication state to {output_path}...")
        context.storage_state(path=str(output_file))
        print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_auth_state.py <login_url> [output_path]")
        sys.exit(1)
        
    target_url = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "playwright/.auth/session.json"
    
    create_auth_state(target_url, out_path)
