import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_URL: str
    VALID_TOKEN: str

    def __init__(self):
        base_url = os.getenv("BASE_URL")
        valid_token = os.getenv("VALID_TOKEN")

        if not base_url:
            raise ValueError("Ошибка требуется BASE_URL")
        if not valid_token:
            raise ValueError("Ошибка требуется VALID_TOKEN")

        self.BASE_URL = base_url.rstrip("/")
        self.VALID_TOKEN = valid_token


settings = Settings()
