import pytest

from api.disk_client import YandexDiskClient
from config.settings import settings


@pytest.fixture(scope="session")
def yandex_disk_api():
    """Базовый клиент для Yandex Disk API"""
    client = YandexDiskClient(base_url=settings.BASE_URL)
    yield client
    client.close()
