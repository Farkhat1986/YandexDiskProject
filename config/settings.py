import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_URL: str
    VALID_TOKEN: str | None = None

    def __init__(self):
        base_url = os.getenv("BASE_URL")
        valid_token = os.getenv("VALID_TOKEN")

        if not base_url:
            raise ValueError("Ошибка требуется BASE_URL")

        self.BASE_URL = base_url.rstrip("/")
        self.VALID_TOKEN = valid_token

    def validate_token_required(self):
        """Валидация для случаев, когда токен обязателен"""
        if not self.VALID_TOKEN:
            raise ValueError("Ошибка: для этого функционала требуется VALID_TOKEN")


settings = Settings()
