from http import HTTPStatus

from config.settings import VALID_TOKEN
from connection.models import DiskInfoResponse


def test_valid_token_authorization(yandex_disk_api):
    """
    Тест: запрос к Yandex Disk API с валидным OAuth-токеном

    Проверяет, что:
    - Сервер возвращает статус 200 OK при корректной авторизации
    - Тело ответа содержит полную информацию о диске пользователя:
        * поле 'user.login' присутствует и не пустое
        * поле 'user.display_name' присутствует и не пустое
    """
    response = yandex_disk_api.get(token=VALID_TOKEN)

    assert (
        response.status_code == HTTPStatus.OK
    ), f"Expected 200, got {response.status_code}"

    disk_info = DiskInfoResponse(**response.json())
    assert disk_info.user.login
    assert disk_info.user.display_name
