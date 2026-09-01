# feed.py
# Point 11 — Generator-based feed paginator  (paginate_posts)
# Point 13 — Performance: @cache_feed(ttl=30) decorator


# ---------------------------------------------------------------------------
# Point 13 imports
# ---------------------------------------------------------------------------

# functools.wraps  — copies the original function's name and docstring onto
#                    the wrapper so it still looks like the real function.
# time             — used to read the current clock and calculate expiry.
from functools import wraps
import time


# ---------------------------------------------------------------------------
# Point 13: @cache_feed(ttl=30)
# ---------------------------------------------------------------------------
#
# What is a decorator?
# A decorator is a function that wraps another function to add behaviour
# without changing the original function's code.
#
# @cache_feed(ttl=30) means:
#   - the first time the decorated function is called, run it normally
#     and store (cache) the result along with the current timestamp.
#   - on every later call, check the timestamp:
#       * if fewer than `ttl` seconds have passed  →  return the cached result
#         immediately (no re-running the function).
#       * if `ttl` seconds have passed             →  the cache has expired,
#         re-run the function and refresh the cache.
#
# Why is this useful?
# Building a feed can be expensive (database queries, sorting, filtering).
# If two requests arrive within 30 seconds, the second one gets the cached
# result instantly instead of repeating all that work.
#
# How it is built (three layers):
#
#   cache_feed(ttl)          ← outer function, receives ttl=30
#     └─ decorator(func)     ← middle function, receives the function being decorated
#           └─ wrapper(...)  ← inner function, runs every time the decorated function is called


def cache_feed(ttl=30):
    """
    A decorator factory that caches a function's return value for `ttl` seconds.

    Usage:
        @cache_feed(ttl=30)
        def get_feed(posts):
            ...

    Args:
        ttl (int): Time-to-live in seconds. Default is 30.

    Returns:
        A decorator that wraps the target function with caching logic.
    """

    # `decorator` is the actual decorator. It receives the function to wrap.
    def decorator(func):

        # These two variables live inside `decorator` and are shared by every
        # call to `wrapper`. They persist between calls (this is a "closure").
        cached_result    = None   # stores the last return value
        cached_timestamp = None   # stores when that value was saved (seconds since epoch)

        # `wraps(func)` copies func's __name__ and __doc__ onto wrapper,
        # so the wrapper looks identical to the original from the outside.
        @wraps(func)
        def wrapper(*args, **kwargs):
            # `nonlocal` lets us reassign the outer variables from inside wrapper.
            nonlocal cached_result, cached_timestamp

            current_time = time.time()   # seconds since Unix epoch (a float)

            # Check whether we have a valid cached result:
            #   cached_timestamp is not None  →  we have run the function before
            #   current_time - cached_timestamp < ttl  →  cache has not expired yet
            cache_is_valid = (
                cached_timestamp is not None
                and (current_time - cached_timestamp) < ttl
            )

            if cache_is_valid:
                # Cache hit: return the stored result immediately.
                age = current_time - cached_timestamp
                print(f"  [cache] HIT  — returning cached result (age: {age:.1f}s / ttl: {ttl}s)")
                return cached_result

            # Cache miss (either first call or cache has expired):
            # call the real function, save its result, record the timestamp.
            print(f"  [cache] MISS — calling {func.__name__}() and caching result")
            cached_result    = func(*args, **kwargs)
            cached_timestamp = time.time()
            return cached_result

        return wrapper   # replace the original function with the wrapper

    return decorator   # return the decorator so @cache_feed(ttl=30) works


# ---------------------------------------------------------------------------
# Example of a cached feed builder (uses the decorator above)
# ---------------------------------------------------------------------------

@cache_feed(ttl=30)
def get_feed(posts):
    """
    Returns the full list of posts.

    In a real app this would query a database, sort by recency, apply filters,
    etc.  Here it simply returns the list as-is to keep things easy to follow.

    Because it is decorated with @cache_feed(ttl=30), repeated calls within
    30 seconds return the cached result without re-running this function.

    Args:
        posts (tuple): The posts to serve. Must be a tuple (not a list) because
                       lists are not hashable — if you ever upgrade to
                       functools.lru_cache this will matter. For now it just
                       reminds us that arguments should be immutable.

    Returns:
        list: The posts, converted to a list for easy use.
    """
    # Simulate a small amount of work (in a real app: database call, sorting…)
    return list(posts)


# ---------------------------------------------------------------------------
# Point 11: generator-based feed paginator (unchanged from before)
# ---------------------------------------------------------------------------
#
# A generator is a special kind of function that uses the `yield` keyword.
# Instead of computing all results and returning them at once, a generator
# pauses after each `yield` and only continues when the caller asks for
# the next value. This means we never hold the whole result set in memory.


def paginate_posts(posts, batch_size=10):
    """
    A generator that yields posts in batches.

    How it works, step by step:
    1. `start` begins at 0 (the first post).
    2. The while loop runs as long as `start` is still within the list.
    3. `posts[start : start + batch_size]` slices out the next batch.
    4. `yield` sends that batch to the caller and PAUSES here.
    5. When the caller asks for the next batch, execution resumes
       and `start` moves forward by `batch_size`.
    6. When `start` reaches the end of the list, the loop ends
       and the generator is done.

    Args:
        posts (list): The full list of post dictionaries.
        batch_size (int): How many posts to include in each batch. Default is 10.

    Yields:
        list: A slice of `posts` containing up to `batch_size` items.
    """
    # Start at the beginning of the list
    start = 0

    # Keep going while there are still posts left to yield
    while start < len(posts):
        # Slice out the next batch of posts
        batch = posts[start : start + batch_size]

        # Yield this batch to whoever is iterating over the generator.
        # Execution pauses here until the next batch is requested.
        yield batch

        # Move the starting index forward to the next batch
        start += batch_size
