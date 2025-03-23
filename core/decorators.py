import threading
import functools


def run_is_thread(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        thread = threading.Thread(
            target=lambda: func(self, *args, **kwargs)
        )
        thread.start()

    return wrapper