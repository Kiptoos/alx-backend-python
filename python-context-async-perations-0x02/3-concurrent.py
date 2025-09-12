#!/usr/bin/env python3
"""
Task 2: Concurrent Asynchronous Database Queries using aiosqlite.
"""

import os
import asyncio
import aiosqlite


async def async_fetch_users(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def async_fetch_older_users(db_path: str, age: int = 40):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE age > ?", (age,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def fetch_concurrently(db_path: str):
    all_users, older_users = await asyncio.gather(
        async_fetch_users(db_path),
        async_fetch_older_users(db_path, age=40)
    )
    print("All users:")
    for r in all_users:
        print(r)
    print("\nUsers older than 40:")
    for r in older_users:
        print(r)


if __name__ == "__main__":
    db_path = os.getenv("DB_PATH", "users.db")
    asyncio.run(fetch_concurrently(db_path))
