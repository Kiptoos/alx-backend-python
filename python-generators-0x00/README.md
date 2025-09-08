# Python Generators — 0x00

This project demonstrates efficient, memory-friendly data access patterns in Python using **generators** with a MySQL backend.

## Environment

Export DB credentials so the zero‑argument helpers work with your existing mains:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD='yourpassword'
```

## Files

- **seed.py** — DB setup + seed helpers
  - `connect_db()` — connects to MySQL server (no DB selected).
  - `create_database(connection)` — creates `ALX_prodev` if not present.
  - `connect_to_prodev()` — connects to `ALX_prodev`.
  - `create_table(connection)` — creates `user_data` table if missing.
  - `insert_data(connection, data)` — insert single dict row OR load from CSV path.
- **0-stream_users.py** — `stream_users()` yields rows one-by-one (ONE loop).
- **1-batch_processing.py** — `stream_users_in_batches()` and `batch_processing()` (≤ 3 loops).
- **2-lazy_paginate.py** — `paginate_users()` + `lazy_paginate()` (ONE loop). Also exports `lazy_pagination` alias.
- **4-stream_ages.py** — `stream_user_ages()` + `average_age()` (exactly TWO loops, no SQL AVG).

## Typical flow

1) **Seed the DB** (via your `0-main.py` which calls these helpers):
```python
import seed
srv = seed.connect_db()
seed.create_database(srv)
srv.close()

conn = seed.connect_to_prodev()
seed.create_table(conn)
seed.insert_data(conn, "user_data.csv")  # CSV header: name,email,age[,user_id]
conn.close()
```

2) **Stream users (Task 1)** — your `1-main.py` with `islice` works out-of-the-box.

3) **Batch process (Task 2)** — print users with age > 25 in batches:
```bash
./2-main.py | head -n 20
```

4) **Lazy paginate (Task 3)** — your `3-main.py` that imports `lazy_pagination` is supported.

5) **Average age (Task 4)**:
```bash
python 4-stream_ages.py
# -> Average age of users: <value>
```

## Notes
- Cursors use `buffered=False` where streaming is needed to keep memory usage low.
- `email` is unique to prevent duplicate rows on repeated seeds.
- Ages are stored as DECIMAL and normalized when printing.
