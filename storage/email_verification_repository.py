import sqlite3

from config.settings import DATABASE_PATH


def create_email_verification_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_email_verification_email_created
            ON email_verification_codes(email, created_at)
            """
        )


def invalidate_old_codes(email: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE email_verification_codes
            SET used=1
            WHERE email=? AND used=0
            """,
            (email,),
        )


def create_verification_code(
    email: str,
    code_hash: str,
    expires_at: str,
    created_at: str,
) -> int:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO email_verification_codes
                (email, code_hash, expires_at, used, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (email, code_hash, expires_at, created_at),
        )
        return int(cursor.lastrowid)


def get_latest_valid_code(email: str) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, email, code_hash, expires_at, used, created_at
            FROM email_verification_codes
            WHERE email=?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (email,),
        ).fetchone()

    return dict(row) if row else None


def mark_code_used(code_id: int) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE email_verification_codes
            SET used=1
            WHERE id=?
            """,
            (code_id,),
        )
