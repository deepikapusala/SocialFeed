
from functools import wraps
import time

def cache_feed(ttl=30):
    def decorator(func):
        cached_result    = None   # stores the last return value
        cached_timestamp = None   # stores when that value was saved (seconds since epoch)

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal cached_result, cached_timestamp

            current_time = time.time()   # seconds since Unix epoch (a float)

            cache_is_valid = (
                cached_timestamp is not None
                and (current_time - cached_timestamp) < ttl
            )

            if cache_is_valid:
                age = current_time - cached_timestamp
                print(f"  [cache] HIT  — returning cached result (age: {age:.1f}s / ttl: {ttl}s)")
                return cached_result

            print(f"  [cache] MISS — calling {func.__name__}() and caching result")
            cached_result    = func(*args, **kwargs)
            cached_timestamp = time.time()
            return cached_result

        return wrapper   # replace the original function with the wrapper
    return decorator   # return the decorator so @cache_feed(ttl=30) works

@cache_feed(ttl=30)
def get_feed(posts):
    return list(posts)


def paginate_posts(posts, batch_size=10):

    start = 0

    while start < len(posts):
        batch = posts[start : start + batch_size]
        yield batch
        start += batch_size
