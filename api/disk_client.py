from api.base import BaseAPIClient


class YandexDiskClient(BaseAPIClient):
    def __init__(self, base_url: str):
        super().__init__(base_url=base_url, api_prefix="/v1/disk")

    def get_disk_info(self, token: str):
        """Получить метаинформацию о диске"""
        return self.get(path="/", token=token)

    def get_files_list(self, token: str, path: str = "/"):
        """Получить список файлов в папке"""
        return self.get(path=f"/resources?path={path}", token=token)
