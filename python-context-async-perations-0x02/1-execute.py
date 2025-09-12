#!/usr/bin/env python3
"""
Task 1: Reusable Query Context Manager.
"""

import sqlite3
import os


class ExecuteQuery:
    """Context manager that executes a given query with parameters."""

    def __init__(self, db_path: str, query: str, params=None):
        self.db_path = db_path
        self.query = query
        self.params = params or ()
        self.conn = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False


if __name__ == "__main__":
    db_path = os.getenv("DB_PATH", "users.db")
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    with ExecuteQuery(db_path, query, params) as results:
        for row in results:
            print(dict(row))
