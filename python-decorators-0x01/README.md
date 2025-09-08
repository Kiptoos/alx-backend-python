# python-decorators-0x01

Implements a sequence of decorators for database operations in SQLite:
- `0-log_queries.py`: logs SQL statements.
- `1-with_db_connection.py`: opens/closes DB connections automatically.
- `2-transactional.py`: wraps operations in a transaction (commit/rollback).
- `3-retry_on_failure.py`: retries on transient failures with backoff.
- `4-cache_query.py`: caches results of SELECT queries by SQL string.

Assumes a SQLite DB file named `users.db` containing a `users` table.
