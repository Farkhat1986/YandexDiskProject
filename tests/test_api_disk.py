from http import HTTPStatus

import allure

from connection.models import (
    CreateFolderResponse,
    ResourceInfo,
    TrashResourceInfo,
    UploadUrlResponse,
)


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
        assert delete_response.text == "", "Тело ответа должно быть пустым"

    with allure.step("Шаг 2: Отправить GET запрос для проверки удаления папки"):
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
    import time

    with allure.step("Предусловие: создать тестовую папку"):
        create_response = yandex_disk_api.create_folder(valid_token, unique_folder_name)
        assert (
            create_response.status_code == HTTPStatus.CREATED
        ), f"Не удалось создать папку: {create_response.status_code}"

    with allure.step("Предусловие: удалить папку в корзину"):
        delete_response = yandex_disk_api.delete_folder(valid_token, unique_folder_name)
        assert delete_response.status_code in [
            HTTPStatus.NO_CONTENT,
            HTTPStatus.ACCEPTED,
        ], f"Не удалось удалить папку в корзину: {delete_response.status_code}"

    with allure.step("Дать время для обработки операции удаления"):
        time.sleep(3)

    with allure.step("Получить информацию о папке в корзине"):
        trash_response = yandex_disk_api.get_trash_contents(valid_token)
        assert (
            trash_response.status_code == HTTPStatus.OK
        ), f"Не удалось получить информацию о корзине: {trash_response.status_code}"

    with allure.step("Найти папку в корзине по имени"):
        trash_data = trash_response.json()
        embedded = trash_data.get("_embedded", {})
        items = embedded.get("items", [])

        folder_in_trash = None
        for item in items:
            origin_path = item.get("origin_path", "")
            name_in_trash = item.get("name", "")

            if item.get("type") == "dir" and (
                name_in_trash == unique_folder_name
                or origin_path.endswith(f"/{unique_folder_name}")
            ):
                folder_in_trash = item
                break

        assert folder_in_trash is not None, (
            f"Папка {unique_folder_name} не найдена в корзине. "
            f"Доступные элементы: {[item.get('name') for item in items if item.get('type') == 'dir']}"
        )

    with allure.step("Валидировать информацию о папке в корзине"):
        trash_info = TrashResourceInfo.model_validate(folder_in_trash)
        assert trash_info.resource_id is not None, "Resource ID должен присутствовать"
        assert trash_info.type == "dir", "Тип должен быть 'dir'"
        assert trash_info.name == unique_folder_name, "Имя папки должно совпадать"

    with allure.step("Отправить PUT запрос для восстановления папки"):
        restore_response = yandex_disk_api.restore_from_trash(
            valid_token, folder_in_trash["path"], unique_folder_name
        )

    with allure.step("Проверить, что статус ответа — 201 Created"):
        assert (
            restore_response.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус 201, получен: {restore_response.status_code}"

    with allure.step("Валидировать структуру ответа восстановления"):
        restore_data = CreateFolderResponse.model_validate(restore_response.json())
        assert restore_data.method == "GET", "Метод должен быть 'GET'"
        assert not restore_data.templated, "Templated должен быть false"
        assert unique_folder_name in str(
            restore_data.href
        ), "HREF должен содержать имя папки"

    with allure.step("Дать время для обработки операции восстановления"):
        time.sleep(2)

    with allure.step("Отправить GET запрос для проверки восстановления"):
        get_response = yandex_disk_api.get_resource_info(
            valid_token, unique_folder_name
        )

    with allure.step("Проверить, что статус ответа — 200 OK"):
        assert (
            get_response.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200, получен: {get_response.status_code}"

    with allure.step("Валидировать информацию о восстановленной папке"):
        folder_info = ResourceInfo.model_validate(get_response.json())
        assert folder_info.type == "dir", "Тип должен быть 'dir'"
        assert folder_info.name == unique_folder_name, "Имя папки должно совпадать"

    with allure.step("Проверить, что папка удалилась из корзины"):
        trash_response_after = yandex_disk_api.get_trash_contents(valid_token)
        assert (
            trash_response_after.status_code == HTTPStatus.OK
        ), "Не удалось получить информацию о корзине после восстановления"

        trash_data_after = trash_response_after.json()
        embedded_after = trash_data_after.get("_embedded", {})
        items_after = embedded_after.get("items", [])

        folder_still_in_trash = None
        for item in items_after:
            if item.get("type") == "dir" and item.get("name") == unique_folder_name:
                folder_still_in_trash = item
                break

        assert (
            folder_still_in_trash is None
        ), f"Папка {unique_folder_name} все еще находится в корзине после восстановления"


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
        assert upload_response.text == "", "Тело ответа должно быть пустым"

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
