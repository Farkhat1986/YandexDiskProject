from http import HTTPStatus

import allure

from connection.models import DownloadLinkResponse, UploadUrlResponse
from utils.wait import POLL_INTERVALL, TIME_OUT, wait_for_condition


@allure.title("Скачивание текстового файла")
@allure.description(
    "Проверяет сценарий:\n"
    "- Создание временной папки на Яндекс.Диске\n"
    "- Загрузку текстового файла в эту папку\n"
    "- Ожидание появления файла\n"
    "- Получение публичной ссылки для скачивания\n"
    "- Успешное скачивание файла по ссылке\n"
    "- Сравнение содержимого скачанного файла с исходным"
)
def test_download_file(yandex_disk_api, valid_token, test_file_content, temp_folder):
    folder_name = temp_folder
    file_name = "data.txt"
    expected_content = test_file_content
    file_path = f"{folder_name}/{file_name}"

    with allure.step("Получить URL для загрузки и загрузить файл в папку"):
        upload_url_resp = yandex_disk_api.get_upload_url(valid_token, file_path)
        assert (
            upload_url_resp.status_code == HTTPStatus.OK
        ), f"Ожидался статус {HTTPStatus.OK}, получен: {upload_url_resp.status_code}"

        upload_data = UploadUrlResponse.model_validate(upload_url_resp.json())
        upload_result = yandex_disk_api.upload_file(upload_data.href, expected_content)
        assert (
            upload_result.status_code == HTTPStatus.CREATED
        ), f"Ожидался статус {HTTPStatus.CREATED}, получен: {upload_result.status_code}"

    def resource_exists():
        resp = yandex_disk_api.get_resource_info(valid_token, file_path)
        return resp.status_code == HTTPStatus.OK

    with allure.step("Дождаться появления файла на диске"):
        wait_for_condition(
            condition=resource_exists,
            timeout=TIME_OUT,
            poll_interval=POLL_INTERVALL,
            error_message=f"Файл {file_path} не появился",
        )

    with allure.step("Получить ссылку для скачивания файла"):
        download_url_resp = yandex_disk_api.get_download_url(valid_token, file_path)
        assert (
            download_url_resp.status_code == HTTPStatus.OK
        ), f"Ожидался статус {HTTPStatus.OK}, получен: {download_url_resp.status_code}"

        download_data = DownloadLinkResponse.model_validate(download_url_resp.json())
        assert str(download_data.href).startswith(
            "https://"
        ), f"Ссылка для скачивания не является валидным HTTPS-URL. Получено: {download_data.href}"

    with allure.step("Скачать файл по полученной ссылке и сравнить содержимое"):
        actual_content = yandex_disk_api.download_public_file(
            str(download_data.href)
        ).strip()
        assert actual_content == expected_content.strip(), "Содержимое не совпадает"
