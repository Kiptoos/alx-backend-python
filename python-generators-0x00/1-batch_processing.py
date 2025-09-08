#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
1-batch_processing.py
---------------------
Task 2: Batch processing of large data using generators.

Requirements:
- Implement stream_users_in_batches(batch_size) that yields batches of rows.
- Implement batch_processing(batch_size) that processes each batch to filter users with age > 25.
- Use NO MORE THAN 3 loops across the whole file.
  * Loop #1 in stream_users_in_batches (while fetchmany)
  * Loop #2 & #3 in batch_processing (for batch, for row in batch)

Both functions use 'yield' / generator semantics.
"""
import seed

def stream_users_in_batches(batch_size):
    """
    Yield lists of user rows in batches of size 'batch_size'.
    Loop #1: while True, fetching with fetchmany to control memory usage.
    """
    conn = seed.connect_to_prodev()
    cur = conn.cursor(dictionary=True, buffered=False)
    try:
        cur.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")
        while True:  # Loop #1
            rows = cur.fetchmany(batch_size)
            if not rows:
                return  # StopIteration
            yield rows
    finally:
        cur.close()
        conn.close()

def batch_processing(batch_size=50):
    """
    Process each batch and print users whose age > 25.
    Loop #2: iterate over batches
    Loop #3: iterate rows within a batch
    """
    for batch in stream_users_in_batches(batch_size):   # Loop #2
        for user in batch:                              # Loop #3
            # Ensure we compare numerically
            age = int(user["age"])
            if age > 25:
                print(user)
