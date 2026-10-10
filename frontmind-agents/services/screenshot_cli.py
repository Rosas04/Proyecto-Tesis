import json
import logging
import sys
from pathlib import Path

# Add current directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.progress_service import progress_path, purge_old_progress
from services.screenshot_worker_impl import (
    take_screenshots,
    take_screenshots_from_html,
    take_screenshots_for_multiple_htmls
)


def _configure_logging(job_id):
    """Log de progreso aislado por tarea (progress/<job_id>.log)."""
    path = progress_path(job_id)
    handlers = [logging.FileHandler(path, mode="w", encoding="utf-8")] if path else [logging.NullHandler()]
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO,
        handlers=handlers,
    )


def main():
    try:
        # Read request from stdin
        request = json.loads(sys.stdin.read())

        purge_old_progress()
        _configure_logging(request.get("job_id"))

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
        # Sólo el tipo y mensaje del error: nunca variables de entorno ni el
        # request (contiene credenciales del sitio auditado).
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
