#!/usr/bin/env python3
"""
Task 2: Concurrent Asynchronous Database Queries using aiosqlite.
"""

import os
import asyncio
import aiosqlite

async def async_fetch_users(db_path: str):
    """Fetch all users asynchronously."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def async_fetch_older_users(db_path: str):
    """Fetch users older than 40 asynchronously."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def fetch_concurrently(db_path: str):
    """Run both queries concurrently and print results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(db_path),
        async_fetch_older_users(db_path)
    )

    print("All users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    db_path = os.getenv("DB_PATH", "users.db")  # Default path fallback
    asyncio.run(fetch_concurrently(db_path))
