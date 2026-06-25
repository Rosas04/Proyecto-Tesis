from services.screenshot_service import take_screenshots


class CaptureAgent:
    def run(self, url: str, credentials = None):
        credentials_dict = credentials.dict() if credentials and hasattr(credentials, "dict") else credentials
        result = take_screenshots(url, credentials_dict)
        result["url"] = url
        result["agent"] = "CaptureAgent"
        result["status"] = "completed"
        return result