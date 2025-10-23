from http import HTTPStatus

import allure

from config.settings import VALID_TOKEN
from connection.models import DiskInfoResponse


@allure.title("Успешная авторизация с валидным OAuth-токеном")
@allure.description(
    "Проверяет, что:\n"
    "- Сервер возвращает статус 200 OK при корректной авторизации\n"
    "- Тело ответа содержит полную информацию о диске пользователя:\n"
    "  * поле 'user.login' присутствует и не пустое\n"
    "  * поле 'user.display_name' присутствует и не пустое"
)
def test_valid_token_authorization(yandex_disk_api):
    with allure.step("Отправить GET-запрос к Yandex Disk API с валидным токеном"):
        response = yandex_disk_api.get(token=VALID_TOKEN)

    with allure.step("Проверить, что статус ответа — 200 OK"):
        assert (
            response.status_code == HTTPStatus.OK
        ), f"Ожидался статус 200, получен: {response.status_code}"

    with allure.step(
        "Валидировать структуру ответа и проверить наличие данных пользователя"
    ):
        disk_info = DiskInfoResponse.model_validate(response.json())
        assert disk_info.user.login, "Поле 'user.login' отсутствует или пустое"
        assert (
            disk_info.user.display_name
        ), "Поле 'user.display_name' отсутствует или пустое"
