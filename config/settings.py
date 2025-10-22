import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_PREFIX = "/v1/disk"

URL = BASE_URL + API_PREFIX

VALID_TOKEN = os.getenv("VALID_TOKEN")
