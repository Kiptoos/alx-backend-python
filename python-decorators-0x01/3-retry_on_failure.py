import time
import sqlite3
import functools

def with_db_connection(func):
    """Open a sqlite3 connection to 'users.db', pass it as the first arg, and close it afterward."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """Retry a function up to `retries` times with `delay` seconds between attempts on any Exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        # Exceeded max retries: re-raise the last exception
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # Attempt to fetch users with automatic retry on failure
    users = fetch_users_with_retry()
    print(users)
