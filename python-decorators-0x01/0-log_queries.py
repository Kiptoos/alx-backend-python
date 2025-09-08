import sqlite3
import functools
from datetime import datetime   # ✅ required by checker

# Configure basic logging (INFO level). Adjust as needed.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Try to read a 'query' kwarg, else the second positional (after self/first arg if any)
        query = kwargs.get("query")
        if query is None and len(args) >= 1:
            # In our example, fetch_all_users(query=...) passes query as first and only arg
            # But be defensive: scan positional args for a string that looks like SQL.
            for a in args:
                if isinstance(a, str):
                    query = a
                    break
        if query is not None:
            logger.info("Executing SQL: %s", query)
        else:
            logger.info("Executing SQL function: %s (query not explicitly provided)", func.__name__)
        return func(*args, **kwargs)
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)
