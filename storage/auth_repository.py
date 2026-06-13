import sqlite3

from config.settings import DATABASE_PATH


def create_users_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                account_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _add_column_if_missing(connection, "users", "email", "TEXT")
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
            ON users(email)
            WHERE email IS NOT NULL AND email != ''
            """
        )


def create_user(username: str, email: str, password_hash: str, account_type: str) -> int:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, password_hash, account_type)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, account_type),
        )
        return int(cursor.lastrowid)


def get_user_by_username(username: str) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, username, email, password_hash, account_type, created_at
            FROM users
            WHERE username=?
            LIMIT 1
            """,
            (username,),
        ).fetchone()

    return dict(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, username, email, password_hash, account_type, created_at
            FROM users
            WHERE email=?
            LIMIT 1
            """,
            (email,),
        ).fetchone()

    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, username, email, password_hash, account_type, created_at
            FROM users
            WHERE id=?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(row) if row else None


def get_user_by_login(login: str) -> dict | None:
    return get_user_by_email(login) if "@" in login else get_user_by_username(login)


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = [
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    ]
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
