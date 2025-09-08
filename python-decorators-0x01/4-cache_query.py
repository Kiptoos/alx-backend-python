import sqlite3
import functools

query_cache = {}

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

def cache_query(func):
    """Cache results based on the SQL query string passed as 'query' (kwarg or positional)."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract the SQL string from kwargs or positional args
        if "query" in kwargs:
            key = kwargs["query"]
        else:
            # Expecting signature (conn, query, *rest)
            if len(args) < 1 or not isinstance(args[0], str):
                # If we cannot determine the query, fall back to calling without cache
                return func(conn, *args, **kwargs)
            key = args[0]

        if key in query_cache:
            return query_cache[key]
        result = func(conn, *args, **kwargs)
        # Shallow copy is fine for list of tuples result; store as-is
        query_cache[key] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)
    # Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
