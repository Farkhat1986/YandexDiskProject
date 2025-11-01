import random
import uuid
from typing import Generator

import allure
import pytest
import requests

from api.disk_client_new import YandexDiskClient
from config.settings import settings


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
def unique_folder_name(prefix: str = "test_folder") -> str:
    """Генерирует уникальное имя папки для тестов"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_file_name(prefix: str = "test_file", extension: str = "txt") -> str:
    """Генерирует уникальное имя файла для тестов"""
    return f"{prefix}_{uuid.uuid4().hex[:6]}.{extension}"


@pytest.fixture
def test_file_content(min_length: int = 10, max_length: int = 100) -> str:
    """Генерирует случайное содержимое для текстового файла"""
    words = ["тест", "данные", "файл", "содержимое", "пример", "текст", "информация"]
    content_length = random.randint(min_length, max_length)

    content = []
    while len(" ".join(content)) < content_length:
        word = random.choice(words)
        content.append(word)

    return " ".join(content)[:content_length]


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
        except requests.exceptions.RequestException as e:
            # Ловим только ошибки сетевого уровня или API
            print(f"Не удалось удалить папку {unique_folder_name}: {e}")
        except Exception as e:
            # Другие ожидаемые исключения
            if "не найдено" in str(e).lower() or "not found" in str(e).lower():
                # Папка уже удалена - это нормально
                pass
            else:
                print(f"Неожиданная ошибка при удалении {unique_folder_name}: {e}")


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
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети при окончательном удалении {unique_folder_name}: {e}")
        except Exception as e:
            error_msg = str(e).lower()
            if any(msg in error_msg for msg in ["не найдено", "not found", "404"]):
                # Ресурс уже удален - это нормально
                pass
            else:
                # Пробуем удалить без permanently=True
                try:
                    yandex_disk_api.delete_folder(valid_token, unique_folder_name)
                except Exception:
                    # Игнорируем ошибки при cleanup
                    pass