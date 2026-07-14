from services.screenshot_service import take_screenshots


class CaptureAgent:
    def run(self, url: str, auth: dict = None, max_pages: int = 10):
        if not url:
            return {
                "agent": "CaptureAgent",
                "status": "error",
                "message": "La URL es obligatoria.",
                "total_interfaces": 0,
                "total_captures": 0,
            }

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        try:
            result = take_screenshots(url=url, auth=auth, max_pages=max_pages)
            return {
                "agent": "CaptureAgent",
                **result,
            }
        except Exception as e:
            return {
                "agent": "CaptureAgent",
                "status": "error",
                "message": str(e),
                "total_interfaces": 0,
                "total_captures": 0,
            }