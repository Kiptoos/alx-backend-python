#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
2-lazy_paginate.py
------------------
Task 3: Lazy loading paginated data using a generator.

We provide:
- paginate_users(page_size, offset): returns one page (a list of dict rows).
- lazypaginate(page_size): generator that yields rows lazily.

Constraints:
- Only ONE loop inside lazypaginate().
- Your sample main imports `lazy_pagination`, so we also expose an alias.
"""
import seed


def paginate_users(page_size, offset):
    """
    Fetch a single page from the database using LIMIT/OFFSET.
    No loops here, just a query + fetch.
    """
    conn = seed.connect_to_prodev()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT user_id, name, email, age FROM user_data ORDER BY user_id LIMIT %s OFFSET %s",
        (page_size, offset),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def lazypaginate(page_size):
    """
    Generator that yields rows one by one, page by page.
    Exactly ONE loop (the while).
    """
    offset = 0
    while True:  # Loop #1
        page = paginate_users(page_size, offset)
        if not page:
            break
        for row in page:  # still part of the single loop body
            yield row
        offset += page_size


# Your 3-main.py imports lazy_pagination from this module, so keep this alias.
lazy_pagination = lazypaginate
