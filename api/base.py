import requests

from config import settings


class BaseAPIClient:
    api_prefix: str = ""

    def __init__(self, base_url: str = None, timeout: float = 30.0):
        """
        Базовый API клиент

        Args:
            base_url: Базовый URL API
            timeout: Таймаут для запросов в секундах (по умолчанию 30 секунд)
        """
        self.base_url = (base_url or settings.BASE_URL).rstrip("/")
        self.api_prefix = self.__class__.api_prefix.lstrip("/")
        self.timeout = timeout
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

    def get(self, path: str = "", token: str = None, params=None, timeout: float = None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        request_timeout = timeout if timeout is not None else self.timeout
        return self.session.get(url, headers=headers, params=params, timeout=request_timeout)

    def put(self, path: str = "", token: str = None, params=None, json=None, timeout: float = None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        request_timeout = timeout if timeout is not None else self.timeout
        return self.session.put(url, headers=headers, params=params, json=json, timeout=request_timeout)

    def delete(self, path: str = "", token: str = None, params=None, timeout: float = None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        request_timeout = timeout if timeout is not None else self.timeout
        return self.session.delete(url, headers=headers, params=params, timeout=request_timeout)

    def post(self, path: str = "", token: str = None, params=None, json=None, timeout: float = None):
        url = self._build_url(path)
        headers = self._get_headers(token)
        request_timeout = timeout if timeout is not None else self.timeout
        return self.session.post(url, headers=headers, params=params, json=json, timeout=request_timeout)

    def set_timeout(self, timeout: float):
        """Установить таймаут по умолчанию"""
        self.timeout = timeout

    def close(self):
        self.session.close()