import pytest

from api.disk_client import YandexDiskClient
from config.settings import BASE_URL


@pytest.fixture(scope="session")
def yandex_disk_api():
    """Базовый клиент для Yandex Disk API"""
    return YandexDiskClient(base_url=BASE_URL)
