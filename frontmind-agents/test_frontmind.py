import json
from services.screenshot_worker_impl import take_screenshots

url = "https://upao.instructure.com/"
auth = {
    "mode": "form",
    "login_url": "https://upao.instructure.com/",
    "username": "000247856",
    "password": "302004Jk"
}

try:
    print("Running take_screenshots...")
    result = take_screenshots(url=url, auth=auth, max_pages=10)
    print(f"Status: {result.get('status')}")
    print(f"Total interfaces found: {result.get('total_interfaces')}")
    for idx, interface in enumerate(result.get('interfaces', [])):
        print(f"  {idx+1}. {interface.get('name')} - {interface.get('url')}")
        if interface.get('errors'):
            print(f"     Errors: {interface.get('errors')}")
except Exception as e:
    print("Error occurred:")
    import traceback
    traceback.print_exc()
