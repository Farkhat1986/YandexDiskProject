import time
from typing import Callable

def wait_for_condition(
    condition: Callable[[], bool],
    timeout: int = 10,
    poll_interval: float = 0.5,
    error_message: str = "Условие не выполнилось в течение таймаута"
) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(poll_interval)
    raise TimeoutError(error_message)