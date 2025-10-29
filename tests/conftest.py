from typing import Generator

import allure
import pytest

from api.disk_client import YandexDiskClient
from config.settings import settings
from utils.helpers import (
    generate_file_content,
    generate_file_name,
    generate_folder_name,
)


@pytest.fixture(scope="session")
def yandex_disk_api():
    """Базовый клиент для Yandex Disk API"""
    client = YandexDiskClient(base_url=settings.BASE_URL)
    yield client
    client.close()


@pytest.fixture(scope="session")
@allure.title("Валидный OAuth-токен")
def valid_token():
    """Валидный токен для тестов"""
    return settings.VALID_TOKEN


@pytest.fixture
def unique_folder_name():
    """Генерация уникального имени папки"""
    return generate_folder_name()


@pytest.fixture
def test_file_name():
    """Имя тестового файла"""
    return generate_file_name()


@pytest.fixture
def test_file_content():
    """Содержимое тестового файла"""
    return generate_file_content()


@pytest.fixture
@allure.title("Созданная тестовая папка")
def created_folder(
    yandex_disk_api: YandexDiskClient, valid_token: str, unique_folder_name: str
) -> Generator[str, None, None]:
    """Фикстура для создания временной папки"""
    with allure.step(f"Создать тестовую папку: {unique_folder_name}"):
        response = yandex_disk_api.create_folder(valid_token, unique_folder_name)
        assert response.status_code == 201, f"Не удалось создать папку: {response.text}"

    yield unique_folder_name

    with allure.step(f"Очистка: удалить папку {unique_folder_name}"):
        try:
            yandex_disk_api.delete_folder(
                valid_token, unique_folder_name, permanently=True
            )
        except Exception:
            pass


@pytest.fixture
@allure.title("Удаленная тестовая папка")
def deleted_folder(
    yandex_disk_api: YandexDiskClient, valid_token: str, unique_folder_name: str
) -> Generator[str, None, None]:
    """Фикстура для папки, которая будет удалена в корзину"""
    with allure.step(f"Создать и удалить тестовую папку: {unique_folder_name}"):
        response = yandex_disk_api.create_folder(valid_token, unique_folder_name)
        assert response.status_code == 201, f"Не удалось создать папку: {response.text}"

        response = yandex_disk_api.delete_folder(valid_token, unique_folder_name)
        assert response.status_code in [
            204,
            202,
        ], f"Не удалось удалить папку: {response.text}"

    yield unique_folder_name

    with allure.step(f"Очистка: окончательное удаление папки {unique_folder_name}"):
        try:
            yandex_disk_api.delete_folder(
                valid_token, unique_folder_name, permanently=True
            )
        except Exception:
            try:
                yandex_disk_api.delete_folder(valid_token, unique_folder_name)
            except Exception:
                pass
