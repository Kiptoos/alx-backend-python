#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
0-stream_users.py
-----------------
Task 1: Implement a generator that streams rows one-by-one from MySQL.

Constraints from spec:
- Must use 'yield'
- The function should have NO MORE THAN ONE loop

We open a server-side (unbuffered) cursor to avoid loading all rows at once.
"""
import seed

def stream_users():
    """
    Generator yielding user rows as dictionaries, one at a time.
    Exactly ONE loop is used (the `for row in cur` below).
    """
    conn = seed.connect_to_prodev()
    # dictionary=True returns dict rows; buffered=False avoids loading everything into memory
    cur = conn.cursor(dictionary=True, buffered=False)
    try:
        cur.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")
        for row in cur:  # <-- the single loop required by the spec
            # Normalize age for nicer printing (keep as-is if not numeric)
            try:
                row["age"] = int(row["age"])
            except Exception:
                pass
            yield row
    finally:
        cur.close()
        conn.close()
