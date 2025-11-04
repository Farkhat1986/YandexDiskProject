import random
import uuid
from http import HTTPStatus
from typing import Generator

import allure
import pytest
import requests

from api.disk_client import YandexDiskClient
from config.settings import settings
from connection.models import UploadUrlResponse


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
                pass
            else:
                try:
                    yandex_disk_api.delete_folder(valid_token, unique_folder_name)
                except Exception:
                    pass


@pytest.fixture
def temporary_folders(yandex_disk_api, valid_token, unique_folder_name):
    """Создаёт временные входную и выходную папки на Диске и удаляет их после теста"""
    input_folder = f"test_input_{unique_folder_name}"
    output_folder = f"test_output_{unique_folder_name}"

    with allure.step(f"Создать папки: {input_folder}, {output_folder}"):
        resp_in = yandex_disk_api.create_folder(valid_token, input_folder)
        resp_out = yandex_disk_api.create_folder(valid_token, output_folder)
        assert (
            resp_in.status_code == HTTPStatus.CREATED
        ), f"Не удалось создать {input_folder}"
        assert (
            resp_out.status_code == HTTPStatus.CREATED
        ), f"Не удалось создать {output_folder}"

    yield input_folder, output_folder

    with allure.step("Очистка: удалить временные папки безвозвратно"):
        yandex_disk_api.delete_folder(valid_token, input_folder, permanently=True)
        yandex_disk_api.delete_folder(valid_token, output_folder, permanently=True)


@pytest.fixture
def temp_folder(yandex_disk_api, valid_token, unique_folder_name):
    """Фикстура для создания временной папки"""
    folder_name = f"sdet_data_{unique_folder_name}"

    create_resp = yandex_disk_api.create_folder(valid_token, folder_name)
    assert create_resp.status_code == HTTPStatus.CREATED

    yield folder_name

    yandex_disk_api.delete_folder(valid_token, folder_name, permanently=True)


@pytest.fixture
def uploaded_file(yandex_disk_api, valid_token, temp_folder, test_file_content):
    """Фикстура для загруженного файла"""
    file_name = "data.txt"
    upload_url_resp = yandex_disk_api.get_upload_url(
        valid_token, f"{temp_folder}/{file_name}"
    )
    assert upload_url_resp.status_code == HTTPStatus.OK

    upload_data = UploadUrlResponse.model_validate(upload_url_resp.json())
    upload_result = yandex_disk_api.upload_file(upload_data.href, test_file_content)
    assert upload_result.status_code == HTTPStatus.CREATED

    return f"{temp_folder}/{file_name}"
