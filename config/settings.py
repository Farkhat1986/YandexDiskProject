import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL").rstrip("/")

VALID_TOKEN = os.getenv("VALID_TOKEN")
