import os
import sys
import json
import traceback
from pathlib import Path

# Add current directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.screenshot_worker_impl import (
    take_screenshots,
    take_screenshots_from_html,
    take_screenshots_for_multiple_htmls
)

def main():
    try:
        # Read request from stdin
        input_data = sys.stdin.read()
        request = json.loads(input_data)
        
        action = request.get("action")
        
        if action == "url":
            results = take_screenshots(
                url=request.get("url"),
                auth=request.get("auth") or request.get("credentials"),
                max_pages=request.get("max_pages", 10)
            )
        elif action == "html":
            results = take_screenshots_from_html(
                request.get("html"),
                request.get("label", "zip")
            )
        elif action == "multiple":
            results = take_screenshots_for_multiple_htmls(
                request.get("htmls"),
                request.get("label_prefix", "zip")
            )
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Print results to stdout
        print(json.dumps(results))
    except Exception as e:
        # Print traceback and error details to stderr and exit
        traceback.print_exc(file=sys.stderr)
        try:
            with open("cli_error_env.txt", "w") as f:
                f.write(f"Error: {e}\n\n")
                for k, v in os.environ.items():
                    f.write(f"{k}: {v}\n")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
