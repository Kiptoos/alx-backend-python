#!/usr/bin/env python3
"""
Task 0: Custom class-based context manager for DB connection.
"""

import sqlite3
import os


class DatabaseConnection:
    """Custom context manager for handling SQLite DB connections."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False  # don’t suppress exceptions


if __name__ == "__main__":
    db_path = os.getenv("DB_PATH", "users.db")
    with DatabaseConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(dict(row))
