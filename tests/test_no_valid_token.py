from http import HTTPStatus

from connection.models import ErrorResponse


def test_no_token_authorization(yandex_disk_api):
    """
    Тест: запрос к Yandex Disk API без токена авторизации

    Проверяет, что:
    - Сервер возвращает статус 401 Unauthorized
    - Тело ответа содержит корректную структуру ошибки:
        * поле 'error' присутствует и не пустое
        * поле 'description' присутствует
        * поле 'message' присутствует
    """
    response = yandex_disk_api.get()

    assert (
        response.status_code == HTTPStatus.UNAUTHORIZED
    ), f"Expected 401, got {response.status_code}"

    disk_info = ErrorResponse(**response.json())
    assert disk_info.error
    assert disk_info.description
    assert disk_info.message
