import time
from functools import wraps


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка базы данных: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f"Вы уверены, что хотите выполнить действие "
                f'"{action_name}"? (y/n): '
            )

            if answer.lower() != "y":
                raise ValueError("Действие отменено.")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        elapsed_time = time.monotonic() - start_time

        print(
            f"Функция {func.__name__} выполнилась "
            f"за {elapsed_time:.3f} секунд"
        )

        return result

    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    cache_result.cache = cache

    return cache_result
