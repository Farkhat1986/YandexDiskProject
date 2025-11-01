import uuid
from http import HTTPStatus

import allure

from connection.models import CopyResourceResponse, ErrorResponse, UploadUrlResponse


@allure.title("Загрузка и копирование файла")
@allure.description(
    "Проверяет сценарий:\n"
    "- Создание входной и выходной папок\n"
    "- Загрузку текстового файла во входную папку\n"
    "- Успешное копирование файла из входной папки в выходную\n"
    "- Обработку ошибки при повторной попытке копирования (ожидается HTTP 409 Conflict)"
)
def test_upload_and_copy_file(yandex_disk_api, valid_token, test_file_content):
    input_folder = f"input_data_{uuid.uuid4().hex[:6]}"
    output_folder = f"output_data_{uuid.uuid4().hex[:6]}"
    file_name = "data.txt"
    file_content = test_file_content

    def cleanup():
        yandex_disk_api.delete_folder(valid_token, input_folder, permanently=True)
        yandex_disk_api.delete_folder(valid_token, output_folder, permanently=True)

    try:
        with allure.step("Создать входную и выходную папки на Яндекс.Диске"):
            resp_in = yandex_disk_api.create_folder(valid_token, input_folder)
            resp_out = yandex_disk_api.create_folder(valid_token, output_folder)
            assert resp_in.status_code == HTTPStatus.CREATED
            assert resp_out.status_code == HTTPStatus.CREATED

        with allure.step("Получить URL для загрузки и загрузить файл во входную папку"):
            upload_resp = yandex_disk_api.get_upload_url(
                valid_token, f"{input_folder}/{file_name}"
            )
            assert upload_resp.status_code == HTTPStatus.OK

            upload_data = UploadUrlResponse.model_validate(upload_resp.json())
            upload_result = yandex_disk_api.upload_file(upload_data.href, file_content)
            assert (
                upload_result.status_code == HTTPStatus.CREATED
            ), f"Ожидался статус 201, получен: {upload_result.status_code}"

        with allure.step("Скопировать файл из входной папки в выходную"):
            copy_resp = yandex_disk_api.copy_resource(
                valid_token,
                from_path=f"{input_folder}/{file_name}",
                to_path=f"{output_folder}/{file_name}",
            )
            assert copy_resp.status_code == HTTPStatus.CREATED

            copy_data = CopyResourceResponse.model_validate(copy_resp.json())
            assert str(copy_data.href).startswith("https://")
            assert copy_data.method == "GET"
            assert copy_data.templated is False

        with allure.step("Повторно скопировать тот же файл → ожидается конфликт (409)"):
            conflict_resp = yandex_disk_api.copy_resource(
                valid_token,
                from_path=f"{input_folder}/{file_name}",
                to_path=f"{output_folder}/{file_name}",
            )
            assert conflict_resp.status_code == HTTPStatus.CONFLICT

            error_data = ErrorResponse.model_validate(conflict_resp.json())
            error_text = (error_data.message or error_data.description or "").lower()
            assert any(
                keyword in error_text for keyword in ["конфликт", "существует", "уже"]
            ), f"Сообщение об ошибке не содержит ожидаемых ключевых слов: {error_text}"

    finally:
        with allure.step("Очистка: удалить созданные папки безвозвратно"):
            cleanup()
