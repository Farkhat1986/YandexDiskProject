import requests

from config import settings


class BaseAPIClient:

    api_prefix: str = ""

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or settings.BASE_URL).rstrip("/")
        self.api_prefix = self.__class__.api_prefix.lstrip("/")
        self.session = requests.Session()

    def _build_url(self, path: str = "") -> str:
        path = path.lstrip("/")
        full_path = f"{self.api_prefix}/{path}" if self.api_prefix else path
        return f"{self.base_url}/{full_path}".rstrip("/")

    def _get_headers(self, token: str = None) -> dict:
        headers = {}
        if token:
            headers["Authorization"] = f"OAuth {token}"
        return headers

    def get(self, path: str = "", token: str = None, params=None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        return self.session.get(url, headers=headers, params=params)

    def close(self):
        self.session.close()
