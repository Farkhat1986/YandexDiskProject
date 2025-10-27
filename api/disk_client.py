from api.base import BaseAPIClient


class YandexDiskClient(BaseAPIClient):
    api_prefix = "/v1/disk"

    def __init__(self, base_url: str = None):
        super().__init__(base_url=base_url)

    def get_disk_info(self, token: str):
        """Получить метаинформацию о диске"""
        return self.get(path="/", token=token)

    def get_files_list(self, token: str, path: str = "/"):
        """Получить список файлов в папке"""
        return self.get(path="/resources", token=token, params={"path": path})
