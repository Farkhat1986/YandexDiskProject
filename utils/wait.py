import time
from typing import Callable

TIME_OUT = 10
POLL_INTERVALL = 0.5


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: int = TIME_OUT,
    poll_interval: float = POLL_INTERVALL,
    error_message: str = "Условие не выполнилось в течение таймаута",
) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(poll_interval)
    raise TimeoutError(error_message)
