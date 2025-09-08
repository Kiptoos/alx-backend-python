#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
4-stream_ages.py
----------------
Task 4: Memory-efficient aggregation with generators.
Goal: compute average age WITHOUT SQL AVG and WITHOUT loading the whole dataset.

Constraints:
- Exactly TWO loops in this script total:
  * Loop #1 inside the age generator
  * Loop #2 when consuming the generator to compute the average
"""
from decimal import Decimal
import seed

def stream_user_ages():
    """
    Generator yielding ages one-by-one as Decimal (stable numeric type).
    Loop #1: iterate the DB cursor row by row.
    """
    conn = seed.connect_to_prodev()
    cur = conn.cursor(buffered=False)
    try:
        cur.execute("SELECT age FROM user_data")
        for (age,) in cur:  # Loop #1
            yield Decimal(str(age))
    finally:
        cur.close()
        conn.close()

def average_age():
    """
    Consume the generator and print the average age.
    Loop #2: iterate ages; no SQL AVG used.
    """
    total = Decimal(0)
    count = 0
    for age in stream_user_ages():  # Loop #2
        total += age
        count += 1
    avg = (total / count) if count else Decimal(0)
    print(f"Average age of users: {avg:.2f}")
    return avg

if __name__ == "__main__":
    average_age()
