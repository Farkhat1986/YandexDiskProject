import random
import string
import uuid


def random_text(prefix: str = "Тест", length: int = 8) -> str:
    """Генерирует случайный текст с префиксом"""
    chars = string.ascii_letters + string.digits
    suffix = "".join(random.choice(chars) for _ in range(length))
    return f"{prefix} {suffix}"


def generate_folder_name(prefix: str = "test_folder") -> str:
    """Генерирует уникальное имя папки для тестов"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def generate_file_name(prefix: str = "test_file", extension: str = "txt") -> str:
    """Генерирует уникальное имя файла для тестов"""
    return f"{prefix}_{uuid.uuid4().hex[:6]}.{extension}"


def generate_file_content(min_length: int = 10, max_length: int = 100) -> str:
    """Генерирует случайное содержимое для текстового файла"""
    words = ["тест", "данные", "файл", "содержимое", "пример", "текст", "информация"]
    content_length = random.randint(min_length, max_length)

    content = []
    while len(" ".join(content)) < content_length:
        word = random.choice(words)
        content.append(word)

    return " ".join(content)[:content_length]
