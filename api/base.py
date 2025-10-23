import requests


class BaseAPIClient:
    def __init__(self, base_url: str, api_prefix: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix.lstrip("/")

    def _build_url(self, path: str = "") -> str:
        path = path.lstrip("/")
        full_path = f"{self.api_prefix}/{path}" if self.api_prefix else path
        return f"{self.base_url}/{full_path}".rstrip("/")

    def _get_headers(self, token: str = None) -> dict:
        headers = {}
        if token:
            headers["Authorization"] = f"OAuth {token}"
        return headers

    def get(self, path: str = "", token: str = None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        return requests.get(url, headers=headers)
