from http import HTTPStatus

import allure

from connection.models import (
    CreateFolderResponse,
    ResourceInfo,
    UploadUrlResponse,
)
from utils.wait import wait_for_condition


@allure.title("Создание папки - успешное создание")
@allure.description(
    "Проверяет успешное создание новой папки на Яндекс Диске:\n"
    "- PUT запрос возвращает статус 201 Created\n"
    "- Ответ содержит корректные данные о созданной папке\n"
    "- GET запрос подтверждает существование папки с типом 'dir'"
)
def test_create_folder_success(yandex_disk_api, valid_token, unique_folder_name):
    with allure.step("Предусловие: убедиться, что папка не существует"):
        response = yandex_disk_api.get_resource_info(valid_token, unique_folder_name)
        assert (
            response.status_code == HTTPStatus.NOT_FOUND
        ), f"Папка {unique_folder_name} не должна существовать перед тестом"

    with allure.step("Отправить PUT запрос для создания папки"):
        create_response = yandex_disk_api.create_folder(valid_token, unique_folder_name)

    with allure.step("Проверить, что статус ответа — 201 Created"):
        assert (
            create_response.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус 201, получен: {create_response.status_code}"

    with allure.step("Валидировать структуру ответа создания папки"):
        create_data = CreateFolderResponse.model_validate(create_response.json())
        assert create_data.method == "GET", "Метод должен быть 'GET'"
        assert not create_data.templated, "Templated должен быть false"
        assert unique_folder_name in str(
            create_data.href
        ), "HREF должен содержать имя папки"

    with allure.step("Отправить GET запрос для проверки создания папки"):
        get_response = yandex_disk_api.get_resource_info(
            valid_token, unique_folder_name
        )

    with allure.step("Проверить, что статус ответа — 200 OK"):
        assert (
            get_response.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200, получен: {get_response.status_code}"

    with allure.step("Валидировать информацию о созданной папке"):
        folder_info = ResourceInfo.model_validate(get_response.json())
        assert folder_info.type == "dir", "Тип должен быть 'dir'"
        assert folder_info.name == unique_folder_name, "Имя папки должно совпадать"


@allure.title("Создание папки - попытка создания существующей папки")
@allure.description(
    "Проверяет обработку попытки создания уже существующей папки:\n"
    "- PUT запрос возвращает статус 409 Conflict"
)
def test_create_existing_folder(yandex_disk_api, valid_token, created_folder):
    with allure.step("Отправить PUT запрос для создания существующей папки"):
        response = yandex_disk_api.create_folder(valid_token, created_folder)

    with allure.step("Проверить, что статус ответа — 409 Conflict"):
        assert (
            response.status_code == HTTPStatus.CONFLICT
        ), f"Ожидался статус 409, получен: {response.status_code}"


@allure.title("Удаление папки - успешное удаление")
@allure.description(
    "Проверяет успешное удаление папки на Яндекс Диске:\n"
    "- DELETE запрос возвращает статус 204 No Content\n"
    "- GET запрос подтверждает отсутствие папки (404 Not Found)"
)
def test_delete_folder_success(yandex_disk_api, valid_token, created_folder):
    with allure.step("Предусловие: убедиться, что папка существует"):
        response = yandex_disk_api.get_resource_info(valid_token, created_folder)
        assert (
            response.status_code == HTTPStatus.OK
        ), f"Папка {created_folder} должна существовать перед удалением"

    with allure.step("Отправить DELETE запрос для удаления папки"):
        delete_response = yandex_disk_api.delete_folder(valid_token, created_folder)

    with allure.step("Проверить, что статус ответа — 204 No Content"):
        assert (
            delete_response.status_code == HTTPStatus.NO_CONTENT
        ), f"Ожидался статус 204, получен: {delete_response.status_code}"

    with allure.step("Проверить, что тело ответа пустое"):
        assert not delete_response.content, "Тело ответа должно быть пустым"

    with allure.step("Отправить GET запрос для проверки удаления папки"):
        get_response = yandex_disk_api.get_resource_info(valid_token, created_folder)

    with allure.step("Проверить, что статус ответа — 404 Not Found"):
        assert (
            get_response.status_code == HTTPStatus.NOT_FOUND
        ), f"Ожидался статус 404, получен: {get_response.status_code}"


@allure.title("Удаление папки - попытка удаления несуществующей папки")
@allure.description(
    "Проверяет обработку попытки удаления несуществующей папки:\n"
    "- DELETE запрос возвращает статус 404 Not Found"
)
def test_delete_nonexistent_folder(yandex_disk_api, valid_token, unique_folder_name):
    with allure.step("Отправить DELETE запрос для несуществующей папки"):
        response = yandex_disk_api.delete_folder(valid_token, unique_folder_name)

    with allure.step("Проверить, что статус ответа — 404 Not Found"):
        assert (
            response.status_code == HTTPStatus.NOT_FOUND
        ), f"Ожидался статус 404, получен: {response.status_code}"


@allure.title("Восстановление папки из корзины")
@allure.description(
    "Проверяет успешное восстановление папки из корзины Яндекс Диска:\n"
    "- PUT запрос возвращает статус 201 Created\n"
    "- GET запрос подтверждает восстановление папки"
)
def test_restore_folder_from_trash(yandex_disk_api, valid_token, unique_folder_name):
    with allure.step("Предусловие: создать тестовую папку"):
        create_response = yandex_disk_api.create_folder(valid_token, unique_folder_name)
        assert create_response.status_code == HTTPStatus.CREATED, \
            f"Не удалось создать папку: {create_response.status_code}"

    with allure.step("Предусловие: удалить папку в корзину"):
        delete_response = yandex_disk_api.delete_folder(valid_token, unique_folder_name)
        assert delete_response.status_code in [HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED], \
            f"Не удалось удалить папку в корзину: {delete_response.status_code}"

    def folder_in_trash():
        resp = yandex_disk_api.get_trash_contents(valid_token)
        if resp.status_code != HTTPStatus.OK:
            return False
        items = resp.json().get("_embedded", {}).get("items", [])
        return any(
            item.get("type") == "dir" and item.get("name") == unique_folder_name
            for item in items
        )

    with allure.step("Дождаться появления папки в корзине"):
        wait_for_condition(
            folder_in_trash,
            timeout=15,
            error_message=f"Папка {unique_folder_name} не появилась в корзине за 15 сек"
        )

    with allure.step("Получить информацию о папке в корзине"):
        trash_resp = yandex_disk_api.get_trash_contents(valid_token)
        trash_data = trash_resp.json()
        items = trash_data["_embedded"]["items"]
        folder_in_trash_item = next(
            (item for item in items if item.get("name") == unique_folder_name and item.get("type") == "dir"),
            None
        )
        assert folder_in_trash_item is not None, "Папка исчезла из корзины неожиданно"

    with allure.step("Восстановить папку из корзины"):
        restore_resp = yandex_disk_api.restore_from_trash(
            valid_token, folder_in_trash_item["path"]
        )
        assert restore_resp.status_code == HTTPStatus.CREATED, \
            f"Ожидался 201, получен: {restore_resp.status_code}"

    def folder_restored():
        resp = yandex_disk_api.get_resource_info(valid_token, unique_folder_name)
        return resp.status_code == HTTPStatus.OK

    with allure.step("Дождаться появления восстановленной папки в основном хранилище"):
        wait_for_condition(
            folder_restored,
            timeout=15,
            error_message=f"Папка {unique_folder_name} не восстановилась за 15 сек"
        )

    def folder_not_in_trash():
        resp = yandex_disk_api.get_trash_contents(valid_token)
        if resp.status_code != HTTPStatus.OK:
            return False
        items = resp.json().get("_embedded", {}).get("items", [])
        return not any(
            item.get("type") == "dir" and item.get("name") == unique_folder_name
            for item in items
        )

    with allure.step("Убедиться, что папка удалена из корзины"):
        wait_for_condition(
            folder_not_in_trash,
            timeout=10,
            error_message=f"Папка {unique_folder_name} всё ещё в корзине после восстановления"
        )


@allure.title("Создание текстового файла")
@allure.description(
    "Проверяет создание текстового файла на Яндекс Диске:\n"
    "- GET запрос возвращает URL для загрузки\n"
    "- PUT запрос загружает файл с статусом 201 Created\n"
    "- GET запрос подтверждает создание файла с типом 'file' и MIME-типом 'text/plain'"
)
def test_create_text_file_success(
    yandex_disk_api, valid_token, test_file_name, test_file_content
):
    with allure.step("Предусловие: удалить файл, если он существует"):
        response = yandex_disk_api.get_resource_info(valid_token, test_file_name)
        if response.status_code == HTTPStatus.OK:
            yandex_disk_api.delete_folder(valid_token, test_file_name, permanently=True)

    with allure.step("Получить URL для загрузки файла"):
        upload_url_response = yandex_disk_api.get_upload_url(
            valid_token, test_file_name
        )

    with allure.step("Проверить, что статус ответа — 200 OK"):
        assert (
            upload_url_response.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200, получен: {upload_url_response.status_code}"

    with allure.step("Валидировать структуру ответа с URL загрузки"):
        upload_data = UploadUrlResponse.model_validate(upload_url_response.json())
        assert upload_data.method == "PUT", "Метод должен быть 'PUT'"
        assert not upload_data.templated, "Templated должен быть false"
        assert (
            upload_data.operation_id is not None
        ), "Operation ID должен присутствовать"

    with allure.step("Загрузить текстовый файл по полученному URL"):
        upload_response = yandex_disk_api.upload_file(
            str(upload_data.href), test_file_content
        )

    with allure.step("Проверить, что статус ответа — 201 Created"):
        assert (
            upload_response.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус 201, получен: {upload_response.status_code}"

    with allure.step("Проверить, что тело ответа пустое"):
        assert not upload_response.content, "Тело ответа должно быть пустым"

    with allure.step("Проверить создание файла"):
        file_info_response = yandex_disk_api.get_resource_info(
            valid_token, test_file_name
        )

    with allure.step("Проверить, что статус ответа — 200 OK"):
        assert (
            file_info_response.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200, получен: {file_info_response.status_code}"

    with allure.step("Валидировать информацию о созданном файле"):
        file_info = ResourceInfo.model_validate(file_info_response.json())
        assert file_info.type == "file", "Тип должен быть 'file'"
        assert file_info.name == test_file_name, "Имя файла должно совпадать"
        assert file_info.mime_type == "text/plain", "MIME-тип должен быть 'text/plain'"