import json

def main():
    try:
        with open("resultado_mvp_mobile.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print("Agent:", data.get("agent"))
        print("Status:", data.get("status"))
        print("Start URL:", data.get("start_url"))
        print("Final URL:", data.get("final_url"))
        print("Routes Discovered:", data.get("routes_discovered"))
        
        print("\nInterfaces:")
        for iface in data.get("interfaces", []):
            print(f" - {iface.get('name')} | URL: {iface.get('url')} | Title: {iface.get('title')}")
            print(f"   HTML Length: {iface.get('html_length')}")
            print(f"   DOM Metrics: {iface.get('dom_metrics')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
