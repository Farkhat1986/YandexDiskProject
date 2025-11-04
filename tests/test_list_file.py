import json
from http import HTTPStatus
from pathlib import PurePosixPath

import allure
from jsonschema import ValidationError, validate

from connection.models import FilesListResponse

FILES_LIST_SCHEMA = FilesListResponse.model_json_schema(mode="serialization")


@allure.title("Получение списка файлов и валидация структуры ответа через JSON Schema")
@allure.description(
    "Проверяет сценарий:\n"
    "- Создание временной папки и загрузка файла\n"
    "- Получение списка файлов в папке\n"
    "- Валидация HTTP 200\n"
    "- Валидация структуры ответа через JSON Schema (из Pydantic)\n"
    "- Дополнительно: проверка через Pydantic модель"
)
def test_list_files_structure(
    yandex_disk_api, valid_token, uploaded_file, uploaded_folder_path
):

    with allure.step(f"Запрос списка файлов в папке: {uploaded_folder_path}"):
        response = yandex_disk_api.get_files_list(
            valid_token, path=uploaded_folder_path
        )
        assert (
            response.status_code == HTTPStatus.OK
        ), f"Ожидался 200, получен {response.status_code}. Тело: {response.text}"

    json_response = response.json()

    assert (
        json_response.get("type") == "dir"
    ), f"Ожидалась папка, получен тип: {json_response.get('type')}"
    assert (
        "_embedded" in json_response
    ), "Ответ не содержит _embedded — возможно, запрошен файл"

    with allure.step("Проверка соответствия JSON Schema"):
        try:
            validate(instance=json_response, schema=FILES_LIST_SCHEMA)
        except ValidationError as e:
            allure.attach(
                json.dumps(json_response, indent=2, ensure_ascii=False),
                "Ответ API",
                allure.attachment_type.JSON,
            )
            allure.attach(
                json.dumps(FILES_LIST_SCHEMA, indent=2),
                "Сгенерированная схема",
                allure.attachment_type.JSON,
            )
            raise AssertionError(f"JSON Schema validation failed: {e.message}") from e

    with allure.step("Проверка через Pydantic модель"):
        files_list = FilesListResponse.model_validate(json_response)

        expected_file_name = PurePosixPath(uploaded_file).name
        found = any(
            item.name == expected_file_name for item in files_list.embedded.items
        )
        assert found, f"Файл '{expected_file_name}' не найден в списке"
