from django.core.cache import cache

ATTEMPT_LIMIT = 5
WINDOW_SECONDS = 15 * 60


def incr_login_attempt(key: str) -> int:
    count = cache.get(key, 0)
    count += 1
    cache.set(key, count, timeout=WINDOW_SECONDS)
    return count


def reset_login_attempt(key: str):
    cache.delete(key)


def is_rate_limited(key: str) -> bool:
    return (cache.get(key, 0) or 0) >= ATTEMPT_LIMIT
