import requests

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

    def create_folder(self, token: str, folder_name: str):
        """Создание папки"""
        return self.put(
            path="/resources", token=token, params={"path": f"app:/{folder_name}"}
        )

    def get_resource_info(self, token: str, path: str):
        """Получение информации о ресурсе"""
        return self.get(path="/resources", token=token, params={"path": f"app:/{path}"})

    def get_trash_contents(self, token: str):
        """Получить содержимое корзины"""
        return self.get(path="/trash/resources", token=token)

    def delete_folder(self, token: str, folder_name: str, permanently: bool = False):
        """Удаление папки"""
        params = {"path": f"app:/{folder_name}", "permanently": permanently}

        return self.delete(path="/resources", token=token, params=params)

    def get_trash_resource(self, token: str, resource_name: str):
        """Получить информацию о конкретном ресурсе в корзине"""
        params = {"path": f"app:/{resource_name}"}
        return self.get(path="/trash/resources", token=token, params=params)

    def restore_from_trash(self, token: str, trash_path: str, new_name: str = None):
        """Восстановить ресурс из корзины"""
        params = {"path": trash_path}
        if new_name:
            params["name"] = new_name

        return self.put(path="/trash/resources/restore", token=token, params=params)

    def get_upload_url(self, token: str, file_name: str):
        """Получение URL для загрузки файла"""
        return self.get(
            path="/resources/upload", token=token, params={"path": f"app:/{file_name}"}
        )

    def upload_file(self, upload_url: str, content: str):
        """Загрузка файла"""
        return requests.put(
            upload_url,
            data=content.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )

    def get_folder_info(self, token: str, folder_name: str):
        """Получить информацию о папке"""
        params = {"path": f"app:/{folder_name}"}
        return self.get(path="/resources", token=token, params=params)
