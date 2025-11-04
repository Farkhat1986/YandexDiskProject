from http import HTTPStatus

import allure

from connection.models import (
    CopyResourceRequest,
    CopyResourceResponse,
    ErrorResponse,
    UploadUrlResponse,
)


@allure.title("Загрузка и копирование файла")
@allure.description(
    "Проверяет сценарий:\n"
    "- Создание входной и выходной папок\n"
    "- Загрузку текстового файла во входную папку\n"
    "- Успешное копирование файла из входной папки в выходную\n"
    "- Обработку ошибки при повторной попытке копирования (ожидается HTTP 409 Conflict)"
)
def test_upload_and_copy_file(
    yandex_disk_api, valid_token, test_file_content, temporary_folders
):
    input_folder, output_folder = temporary_folders
    file_name = "data.txt"
    file_content = test_file_content

    with allure.step("Получить URL для загрузки файла"):
        upload_resp = yandex_disk_api.get_upload_url(
            valid_token, f"{input_folder}/{file_name}"
        )
        assert (
            upload_resp.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200 OK, получен: {upload_resp.status_code}"

        upload_data = UploadUrlResponse.model_validate(upload_resp.json())

    with allure.step("Загрузить файл по полученному URL"):
        upload_result = yandex_disk_api.upload_file(upload_data.href, file_content)
        assert (
            upload_result.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус 201 CREATED, получен: {upload_result.status_code}"

    with allure.step("Инициировать копирование файла из входной папки в выходную"):
        copy_request = CopyResourceRequest(
            from_path=f"{input_folder}/{file_name}",
            to_path=f"{output_folder}/{file_name}",
        )
        copy_resp = yandex_disk_api.copy_resource(
            valid_token, copy_request.from_path, copy_request.to_path
        )
        assert (
            copy_resp.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус 201 CREATED, получен: {copy_resp.status_code}"

    with allure.step("Проверить структуру ответа после успешного копирования"):
        copy_data = CopyResourceResponse.model_validate(copy_resp.json())
        assert str(copy_data.href).startswith(
            "https://"
        ), f"Ссылка не начинается с 'https://' Получено: {copy_data.href}"
        assert copy_data.method == "GET", f"Неверный HTTP-метод: {copy_data.method}"
        assert (
            copy_data.templated is False
        ), f"Поле 'templated' должно быть False, получено: {copy_data.templated}"

    with allure.step("Повторно инициировать копирование (ожидается ошибка 409)"):
        conflict_resp = yandex_disk_api.copy_resource(
            valid_token, copy_request.from_path, copy_request.to_path
        )
        assert (
            conflict_resp.status_code == HTTPStatus.CONFLICT
        ), f"Ожидался статус 409 CONFLICT, получен: {conflict_resp.status_code}"

    with allure.step("Проверить сообщение об ошибке при конфликте"):
        error_data = ErrorResponse.model_validate(conflict_resp.json())
        error_text = (error_data.message or error_data.description or "").lower()
        assert any(
            keyword in error_text for keyword in ["конфликт", "существует", "уже"]
        ), f"Сообщение об ошибке не содержит ожидаемых ключевых слов: {error_text}"
