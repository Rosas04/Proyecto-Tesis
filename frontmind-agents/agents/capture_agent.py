from services.screenshot_service import take_screenshots


class CaptureAgent:
    def run(self, url: str):
        result = take_screenshots(url)
        result["url"] = url
        result["agent"] = "CaptureAgent"
        result["status"] = "completed"
        return result