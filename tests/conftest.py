import pytest
import requests

from config.settings import URL


@pytest.fixture(scope="session")
def yandex_disk_api():
    """Базовый клиент для Yandex Disk API"""

    class YandexDiskClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def get(self, token=None):
            headers = {}
            if token:
                headers["Authorization"] = f"OAuth {token}"
            return requests.get(self.base_url, headers=headers)

    return YandexDiskClient(base_url=URL)
