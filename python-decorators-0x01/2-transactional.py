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

def transactional(func):
    """Wrap DB operations in a transaction: commit on success, rollback on error, re-raise."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    # No explicit return needed


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print("Email updated.")
