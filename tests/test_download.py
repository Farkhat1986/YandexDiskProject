import uuid
from http import HTTPStatus

import allure

from connection.models import DownloadLinkResponse, UploadUrlResponse


@allure.title("Тест-кейс №4: Скачивание текстового файла")
@allure.description(
    "Проверяет сценарий:\n"
    "- Создание временной папки на Яндекс.Диске\n"
    "- Загрузку текстового файла в эту папку\n"
    "- Получение публичной ссылки для скачивания\n"
    "- Успешное скачивание файла по ссылке\n"
    "- Сравнение содержимого скачанного файла с исходным"
)
def test_download_file(yandex_disk_api, valid_token, test_file_content):
    folder_name = f"sdet_data_{uuid.uuid4().hex[:6]}"
    file_name = "data.txt"
    expected_content = test_file_content

    def cleanup():
        yandex_disk_api.delete_folder(valid_token, folder_name, permanently=True)

    try:
        with allure.step("Создать временную папку на Яндекс.Диске"):
            create_resp = yandex_disk_api.create_folder(valid_token, folder_name)
            assert (
                create_resp.status_code == HTTPStatus.CREATED
            ), f"Ожидался статус 201 при создании папки, получен: {create_resp.status_code}"

        with allure.step("Получить URL для загрузки и загрузить файл в папку"):
            upload_url_resp = yandex_disk_api.get_upload_url(
                valid_token, f"{folder_name}/{file_name}"
            )
            assert (
                upload_url_resp.status_code == HTTPStatus.OK
            ), f"Не удалось получить URL для загрузки: {upload_url_resp.status_code}"

            upload_data = UploadUrlResponse.model_validate(upload_url_resp.json())
            upload_result = yandex_disk_api.upload_file(
                upload_data.href, expected_content
            )
            assert (
                upload_result.status_code == HTTPStatus.CREATED
            ), f"Ожидался статус 201 при загрузке, получен: {upload_result.status_code}"

        with allure.step("Получить ссылку для скачивания файла"):
            download_url_resp = yandex_disk_api.get_download_url(
                valid_token, f"{folder_name}/{file_name}"
            )
            assert (
                download_url_resp.status_code == HTTPStatus.OK
            ), f"Не удалось получить ссылку на скачивание: {download_url_resp.status_code}"

            download_data = DownloadLinkResponse.model_validate(
                download_url_resp.json()
            )
            assert str(download_data.href).startswith(
                "https://"
            ), f"Ссылка для скачивания не является HTTPS: {download_data.href}"

        with allure.step("Скачать файл по полученной ссылке и сравнить содержимое"):
            actual_content = yandex_disk_api.download_public_file(
                str(download_data.href)
            ).strip()
            assert (
                actual_content == expected_content.strip()
            ), "Содержимое скачанного файла не совпадает с ожидаемым"

    finally:
        with allure.step("Очистка: удалить временную папку безвозвратно"):
            cleanup()
