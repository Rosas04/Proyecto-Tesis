import logging
from agents.capture_agent import CaptureAgent

logging.basicConfig(level=logging.INFO)

def main():
    agent = CaptureAgent()
    auth_config = {
        "mode": "form",
        "login_url": "https://upao.instructure.com/",
        "username": "000247856",
        "password": "302004Jk",
    }
    
    try:
        result = agent.run(url="https://upao.instructure.com/", auth=auth_config, max_pages=3)
        print("Success! Routes discovered:", result.get("routes_discovered"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
