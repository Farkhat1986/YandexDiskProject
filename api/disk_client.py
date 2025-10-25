from api.base import BaseAPIClient
from config.settings import settings


class YandexDiskClient(BaseAPIClient):
    def __init__(self, base_url: str):
        super().__init__(base_url=settings.BASE_URL, api_prefix="/v1/disk")

    def get_disk_info(self, token: str):
        """Получить метаинформацию о диске"""
        return self.get(path="/", token=token)

    def get_files_list(self, token: str, path: str = "/"):
        """Получить список файлов в папке"""
        return self.get(path="/resources", token=token, params={"path": path})
