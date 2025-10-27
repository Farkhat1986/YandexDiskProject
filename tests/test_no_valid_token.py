from http import HTTPStatus

import allure

from connection.models import ErrorResponse


@allure.title("Отказ в доступе при отсутствии OAuth-токена")
@allure.description(
    "Проверяет, что:\n"
    "- Сервер возвращает статус 401 Unauthorized при запросе без токена\n"
    "- Тело ответа содержит корректную структуру ошибки:\n"
    "  * поле 'error' присутствует и не пустое\n"
    "  * поле 'description' присутствует\n"
    "  * поле 'message' присутствует"
)
def test_no_token_authorization(yandex_disk_api):
    with allure.step("Отправить GET-запрос к Yandex Disk API без токена авторизации"):
        response = yandex_disk_api.get()

    with allure.step("Проверить, что статус ответа — 401 Unauthorized"):
        assert (
            response.status_code == HTTPStatus.UNAUTHORIZED
        ), f"Ожидался статус 401, получен: {response.status_code}"

    with allure.step("Валидировать структуру ошибки в ответе"):
        error_response = ErrorResponse.model_validate(response.json())
        assert error_response.error, "Поле 'error' отсутствует или пустое"
        assert error_response.description, "Поле 'description' отсутствует или пустое"
        assert error_response.message, "Поле 'message' отсутствует или пустое"
