#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
seed.py
-------
Project support module (Task 0): database setup + seeding helpers.

This file exposes the EXACT prototypes required by the checker and your mains:

    def connect_db()                -> connects to the MySQL server (no DB selected)
    def create_database(connection) -> creates database ALX_prodev if missing
    def connect_to_prodev()         -> connects to the ALX_prodev database
    def create_table(connection)    -> creates table user_data if missing
    def insert_data(connection, data) -> inserts a dict row OR loads rows from a CSV path

Design notes
- Zero-argument functions (connect_db/connect_to_prodev) read credentials from
  environment variables so they work with your `0-main.py` as-is:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
- Table schema matches the spec:
    user_id CHAR(36) PRIMARY KEY (UUID v4), name/email NOT NULL, age DECIMAL NOT NULL.
- We add UNIQUE(email) so rerunning the seed won't duplicate rows.
- INSERT uses an idempotent "ON DUPLICATE KEY UPDATE user_id=user_id" no-op.
"""

import os
import csv
import uuid
from decimal import Decimal, InvalidOperation
import mysql.connector

DB_NAME = "ALX_prodev"


# -----------------------------
# Internal helper: config
# -----------------------------
def _cfg():
    """Read DB connection params from environment with safe defaults."""
    return (
        os.getenv("DB_HOST", "localhost"),
        int(os.getenv("DB_PORT", "3306")),
        os.getenv("DB_USER", "root"),
        os.getenv("DB_PASSWORD", ""),
    )


# -----------------------------
# Required prototypes
# -----------------------------
def connect_db():
    """
    Connect to the MySQL server (no database selected).
    Return: mysql.connector connection object.
    """
    host, port, user, pwd = _cfg()
    return mysql.connector.connect(host=host, port=port, user=user, password=pwd)


def create_database(connection):
    """
    Create the ALX_prodev database if it doesn't exist.
    Idempotent: safe to call repeatedly.
    """
    cur = connection.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.close()
    connection.commit()


def connect_to_prodev():
    """
    Connect to the ALX_prodev database (zero-arg per spec).
    Reads credentials from environment variables.
    """
    host, port, user, pwd = _cfg()
    return mysql.connector.connect(host=host, port=port, user=user, password=pwd, database=DB_NAME)


def create_table(connection):
    """
    Create the user_data table if it doesn't already exist.
    Prints "Table user_data created successfully" (as your sample output shows).
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) NOT NULL,
        name    VARCHAR(255) NOT NULL,
        email   VARCHAR(255) NOT NULL,
        age     DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (user_id),
        UNIQUE KEY email_unique (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cur = connection.cursor()
    cur.execute(ddl)
    cur.close()
    connection.commit()
    print("Table user_data created successfully")


# -----------------------------
# Internal helper: insert one
# -----------------------------
def _insert_one(connection, row):
    """
    Insert a single row into user_data.
    - Generates UUID4 if user_id not provided.
    - Validates age is numeric (Decimal).
    - Ignores duplicate email (unique constraint) using a no-op update.
    """
    uid = row.get("user_id") or str(uuid.uuid4())
    name = row.get("name")
    email = row.get("email")
    raw_age = row.get("age")

    if not (name and email and raw_age is not None):
        raise ValueError("Row must include 'name', 'email', and 'age'.")

    try:
        age = Decimal(str(raw_age))
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid age value: {raw_age!r}")

    sql = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE user_id = user_id
    """
    cur = connection.cursor()
    cur.execute(sql, (uid, name, email, age))
    connection.commit()
    cur.close()


def insert_data(connection, data):
    """
    Insert data in the database if it does not exist.

    Accepts:
      - dict: single user row, e.g. {"name": "...", "email": "...", "age": 42}
      - str : CSV file path with headers name,email,age[,user_id]

    For CSV files, rows are streamed and inserted one-by-one.
    """
    if isinstance(data, dict):
        _insert_one(connection, data)
        return

    if isinstance(data, str):
        with open(data, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _insert_one(connection, row)
        return

    raise TypeError("data must be a dict row or a CSV file path (string)")
